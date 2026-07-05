# Scope: Milestone 2 (Backend Stability & Schema Contexts)

## Architecture
- `backend/db/models.py`: SQLAlchemy models for ChatMessage, Artifact, Flashcard.
- `backend/main.py`: FastAPI entry point. Performs startup, runs migrations, defines routes, including `/api/documents/url` alias.
- `backend/db/crud.py`: DB access layer. Handles creation/fetching of ChatMessage, Artifact, Flashcard, filtering by project/document context.
- `backend/nlp/concept_map.py`: Concept mapping and offline NLP.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Database Schema Contexts & Patching | Update models (ChatMessage, Artifact, Flashcard), add dynamic SQLite schema-patching on startup. | None | PLANNED |
| 2 | CRUD & Endpoint Context updates | Update CRUD functions and API routes to support project_id/document_id. | M1 | PLANNED |
| 3 | API Ingestion URL Alias | Expose /api/documents/url alias endpoint in main.py. | None | PLANNED |
| 4 | Offline Local-NLP Fallbacks | Implement offline TF-IDF/TextRank for exam prep, study plan, path, suggestions, and concept definitions/formulas. | None | PLANNED |
| 5 | Verification & Testing | Test all backend endpoints using unit/integration test suite to verify stability and correctness. | M1, M2, M3, M4 | PLANNED |

## Interface Contracts
### CRUD ↔ API Endpoints
- `create_flashcard`, `get_flashcards`, `get_due_flashcards`: Support both `project_id` and `document_id`.
- `create_artifact`, `get_artifacts`: Support optional `document_id`.
- `save_chat_message`, `get_chat_history`: Support optional `document_id`.
- `/api/documents/url` accepts same payload as `/api/documents/ingest_url`.
