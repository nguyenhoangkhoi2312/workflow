# Project Progress & Context

## Overview
This project is an advanced educational application designed to generate personalized study tools—such as Flashcards, Quizzes, Smart Notes, and Learning Paths—from uploaded study materials. The UI/UX is styled heavily after an elegant, premium design aesthetic (referred to internally as the "Omilearn" aesthetic) utilizing a maroon/cream color palette (`#8A334B`, `#3B6B59`, `#F8EFEA`, `#1B2A4E`).

## Tech Stack
- **Frontend**: React, Vite, React Router (`HashRouter` for Electron), TailwindCSS (mostly vanilla inline CSS for core theming), Lucide-React.
- **Backend**: Python, FastAPI, Uvicorn, Google GenAI SDK (Gemini).
- **Packaging**: Electron (frontend wrapper) + PyInstaller (freezes the FastAPI backend). Outputs to a standalone macOS `.dmg`.

## UI/UX Architecture & Recent Overhauls
We recently completed a massive overhaul of the frontend architecture:
1. **Contextual Studio Sidebar**: 
   - Standalone pages for Flashcards, Quizzes, and Notes have been **deleted**. 
   - We shifted to a "Workspace" model. Users view their documents in the `DocumentViewer` (Project Workspace), and use the `StudioSidebar` (right side) to trigger the generation of study materials via elegant modals (`CreateExamModal`, `UploadModal`, `StudyDocProgressModal`).
2. **Interactive Exam Viewer (`/exam/:id`)**:
   - A stunning 3-column layout for taking exams.
   - **Left:** Interactive questions (Multiple Choice and Short Answer/Điền khuyết) with an "Instant Reveal" (Hiện đáp án & Giải thích luôn) toggle.
   - **Center:** Control panel (timer, submit button, animated trophy score).
   - **Right:** Source Document viewer, allowing users to reference the PDF/text while taking the exam.
3. **Settings & Dual Engine Mode**:
   - The `/settings` page features an "Engine Mode" toggle.
   - Users can choose between **Google Gemini AI** (requires an API key, connects to Google) and **Local Algorithm** (runs purely on local Python NLP heuristic scripts).

## Backend Architecture
- **Offline / Ephemeral Setup**: The Electron main process spawns the frozen Python FastAPI binary on an ephemeral port. The React frontend makes local HTTP requests to it.
- **AI Engine**: Uses the Google GenAI SDK to generate high-quality educational content when the user selects "AI Mode" and provides a valid `X-API-Key`.
- **Algorithm Engine (Current Focus)**: When the user selects "Local Algorithm", the backend relies on deterministic Natural Language Processing (NLP) heuristics to generate content without an LLM.

## Current Goal (For Claude)
We need to drastically improve the **Local Algorithm** engine in the Python backend. Currently, it relies on extremely basic heuristics (e.g., splitting sentences and randomly blanking words) injected into `main.py`.

The intended functionality is to build a robust, completely offline, non-LLM Python NLP pipeline using libraries like `spaCy`, `NLTK`, `TextRank`, `PyPDF2`, or `YAKE` to:
1. Extract Flashcards (keyword extraction, definition parsing).
2. Generate Quizzes (factual sentence extraction, Named Entity blanking, distractor generation via WordNet/embeddings).
3. Generate Smart Notes (extractive text summarization).
4. Extract structural Learning Paths (parsing PDF Table of Contents and headers).

**Context for Claude:** We are building this non-AI algorithm *first* so that the application has a flawless, free, offline baseline functionality before users are ever required to input an AI API key. Please research and propose the architectural algorithms and Python pipelines to achieve this!
