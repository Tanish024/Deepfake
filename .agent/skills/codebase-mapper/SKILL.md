---
name: Codebase Mapper
description: Architecture, structure, and constraints for the Deepfake Shield project.
---

# Deepfake Shield Codebase Map

- **Project:** Deepfake Shield
- **Stack:** React+Vite (frontend), Flask (backend), PyTorch+EfficientNet (model)
- **model/:** contains `preprocess.py`, `face_detector.py`, `pipeline.py`
- **backend/:** contains `app.py`, `routes/analyze.py`
- **frontend/src/:** contains `components/`, `api/client.js`
- **All API calls** go through `frontend/src/api/client.js` only
- **API response format:** `{ verdict, confidence, frames_analyzed, suspicious_frames }`
- **No inline styles** in React
- **No hardcoded URLs**, use `.env`
