# Handoff Report: Milestone 2 Analysis

## 1. Observation
- The endpoint `/api/documents/ingest_url` is defined at lines 665-701 in `backend/main.py`:
  ```python
  @app.post("/api/documents/ingest_url")
  def ingest_url(request: UrlIngestRequest, db: Session = Depends(get_db)):
  ```
- The `UrlIngestRequest` model is defined at lines 125-127 in `backend/main.py`:
  ```python
  class UrlIngestRequest(BaseModel):
      url: str
      project_id: int | None = None
  ```
- Database models for `ChatMessage` (lines 122-132) and `Artifact` (lines 134-144) in `backend/db/models.py` only possess a `project_id` foreign key referencing the `projects` table, and both columns are mandatory (`nullable` defaults to False). They are missing a `document_id` column.
- Database model for `Flashcard` (lines 6-17) in `backend/db/models.py` has no column for either `project_id` or `document_id`.
- The CRUD functions in `backend/db/crud.py` filter and save messages and artifacts strictly by `project_id`:
  - `save_chat_message` (line 119) requires `project_id` and does not accept `document_id`.
  - `create_artifact` (line 126) and `get_artifacts` (line 133) only take `project_id`.
  - Flashcard functions (`create_flashcard`, `get_flashcards`, `get_due_flashcards`) do not accept or filter by any project/document context.

---

## 2. Logic Chain
- **URL Ingestion Endpoint**:
  1. Setting `/api/documents/url` as an alias is required.
  2. Because FastAPI allows stacking route decorators, we can add `@app.post("/api/documents/url")` immediately above the definition of `ingest_url` at line 665.
  3. Since the payload must be the same, `UrlIngestRequest` will serve both routes.
- **Dual Contexts for Chats, Artifacts, and Flashcards**:
  1. The user rules specify that features must support both project contexts (`project_id`) and standalone document contexts (`document_id`).
  2. To achieve this, the tables `chat_messages` and `artifacts` must have their `project_id` columns made nullable, and a nullable `document_id` column must be added referencing `documents.id`.
  3. The `flashcards` table must be updated to have both `project_id` (referencing `projects.id`) and `document_id` (referencing `documents.id`) columns.
  4. Corresponding CRUD functions in `backend/db/crud.py` must be updated to handle these optional fields.
  5. The API routes in `backend/main.py` (`/api/chat`, `/api/generate_flashcards`, `/api/flashcards/due`, etc.) must be updated to parse both parameters and use the updated CRUD layer.

---

## 3. Caveats
- Since SQLite does not dynamically modify existing table schemas on model updates, a dynamic database schema patch script must run on backend startup to alter existing tables for active setups.
- Frontend files (`src/pages/DocumentViewer.jsx`, etc.) may not yet supply `document_id` to endpoints (such as `/api/chat` or `/api/generate_flashcards`), which should be addressed in subsequent frontend development task scopes.

---

## 4. Conclusion
- The backend needs to expose `/api/documents/url` via a stacked FastAPI decorator on `ingest_url`.
- Database models for `ChatMessage`, `Artifact`, and `Flashcard` must be updated to support nullable `project_id` and optional `document_id` fields.
- CRUD methods and request schemas must be updated to pass and filter by these IDs.
- A dynamic patching routine must be introduced on backend startup to seamlessly add columns to existing SQLite database instances.

---

## 5. Verification Method
- **Startup & API Alias Validation**:
  - Run the backend: `python -m uvicorn main:app --port 8000 --reload` (within the `backend/` directory).
  - Open `http://127.0.0.1:8000/docs` in the browser or run a GET request to verify both `/api/documents/ingest_url` and `/api/documents/url` are registered and active.
- **SQLite Database Schema Verification**:
  - Open the SQLite database: `sqlite3 omilearn_local.db` (or from the workspace path).
  - Run `.schema chat_messages`, `.schema artifacts`, and `.schema flashcards` to confirm new columns (`document_id`, `project_id`) are present.
- **API Functional Tests**:
  - Run `python test_api.py` to ensure core API functionality has not regressed.
