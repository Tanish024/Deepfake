# Use an official Python runtime as a parent image
# Pinned to bullseye for stable package availability (libgl1-mesa-glx)
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project into the container
COPY . .

# Change to the backend directory where requirements.txt lives
WORKDIR /app/backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production serving
RUN pip install gunicorn

# Hugging Face Spaces specifically requires the app to listen on port 7860
EXPOSE 7860

# Run the backend server using Gunicorn, binding to 0.0.0.0:7860
# Use --preload so the factory is called before workers fork
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:create_app()", "--timeout", "120", "--preload"]
