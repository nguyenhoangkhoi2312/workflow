# Project Progress & Context

## Overview
This project is an advanced offline-first educational application designed to generate personalized study tools—such as Flashcards, Quizzes, Smart Notes, and Concept Maps—from uploaded study materials. The UI/UX is styled heavily after an elegant, premium design aesthetic (referred to internally as the "Omilearn" aesthetic) utilizing a maroon/cream color palette.

## Tech Stack
- **Frontend**: React, Vite, React Router, TailwindCSS/Vanilla CSS, Lucide-React.
- **Backend**: Python, FastAPI, Uvicorn, SQLAlchemy (SQLite), Google GenAI SDK (Gemini).
- **Packaging**: Electron (frontend wrapper) + PyInstaller (freezes the FastAPI backend). Outputs to a standalone macOS binary.

## UI/UX Architecture
1. **Document Library (Workspace)**: Users view their uploaded documents in the `DocumentViewer`.
2. **Contextual Studio Sidebar**: Users trigger the generation of study materials (Concept Maps, Quizzes, Flashcards) based on the active document via elegant modals.
3. **Settings & Dual Engine Mode**: Users can toggle between **Google Gemini AI** and the **Offline Algorithm** (runs purely on local Python NLP heuristic scripts).

## Backend Architecture
- **Offline / Ephemeral Setup**: The Electron main process spawns the frozen Python FastAPI binary.
- **SQLite Database (`omilearn_local.db`)**: Handles state persistence for Flashcards, Documents, and Quiz Scores.

### 1. Offline Natural Language Processing (NLP) Engine (Phases 1-5)
The backend relies on robust deterministic Natural Language Processing (NLP) heuristics to generate content without an LLM.
*   **Dependencies:** `spaCy`, `NLTK`, `pytextrank`, `pdfplumber`, `scikit-learn`, and `networkx`.
*   **Flashcards (`nlp/flashcards.py`):** Uses `spaCy` dependency parsing to extract definitional noun-chunks and Q&A pairs.
*   **Quizzes (`nlp/quizzes.py`):** Uses Named Entity Recognition (NER) to blank out subjects, querying NLTK's `WordNet` for distractors.
*   **Smart Notes (`nlp/notes.py`):** Uses `pytextrank` eigenvalue centrality to generate extractive summaries.
*   **Learning Paths (`nlp/pdf_toc.py`):** Uses `pdfplumber` to statistically infer font sizes, detecting chapter titles and exact page boundaries.
*   **Advanced Features:** SM-2 spaced repetition scheduler, `readability.py` (text difficulty scoring), and `concept_map.py` (TF-IDF semantic clustering).

### 2. Persistence & Sync Architecture (Phases 6-9)
We recently transitioned the application into a persistent, cloud-synced platform.

*   **Phase 6 (SQLite Persistence):** Implemented `SQLAlchemy` to store Flashcard generation and SM-2 review states in a local SQLite database (`omilearn_local.db`).
*   **Phase 7 (Native Cloud Sync):** Bypassed complex OAuth integrations. Users select their local Google Drive or OneDrive folder via an Electron native dialog (`CloudSyncModal`/Sidebar). The frontend writes this path to `~/.omilearn_config.json`. On startup, the FastAPI backend boots the SQLite database directly inside this cloud folder, allowing native desktop clients to sync the database implicitly!
*   **Phase 8 (Document Library):** Uploaded PDFs are parsed locally via `pdfplumber`. To keep the database size minimal (for lightning-fast cloud sync), we only save the extracted text to the `documents` SQLite table, not the binary PDF. The `DocumentViewer` dynamically fetches and displays the active document.
*   **Phase 9 (Automated Quizzes):** Integrated the NLP Quiz Generator with the UI (`TakeQuizModal.jsx`). Users can generate 5-question multiple-choice exams from their documents. The frontend automatically grades the exam and saves the score to the new `quiz_scores` SQLite table.

## Current Goal (For Claude / Next Agents)
The core offline pipelines (Documents, Flashcards, Quizzes, Cloud Sync) are fully operational.
Next potential objectives:
1. **Study Doc Progress UI (Phase 10):** Build out the `StudyDocProgressModal` to aggregate and display the user's reading difficulty (TF-IDF score), recent quiz scores, and SM-2 flashcard retention rates for the active document.
2. **Refining the UI:** Continue polishing the React interfaces for the newly generated modals.
