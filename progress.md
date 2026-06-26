# Project Progress & Context

## Overview
This project is an advanced offline-first educational application designed to generate personalized study tools—such as Flashcards, Quizzes, Smart Notes, and Concept Maps—from uploaded study materials. The UI/UX is styled heavily after an elegant, premium design aesthetic (referred to internally as the "Omilearn" aesthetic) utilizing a maroon/cream/navy color palette.

## Tech Stack
- **Frontend**: React, Vite, React Router, TailwindCSS/Vanilla CSS, Lucide-React, React Flow (for Concept Maps), React Markdown (for Notes).
- **Backend**: Python, FastAPI, Uvicorn, SQLAlchemy (SQLite), NLP Libraries (spaCy, NLTK, pytextrank, networkx).
- **Packaging**: Electron (frontend wrapper) + PyInstaller (freezes the FastAPI backend). Outputs to a standalone macOS binary.

## UI/UX Architecture
1. **Document Library (Workspace)**: Users view their uploaded documents and summaries in the `DocumentViewer`.
2. **Contextual Studio Sidebar**: The `StudioSidebar` acts as the command center. Users trigger the generation of study materials (Concept Maps, Quizzes, Flashcards, Smart Notes) based on the active document via elegant modal overlays.
3. **Settings & Engine Mode**: Users can toggle between **Google Gemini AI** (API) and the **Offline Algorithm** (runs purely on local Python NLP heuristic scripts).

## Backend Architecture
- **Offline / Ephemeral Setup**: The Electron main process (`electron/main.cjs`) dynamically spawns the frozen Python FastAPI binary (`backend/dist/workflow-backend/workflow-backend`).
- **SQLite Database (`omilearn_local.db`)**: Handles state persistence for Flashcards, Documents, Quiz Scores, and SM-2 Spaced Repetition scheduling metrics.

### 1. Offline Natural Language Processing (NLP) Engine (Phases 1-5)
The backend relies on robust deterministic NLP heuristics to generate content without an LLM.
*   **Flashcards (`nlp/flashcards.py`):** Uses `spaCy` dependency parsing to extract definitional noun-chunks and Q&A pairs.
*   **Quizzes (`nlp/quizzes.py`):** Uses Named Entity Recognition (NER) to blank out subjects, querying NLTK's `WordNet` for distractors.
*   **Smart Notes (`nlp/notes.py`):** Uses `pytextrank` eigenvalue centrality to generate extractive summaries.
*   **Learning Paths (`nlp/pdf_toc.py`):** Uses `pdfplumber` to statistically infer font sizes, detecting chapter titles and exact page boundaries.

### 2. Persistence & Sync Architecture (Phases 6-9)
*   **Phase 6 (SQLite Persistence):** Implemented `SQLAlchemy` to store Flashcard generation and SM-2 review states in a local SQLite database (`omilearn_local.db`).
*   **Phase 7 (Native Cloud Sync):** Bypassed complex OAuth integrations. Users select their local Google Drive or OneDrive folder via an Electron native dialog (`CloudSyncModal`/Sidebar). The frontend writes this path to `~/.omilearn_config.json`. On startup, the FastAPI backend boots the SQLite database directly inside this cloud folder, allowing native desktop clients to sync the database implicitly!
*   **Phase 8 (Document Library):** Uploaded PDFs are parsed locally via `pdfplumber`. To keep the database size minimal (for lightning-fast cloud sync), we only save the extracted text to the `documents` SQLite table, not the binary PDF. The `DocumentViewer` dynamically fetches and displays the active document.
*   **Phase 9 (Automated Quizzes):** Integrated the NLP Quiz Generator with the UI (`TakeQuizModal.jsx`). Users can generate 5-question multiple-choice exams from their documents. The frontend automatically grades the exam and saves the score to the new `quiz_scores` SQLite table.

### 3. Final Modal Integration (Phases 10-12)
We recently completed the final integration of the NLP algorithms into the React UI components. All features are now 100% active.

*   **Phase 10 (Study Doc Analytics):** Built the `StudyDocProgressModal`. This analytics dashboard queries the SQLite database to display the user's active document metrics. It shows Quiz Accuracy (avg score from `quiz_scores`), Flashcard Retention (avg SM-2 easiness factor), and Document Difficulty (calculated via text token ratios).
*   **Phase 11 (Concept Maps & PNG Export):** Built `ConceptMapModal.jsx`. This queries the `/api/generate_map` endpoint (which uses TF-IDF and `networkx` to build semantic knowledge graphs). The UI renders the graph using `@xyflow/react` (React Flow). We also added an "Export PNG" button using `html-to-image` so users can download their knowledge graphs.
*   **Phase 12 (Smart Notes & MD Export):** Built `SmartNotesModal.jsx`. Queries the `/api/generate_notes` endpoint (using `pytextrank`). The resulting extractive summaries are beautifully rendered in the UI using `react-markdown`. We added an "Export MD" button to allow users to save their summaries locally.

### Recent Critical Fixes (Important Context for Claude)
- **PyInstaller SQLAlchemy Missing Module Bug:** The standalone frozen PyInstaller backend was crashing on boot with `ModuleNotFoundError: No module named 'sqlalchemy'`. We diagnosed that PyInstaller's build cache was stale (it remembered the dependency graph from before `sqlalchemy` was installed in the `venv`). **Fix applied:** We ran PyInstaller with the `--clean` flag (`pyinstaller backend.spec --noconfirm --clean`) which completely resolved the issue. The backend boots perfectly now.
- **React Frontend Crash Bug:** The `ConceptMapModal` was throwing `Uncaught ReferenceError: setError is not defined` when the backend timed out or failed. **Fix applied:** Re-added `const [error, setError] = useState(null);` to `ConceptMapModal.jsx`. 

## Current State & Next Steps (For Claude)
**Current Status:** The core offline application is completely functionally robust. The desktop frontend successfully talks to the frozen Python backend, processes PDFs natively, generates data via NLP, persists to an implicit cloud-sync SQLite DB, and allows local data exports.

**Potential Next Steps:**
1. **Testing & QA:** Thoroughly test the "Cloud Sync" (Google Drive/OneDrive folder selection) on different devices to ensure the `~/.omilearn_config.json` correctly updates the database target path.
2. **LLM Engine (Gemini):** Currently, the "Engine Mode" toggle in the UI visually works, but the backend is only wired to the deterministic NLP fallback. You could hook up the actual Google GenAI SDK calls in the `/api/...` endpoints when the Gemini mode is active.
3. **UI Polish:** Fine-tune animations, hover states, and spacing in the modals using TailwindCSS to elevate the "premium" feel.
4. **Build & Release Pipelines:** Test the macOS `.app` build using Electron Builder or Electron Forge to package the UI and backend together for actual distribution.
