# ── Stage 1: Build the React frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy only package files first for better layer caching
COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install

# Copy the rest of the frontend source and build it
COPY frontend/ .
RUN npm run build
# Output is in /frontend/dist

# ── Stage 2: Python backend ─────────────────────────────────────────────────────
# Pinned to bullseye for stable package availability (libgl1-mesa-glx)
FROM python:3.10-slim-bullseye

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire project (backend, model, etc.)
COPY . .

# Copy the built frontend from Stage 1 into the expected location
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Change to the backend directory where requirements.txt lives
WORKDIR /app/backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production serving
RUN pip install gunicorn

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Run with the application factory pattern
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:create_app()", "--timeout", "120", "--preload"]
