# Project: Workflow Codebase Audit & Refactoring

## Architecture
Workflow is a study tool designed for students, featuring a React + Vite + Tailwind/CSS frontend embedded inside Electron, and a FastAPI backend with SQLAlchemy + SQLite database.

- **Frontend**: Single Page Application using `react-router-dom` with HashRouter. Communicates with the backend at `http://127.0.0.1:8000/api`.
- **Backend**: FastAPI app (`backend/main.py`) using SQLite (`backend/workflow_local.db` or `local.db`). Implements offline-first NLP logic using python packages (`pyvi`, `nltk`, `pdfplumber`, etc.) and falls back from Gemini Agent calls to offline functions.
- **Data Flow**: Frontend components trigger interactive API calls to the backend. The backend persists data and serves files from the `uploads/` directory on disk.

## Milestones
| # | Name | Scope | Dependencies | Status | Conversation ID |
|---|------|-------|--------------|--------|-----------------|
| 1 | E2E Testing Suite | Develop E2E testing framework covering Tiers 1-4 for all user requirements. Publish `TEST_READY.md`. | None | DONE | 9b79a6e8-7267-4014-8486-1d21cfddb79c |
| 2 | Backend Stability & Schema Contexts | Migrate database schemas for `chat_messages`, `artifacts`, and `flashcards` to support both `project_id` and `document_id`. Fix URL ingestion path mismatch and implement offline NLP fallbacks for exam prep, study plan, and concept map definitions/formulas. | None | DONE | 5a43dc16-2746-417e-b1fe-966ca61856b2 |
| 3 | Frontend Layout & Context Sync | Fix sidebar layout for projects, fix modal URL hash regex parsing for document vs project context, filter documents by project inside project views, and enable chat history persistence. | M2 | DONE | 547ec740-7cf8-46d6-86cf-25dde7471471 |
| 4 | Dead UI Implementation | Implement Drag-and-drop upload, Create Exam modal, Create Study Document modal, standalone document collaboration, and button click logic. | M3 | DONE | a374feaa-0721-4c81-b389-1ce92fbee3e4 |
| 5 | E2E Pass & Hardening | Run all E2E tests, resolve bugs, perform Tier 5 white-box adversarial testing, and pass the Forensic Audit. | M1, M4 | DONE | 25d0592f-f3f4-4709-8e11-af5cc5cee44a |

## Interface Contracts
### Frontend ↔ Backend API Endpoints
- **Document Ingestion**: `POST /api/documents/ingest_url`
  - Request: `{ "url": string, "project_id": int | null }`
  - Response: `{ "id": int, "filename": string, "kind": string, "upload_date": string }`
- **Upload File**: `POST /api/documents/upload`
  - Request: Multipart FormData with `file`, optional `project_id`, and optional metadata fields.
  - Response: `{ "id": int, "filename": string, "kind": string, "upload_date": string }`
- **Roadmap / Learning Plan**:
  - `POST /api/projects/{project_id}/roadmap/generate` and `POST /api/documents/{document_id}/roadmap/generate`
  - Request: `{ "topic_or_text": string, "api_key": string | null }`
- **Exam Prep / Study Plan**:
  - `POST /api/generate_exam_prep` and `POST /api/generate_study_plan`
  - Request: `{ "topic_or_text": string, "api_key": string | null, "project_id": int | null, "document_id": int | null }`
  - Response: `{ "title": string, "markdown_content": string }`
- **Concept Map**:
  - `POST /api/generate_map`
  - Request: `{ "topic_or_text": string, "api_key": string | null, "project_id": int | null, "document_id": int | null }`
  - Response: `{ "nodes": [ { "id": string, "label": string, "definition": string, "formula": string | null } ], "edges": [ { "source": string, "target": string, "weight": int } ] }`

## Code Layout
- `backend/` - FastAPI backend application
  - `main.py` - FastAPI routes, startup setup, agent runners
  - `db/` - Database connection and CRUD models
  - `nlp/` - Offline/NLP utilities (quizzes, flashcards, concept maps, Vietnamese processing)
- `src/` - React frontend source code
  - `components/` - Shared components (modals, layout, sidebar)
  - `pages/` - Core page components (DocumentExplorer, DocumentViewer, Settings, etc.)
  - `utils/` - Auth, Drive, and API request wrappers
