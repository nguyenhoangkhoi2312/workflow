# Milestone 2 Code Review Report

## Review Summary

**Verdict**: APPROVE

All 71 E2E tests pass successfully. The backend implementation for Milestone 2 is robust, correctly handling database model schema updates, CRUD helpers, endpoints, schema patching, and local NLP fallbacks for both Project and Standalone Document contexts. 

---

## Findings

### [Minor] Finding 1: Inconsistent Roadmap Creation Architecture
- **What**: The endpoint `/api/documents/{document_id}/roadmap/generate` directly implements database insertion logic for roadmaps and roadmap items instead of delegating to a CRUD helper, whereas the project roadmap endpoint `/api/projects/{project_id}/roadmap/generate` calls `crud.create_roadmap()`.
- **Where**: `backend/main.py` (lines 441-453) vs `backend/db/crud.py` (line 13).
- **Why**: This bypasses the DB abstraction layer and creates duplicate database transaction code.
- **Suggestion**: Refactor `crud.create_roadmap` to accept an optional `document_id` parameter and handle the database insertions uniformly for both project and document contexts.

### [Minor] Finding 2: Unreachable Duplicate Code Block
- **What**: In the project roadmap generation endpoint, there is a duplicated block of code that is completely unreachable due to a preceding `return` statement.
- **Where**: `backend/main.py` (lines 421-424).
- **Why**: Dead/redundant code.
- **Suggestion**: Remove lines 421-424 to clean up the endpoint handler.

### [Medium] Finding 3: Potential Orphaned Database Records on Cascaded Project Deletion
- **What**: When a project is deleted, its documents are cascade-deleted via SQLAlchemy. However, the deletion of these documents does not trigger the deletion of their related `QuizScore` or `Roadmap` records in SQLite, since no cascade is configured on those relationships.
- **Where**: `backend/db/models.py` (line 104) and `backend/db/crud.py` (line 125).
- **Why**: Can lead to orphaned rows in tables like `quiz_scores` if a document is deleted via project cascade.
- **Suggestion**: Add appropriate cascade definitions on `Document` relationships or manually clean up all document-related rows in `delete_project`.

---

## Verified Claims

- **All 71 E2E tests pass** → Verified via running `python3 run_e2e_tests.py` clean → **PASS** (71 passed in 23.50s)
- **Database schema patching for document_id and project_id** → Verified via inspecting `patch_database_schema` in `backend/main.py` → **PASS**
- **Support for Standalone Document contexts** → Verified via inspecting `models.py` nullable fields and E2E tests `test_t4_standalone_document_workspace` and `test_t3_standalone_document_flow` → **PASS**
- **Offline fallbacks for Quiz, Exam Prep, Study Plan, and Concept Map** → Verified via inspecting `backend/nlp/concept_map.py` and checking the offline logic under uvicorn. → **PASS**

---

## Coverage Gaps

- **SQLite Foreign Key Enforcement** — risk level: **medium** — recommendation: investigate/enable explicitly on connection setup. SQLite does not enforce foreign keys unless `PRAGMA foreign_keys = ON` is run.

---

## Unverified Items

- None. All items within the scope of Milestone 2 have been fully reviewed and verified.

---
---

# Adversarial Challenge Report

## Challenge Summary

**Overall risk assessment**: LOW

The overall implementation has very high stability. It gracefully handles error boundary cases (empty inputs, invalid keys) and has a bulletproof try-except fallback mechanism on all LLM calls.

---

## Challenges

### [Low] Challenge 1: Absence of SQLite Foreign Key Enforcement
- **Assumption challenged**: SQLite automatically enforces referential integrity on delete.
- **Attack scenario**: A document is deleted, but its linked `quiz_scores` are not deleted because foreign keys are not enforced. Over time, the DB collects orphaned entries, which may cause unexpected behavior on statistical queries.
- **Blast radius**: Low/Medium. Accumulation of orphaned database rows.
- **Mitigation**: Enable SQLite foreign key pragma in SQLAlchemy `connect` events:
  ```python
  from sqlalchemy.engine import Engine
  from sqlalchemy import event
  @event.listens_for(Engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      cursor = dbapi_connection.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()
  ```

### [Low] Challenge 2: Extractive Summary TF-IDF crash under empty or ultra-short text
- **Assumption challenged**: Input text to `generate_offline_exam_prep` or `generate_offline_study_plan` contains enough sentences and vocabulary for TF-IDF.
- **Attack scenario**: User uploads an empty text file or a file containing only a single word. `TfidfVectorizer().fit_transform()` raises a `ValueError: empty vocabulary`.
- **Blast radius**: Low. The exceptions are handled gracefully in try-except blocks, but it defaults to basic list slicing which could lead to empty outputs.
- **Mitigation**: Add checks for `if not sentences:` and return a predefined default dict structure early.

---

## Stress Test Results

- **Empty vocabulary input** → `generate_offline_exam_prep` catches ValueError in try-except and falls back to return a valid response → **PASS**
- **Invalid API Key for LLM** → Falls back to local NLP library methods without throwing unhandled exceptions → **PASS**
- **Standalone document collaboration and workspace invites** → All endpoints return expected values and persist constraints correctly → **PASS**

---

## Unchallenged Areas

- **Frontend layout rendering** — reason not challenged: Milestone 2 scope is strictly limited to backend models, CRUD operations, and endpoints.
