# Milestone 2 Analysis: API Routing, Schema Contexts & Ingestion Aliases

## 1. Executive Summary
This analysis details the proposed changes to the backend codebase to support dual Project and Standalone Document contexts for Chats, Artifacts, and Flashcards, and to expose the `/api/documents/url` endpoint as an alias for URL ingestion.

---

## 2. Ingestion URL Alias Endpoint
### Current Implementation
The URL ingestion endpoint is defined in `backend/main.py` at line 665 as:
```python
@app.post("/api/documents/ingest_url")
def ingest_url(request: UrlIngestRequest, db: Session = Depends(get_db)):
    ...
```
The request schema `UrlIngestRequest` is defined as:
```python
class UrlIngestRequest(BaseModel):
    url: str
    project_id: int | None = None
```

### Proposed Changes
To expose `/api/documents/url` as an alias that accepts the same payload:
1. **Option A (Stacked decorators - Recommended)**:
   FastAPI allows stacking multiple route decorators onto a single handler function. This avoids code duplication and exposes the exact same logic.
   ```python
   @app.post("/api/documents/ingest_url")
   @app.post("/api/documents/url")
   def ingest_url(request: UrlIngestRequest, db: Session = Depends(get_db)):
       ...
   ```
2. **Option B (Separate wrapper route)**:
   Alternatively, we can define a dedicated alias function that delegates directly to `ingest_url`:
   ```python
   @app.post("/api/documents/url")
   def ingest_url_alias(request: UrlIngestRequest, db: Session = Depends(get_db)):
       return ingest_url(request, db)
   ```

To ensure compatibility with standalone document contexts, `UrlIngestRequest` should be updated to accept `document_id` as well:
```python
class UrlIngestRequest(BaseModel):
    url: str
    project_id: int | None = None
    document_id: int | None = None
```

---

## 3. Context Analysis: Chats, Artifacts, and Flashcards

### 3.1. Chats (ChatMessage)
- **Current State**:
  - `ChatMessage` table in `backend/db/models.py` has a mandatory `project_id` column and no `document_id` column.
  - CRUD functions `save_chat_message` and `get_chat_history` filter strictly by `project_id`.
  - The API endpoint `/api/chat` expects `project_id` and does not save messages or retrieve appropriate document context if only `document_id` is supplied.
- **Proposed Strategy**:
  - Make `project_id` nullable in `models.ChatMessage`.
  - Add `document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)` to `models.ChatMessage`.
  - Update `save_chat_message` to take optional `project_id` and `document_id`.
  - Update `get_chat_history` to support querying by either `project_id` or `document_id`.
  - In `/api/chat` endpoint, if `context` is empty and `document_id` is supplied, pull the document text directly from the database and feed it to the agent context.
  - Expose `GET /api/documents/{document_id}/messages` for retrieving chat history for standalone documents.

### 3.2. Artifacts
- **Current State**:
  - `Artifact` table in `backend/db/models.py` requires a `project_id` column and lacks a `document_id` column.
  - CRUD functions `create_artifact` and `get_artifacts` are strictly restricted to `project_id`.
  - API endpoints `/api/generate_quiz`, `/api/generate_exam_prep`, and `/api/generate_study_plan` only save generated artifacts in DB if `request.project_id` is defined.
- **Proposed Strategy**:
  - Make `project_id` nullable in `models.Artifact`.
  - Add `document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)` to `models.Artifact`.
  - Update CRUD functions to support optional `project_id` and `document_id` parameters.
  - Update quiz, exam prep, and study plan endpoints to save artifacts if `request.project_id` OR `request.document_id` is provided.
  - Expose `GET /api/documents/{document_id}/artifacts` endpoint for standalone documents.

### 3.3. Flashcards
- **Current State**:
  - `Flashcard` table in `backend/db/models.py` has NO relationship to projects or documents (global flashcards).
  - CRUD functions `get_flashcards`, `get_due_flashcards`, and `create_flashcard` operate globally.
  - API endpoint `/api/generate_flashcards` does not support associating flashcards with a project or document.
- **Proposed Strategy**:
  - Add `project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)` and `document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)` to `models.Flashcard`.
  - Update `FlashcardRequest` schema in `backend/main.py` to support optional `project_id` and `document_id`.
  - Update `/api/generate_flashcards` endpoint to parse and pass these IDs during card creation.
  - Update `/api/flashcards/due` endpoint to accept query parameters `project_id` and `document_id` to filter due cards.

---

## 4. Dynamic SQLite Schema Patching on Startup
Since SQLite does not dynamically add columns when SQLAlchemy models are modified (if tables already exist), we must add a runtime patch routine in `backend/main.py` before executing `metadata.create_all`:

```python
def patch_database_schema(engine):
    from sqlalchemy import text
    with engine.begin() as conn:
        # 1. Patch chat_messages
        cursor = conn.execute(text("PRAGMA table_info(chat_messages)"))
        chat_cols = [row[1] for row in cursor.fetchall()]
        if "document_id" not in chat_cols:
            conn.execute(text("ALTER TABLE chat_messages ADD COLUMN document_id INTEGER REFERENCES documents(id)"))
            
        # 2. Patch artifacts
        cursor = conn.execute(text("PRAGMA table_info(artifacts)"))
        art_cols = [row[1] for row in cursor.fetchall()]
        if "document_id" not in art_cols:
            conn.execute(text("ALTER TABLE artifacts ADD COLUMN document_id INTEGER REFERENCES documents(id)"))
            
        # 3. Patch flashcards
        cursor = conn.execute(text("PRAGMA table_info(flashcards)"))
        fc_cols = [row[1] for row in cursor.fetchall()]
        if "project_id" not in fc_cols:
            conn.execute(text("ALTER TABLE flashcards ADD COLUMN project_id INTEGER REFERENCES projects(id)"))
        if "document_id" not in fc_cols:
            conn.execute(text("ALTER TABLE flashcards ADD COLUMN document_id INTEGER REFERENCES documents(id)"))
```

This function will be imported/called during the backend bootstrap inside `backend/main.py` before `Base.metadata.create_all(bind=engine)`.
