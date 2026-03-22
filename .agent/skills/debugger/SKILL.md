---
name: Debugger
description: Common bugs and debugging steps for Deepfake Shield.
---

# Deepfake Shield Debugging Guide

- **Common bugs in this project:**
  - **CORS error:** check `flask-cors` is enabled in `app.py`
  - **Model not loading:** use absolute path for `.pth` file
  - **No faces detected:** video might not be mp4, convert first
  - **Frontend not connecting:** check API URL in `.env`
- **Debug steps:** reproduce → read full error → form 3 hypotheses → fix one thing at a time
