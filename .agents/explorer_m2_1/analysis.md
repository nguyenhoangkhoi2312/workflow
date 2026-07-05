# Analysis & Strategy Report — Milestone 2 (Database Schemas and Migration)

## 1. Problem Boundary & Objectives
To ensure the application supports both **Project** contexts (`project_id`) and **Standalone Document** contexts (`document_id`), we must update database models, provide a startup migration/schema-patching routine for SQLite stability, and extend CRUD operations and API routes to handle both context paths.

## 2. Codebase Observations

### A. Database Models (`backend/db/models.py`)
- **`ChatMessage`**: Has `project_id` but lacks `document_id`. The `project_id` foreign key constraint is currently non-explicit about nullability, meaning it defaults to nullable in SQLAlchemy but we must explicitly support optionality for standalone documents.
- **`Artifact`**: Has `project_id` but lacks `document_id`.
- **`Flashcard`**: Completely lacks both `project_id` and `document_id` fields, making flashcards global.

### B. Database Initialization & Startup Migration (`backend/main.py`)
- The FastAPI application initializes database schemas on startup via `models.Base.metadata.create_all(bind=engine)`.
- If we change the SQLAlchemy models, existing user databases (`omilearn_local.db`) will fail when the application attempts to insert or query the new columns because SQLite lacks the columns.
- We need a schema-patching routine that dynamically runs `ALTER TABLE ... ADD COLUMN ...` statements before `create_all()` is executed.

### C. Database CRUD operations (`backend/db/crud.py`)
- **`get_flashcards`** and **`get_due_flashcards`** retrieve flashcards globally. They must accept optional `project_id` and `document_id` and filter accordingly.
- **`create_flashcard`** must accept optional `project_id` and `document_id` and store them.
- **`save_chat_message`** and **`get_chat_history`** are hardcoded to `project_id`. They must support optional `document_id`.
- **`create_artifact`** and **`get_artifacts`** are hardcoded to `project_id`. They must support optional `document_id`.

### D. API Endpoints (`backend/main.py`)
- The request schemas (like `ChatRequest`, `FlashcardRequest`, `TopicRequest`) and endpoint functions for chat, artifacts, and flashcards must be updated to pass and accept `document_id` and route query logic correctly.
- We need to expose a `/api/documents/url` POST alias for URL/YouTube ingestion, behaving identically to `/api/documents/ingest_url`.

---

## 3. Proposed Fix Strategy

### Phase 1: Model Updates (`backend/db/models.py`)
Add nullable ForeignKey columns and relationships to the SQLAlchemy models:
- **`ChatMessage`**:
  ```python
  project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
  document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
  document = relationship("Document")
  ```
- **`Artifact`**:
  ```python
  project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
  document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
  document = relationship("Document")
  ```
- **`Flashcard`**:
  ```python
  project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
  document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
  project = relationship("Project")
  document = relationship("Document")
  ```

### Phase 2: Dynamic SQLite Schema-Patching (`backend/main.py`)
Define and invoke `patch_database_schema(engine)` prior to `Base.metadata.create_all`:
```python
def patch_database_schema(engine):
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    with engine.begin() as conn:
        # 1. ChatMessage document_id
        if "chat_messages" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("chat_messages")]
            if "document_id" not in cols:
                conn.execute("ALTER TABLE chat_messages ADD COLUMN document_id INTEGER REFERENCES documents(id)")
                
        # 2. Artifact document_id
        if "artifacts" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("artifacts")]
            if "document_id" not in cols:
                conn.execute("ALTER TABLE artifacts ADD COLUMN document_id INTEGER REFERENCES documents(id)")
                
        # 3. Flashcard project_id and document_id
        if "flashcards" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("flashcards")]
            if "project_id" not in cols:
                conn.execute("ALTER TABLE flashcards ADD COLUMN project_id INTEGER REFERENCES projects(id)")
            if "document_id" not in cols:
                conn.execute("ALTER TABLE flashcards ADD COLUMN document_id INTEGER REFERENCES documents(id)")
```

### Phase 3: CRUD & Request Schema Updates (`backend/db/crud.py` and `backend/main.py`)
1. Update `ChatRequest` and `FlashcardRequest` Pydantic models to include `document_id: int | None = None`.
2. Update the CRUD helper functions to build query filters dynamically:
   - For `get_flashcards`, `get_due_flashcards`, `get_artifacts`, `get_chat_history`: filter by `project_id == project_id` and/or `document_id == document_id` if provided.
   - For `create_flashcard`, `create_artifact`, `save_chat_message`: accept and save `project_id` and `document_id`.

### Phase 4: Route Handlers (`backend/main.py`)
1. Extend `/api/chat`: if `request.document_id` is supplied without `context`, pull `doc.content` from the database. Save history with `document_id`.
2. Expose `@app.get("/api/documents/{document_id}/messages")` and `@app.get("/api/documents/{document_id}/artifacts")` to fetch document-scoped entities.
3. Update artifact generation endpoints (`/api/generate_quiz`, `/api/generate_exam_prep`, `/api/generate_study_plan`) to save artifacts using the correct project or document context.
4. Expose the URL ingestion alias by attaching `@app.post("/api/documents/url")` to `ingest_url`.
