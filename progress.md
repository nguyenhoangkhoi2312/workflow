# Project Progress & Context

## Overview
This project is an AI-powered educational application inspired by Workflow. It provides users with personalized study tools like Flashcards, Quizzes, Smart Notes, and Learning Paths generated dynamically from their own uploaded study materials.

## Tech Stack
- **Frontend**: React, Vite, React Router (`HashRouter` for Electron compatibility), TailwindCSS, Lucide-React for icons.
- **Backend**: Python, FastAPI, Uvicorn, Google GenAI SDK (Gemini).
- **Packaging**: Electron (frontend wrapper) + PyInstaller (freezes the FastAPI backend into a standalone binary). The final output is a standalone macOS `.dmg`.

## Architecture
- **Offline / Standalone Environment**: The application runs entirely offline. The Electron main process spawns the frozen Python FastAPI binary on an ephemeral port, enabling the React frontend to make local HTTP requests to the backend.
- **Dynamic NLP & AI Engine**:
  - The backend accepts requests (e.g., `/api/flashcards`, `/api/quizzes`, `/api/suggestions`).
  - If a valid `X-API-Key` (Gemini API Key) is provided, it uses the Google GenAI SDK to generate high-quality educational content.
  - If no API Key is provided (or if the user is completely offline), the backend seamlessly falls back to a deterministic **Natural Language Processing (NLP)** algorithm to generate flashcards and quizzes using text summarization and keyword extraction heuristics.

## Recently Completed Features
1. **Local File Library & Uploads**:
   - Built a custom `storage.js` helper utilizing `localStorage`.
   - Users can now upload `.txt` and `.md` files via the `DocumentExplorer` page.
   - Files are securely stored locally and rendered via `DocumentViewer`.
2. **Dashboard AI Suggestion Engine**:
   - Added a `POST /api/suggestions` endpoint.
   - When the user opens the app, the frontend aggregates the text from all their uploaded documents and queries the backend.
   - The backend analyzes the corpus and recommends a tailored Learning Path, Quiz topic, and Flashcard topic.
3. **Settings & API Configuration**:
   - Built a `/settings` page to allow users to securely inject their Gemini API key into the app's `localStorage`.
   - Updated the `api.js` wrapper to attach this key as an `X-API-Key` header on every request.
4. **PyInstaller + Electron Compilation Fixes**:
   - Fixed `uvicorn` issues with PyInstaller freezing by checking `getattr(sys, 'frozen', False)`.
   - Integrated the backend build step `pyinstaller --name workflow-backend --noconfirm main.py` directly into the Node build scripts.

## Current Status
- The `.dmg` application has been successfully built and packaged for `mac-arm64`.
- All features (AI, NLP Fallbacks, File Uploads, Suggestion Engine, Settings) are functional.
- The user is currently testing the latest release binary.

## Next Steps
- Gather feedback from the user on the algorithmic/NLP fallback outputs.
- Consider adding local SQLite support instead of `localStorage` if the user's document corpus grows larger than the 5MB limit.
- Consider adding PDF parsing support to the Python backend (e.g., using `PyMuPDF` or `pdfplumber`).
