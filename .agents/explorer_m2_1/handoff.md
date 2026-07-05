# Handoff Report — Explorer 1 (Milestone 2)

## 1. Observation
- **Scope Contract**: Defined in `.agents/sub_orch_m2/SCOPE.md`:
  - `ChatMessage` and `Artifact` models must support optional `document_id`.
  - `Flashcard` model must support optional `project_id` and `document_id`.
  - Startup migration/schema-patching routine is needed in `backend/main.py` before table creation.
  - CRUD operations (`create_flashcard`, `get_flashcards`, `get_due_flashcards`, `create_artifact`, `get_artifacts`, `save_chat_message`, `get_chat_history`) must filter/save by these IDs.
  - Endpoint `/api/documents/url` alias is required.
- **Model Declarations**: Observed in `backend/db/models.py`:
  - Line 6-17: `class Flashcard(Base)` lacks `project_id` and `document_id` columns.
  - Line 122-132: `class ChatMessage(Base)` has `project_id = Column(Integer, ForeignKey("projects.id"))` but lacks `document_id`.
  - Line 134-144: `class Artifact(Base)` has `project_id = Column(Integer, ForeignKey("projects.id"))` but lacks `document_id`.
- **Database Initialization**: Observed in `backend/main.py`:
  - Line 50: `models.Base.metadata.create_all(bind=engine)` is called directly without Alembic or check-based migrations.
- **CRUD Operations**: Observed in `backend/db/crud.py`:
  - Line 5: `def get_flashcards(db: Session, skip: int = 0, limit: int = 100):` returns all cards without filtering.
  - Line 28: `def get_due_flashcards(db: Session):` filters only by due date.
  - Line 32: `def create_flashcard(db: Session, front: str, back: str):` only writes front and back.
  - Line 119: `def save_chat_message(...)` only takes `project_id`.
  - Line 126: `def create_artifact(...)` only takes `project_id`.
  - Line 133: `def get_artifacts(...)` filters only by `project_id`.
  - Line 136: `def get_chat_history(...)` filters only by `project_id`.

## 2. Logic Chain
- **Step 1**: To satisfy the Project vs. Standalone Document contexts constraint, models must hold optional foreign key references to the respective scoping entities (`projects` and `documents`). Nullable relationships will allow either scoping reference to be omitted.
- **Step 2**: Modifying SQLAlchemy models alone triggers SQLAlchemy errors if columns are missing from an already-created SQLite database.
- **Step 3**: Since standard Alembic migrations are not configured, a programmatic startup function using SQLAlchemy's `inspect` utility can verify column existence in tables at runtime and run safe `ALTER TABLE ... ADD COLUMN ...` statements if columns do not exist.
- **Step 4**: CRUD operations must filter queries when scope IDs are provided to prevent context leak (e.g. flashcards of document A appearing in document B).
- **Step 5**: Route handlers must receive these ID fields from FastAPI requests, pass them to NLP utility invocations and CRUD helpers, and expose the alias endpoint mapping the new `/api/documents/url` route to the existing URL ingestion functionality.

## 3. Caveats
- SQLite does not easily support dropping columns or modifying constraints (e.g., changing a column from `NOT NULL` to `NULL`) without recreating the table. However, since the default nullability constraint for standard SQLAlchemy columns is `nullable=True`, the existing column fields in target tables permit NULL values in database files, meaning no table reconstruction is required.

## 4. Conclusion
We have mapped out a strategy to migrate schemas, implement dynamic patching, adjust CRUD code, and update API endpoints.
All modifications are captured in a precise diff file located at:
`/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_1/changes.patch`

## 5. Verification Method
- **Method**:
  1. Inspect the patch file `changes.patch` to verify alignment with structural requirements.
  2. Apply the patch using: `git apply .agents/explorer_m2_1/changes.patch` (or manually adjust files accordingly).
  3. Start the backend with `python test_api.py`. It should print:
     ```
     Starting backend...
     Testing /api/generate_quiz
     Quiz Response Status: 200
     Testing /api/generate_map
     Map Response Status: 200
     Testing /api/generate_flashcards
     Flashcard Generate Status: 200
     ...
     ```
  4. Manually verify schema modifications in sqlite via python console:
     ```python
     from sqlalchemy import inspect
     from db.database import engine
     inspector = inspect(engine)
     print([c["name"] for c in inspector.get_columns("flashcards")]) # should include 'project_id', 'document_id'
     ```
