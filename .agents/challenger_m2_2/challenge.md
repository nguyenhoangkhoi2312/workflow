# Challenge Report — Database Migration & Cascade Deletes

## Challenge Summary

**Overall risk assessment**: HIGH

Through empirical verification and automated testing, we validated the startup schema-patching mechanism and the cascading delete behaviors under both project and document deletions. 

Our findings indicate:
1. **Startup Schema Patching**: Functions correctly. Schema migrations successfully apply to pre-existing SQLite tables by adding the requested columns (`document_id` and `project_id`) without data loss or corruption.
2. **Cascade Deletion**: Contains critical flaws that lead to orphaned records (database leaks) and potential security/access control vulnerabilities.
   - Under **Document deletion**: `ProjectMember` and `ProjectInvite` records referencing the deleted document are orphaned.
   - Under **Project deletion**: SQLAlchemy's cascade delete deletes `Document` rows, but because SQLite's foreign key constraint enforcement is disabled and SQLAlchemy models do not define relationships from `Document` to child tables (such as `QuizScore`, `Roadmap`, etc.), all child records for those deleted documents are orphaned in the database.
   - Under **Physical storage**: Uploaded files in `backend/uploads/` are never deleted from disk when their corresponding database document is deleted.

---

## Challenges

### [High] Challenge 1: Cascading Deletion Leakage on Project Deletion (Orphaned Document Child Records)

- **Assumption challenged**: The assumption that deleting a `Project` cascade-deletes all its child resources and their nested structures (e.g. document quizzes, roadmaps, flashcards) cleanly.
- **Attack scenario**: A user creates a project, uploads documents, generates roadmaps, and takes quizzes (creating `QuizScore` records). The user later deletes the project. SQLAlchemy cascades the deletion of the `Document` records. However, because SQLite's foreign key constraint enforcement is disabled by default and the `Document` model lacks cascade relationships to `QuizScore`, `Roadmap`, `Flashcard`, `ChatMessage`, and `Artifact`, the child rows referencing those deleted documents are permanently orphaned.
- **Blast radius**: High database pollution. Orphaned rows accumulate indefinitely, increasing the database size and potentially causing queries (e.g. fetching all flashcards or roadmaps across the app) to return invalid records referencing non-existent documents.
- **Mitigation**:
  1. Enable SQLite foreign key constraint enforcement in `backend/db/database.py`:
     ```python
     from sqlalchemy import event
     @event.listens_for(engine, "connect")
     def set_sqlite_pragma(dbapi_connection, connection_record):
         cursor = dbapi_connection.cursor()
         cursor.execute("PRAGMA foreign_keys=ON")
         cursor.close()
     ```
  2. Update database models in `backend/db/models.py` to specify `ondelete="CASCADE"` on the foreign keys:
     ```python
     document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
     ```

### [High] Challenge 2: Access Control Leakage on Document Deletion (Orphaned ProjectMember & ProjectInvite)

- **Assumption challenged**: The assumption that deleting a `Document` cleans up all metadata and permissions associated with it.
- **Attack scenario**: A user uploads a document, invites a collaborator, and then deletes the document. The document's record is deleted, but the `ProjectMember` and `ProjectInvite` records referencing it remain in the database. If a new document is later uploaded and assigned the same auto-incremented primary key ID, the previous collaborator automatically gains active access/pending invitation to the new document.
- **Blast radius**: Security and privacy violation. Unintended access to confidential documents.
- **Mitigation**: Update `crud.delete_document` in `backend/db/crud.py` to delete associated member and invite records:
  ```python
  db.query(models.ProjectMember).filter(models.ProjectMember.document_id == doc_id).delete()
  db.query(models.ProjectInvite).filter(models.ProjectInvite.document_id == doc_id).delete()
  ```

### [Medium] Challenge 3: Physical Uploaded File Leakage on Document Deletion

- **Assumption challenged**: Deleting a document removes its physical storage footprint.
- **Attack scenario**: A user uploads a 50MB PDF or a video file. The file is copied to `backend/uploads/{doc_id}{suffix}`. The user deletes the document. `crud.delete_document` deletes the DB rows but does not clean up the file on disk.
- **Blast radius**: Disk space exhaustion.
- **Mitigation**: Update `crud.delete_document` to find and delete matching files in the `uploads` directory:
  ```python
  import glob
  import os
  from main import UPLOAD_DIR
  
  files = glob.glob(os.path.join(UPLOAD_DIR, f"{doc_id}.*"))
  for f in files:
      try:
          os.remove(f)
      except OSError:
          pass
  ```

---

## Stress Test Results

- **Startup Schema Patching** → Simulating older SQLite schema populated with data and running startup patch script → New columns are appended to tables and all pre-existing records remain intact → **PASS**
- **Document Deletion Cascade (Database-only)** → Delete document Doc B and check child records → `QuizScore`, `Roadmap`, `ChatMessage`, `Artifact`, `Flashcard` are deleted → **PASS** (Explicitly handled in `crud.delete_document`)
- **Document Deletion Cascade (Members & Invites)** → Delete document Doc B and check `ProjectMember`/`ProjectInvite` rows → Records still exist in DB → **FAIL** (Leaked)
- **Project Deletion Cascade (Nested Document Childs)** → Delete Project and check child records of its documents (`QuizScore`, document-level `Roadmap`/`Flashcard`) → Records still exist in DB → **FAIL** (Leaked)
- **Physical Document Cleanup** → Delete document Doc B and check `backend/uploads/` → File still exists on disk → **FAIL** (Leaked)

---

## Unchallenged Areas

- **Concurrency & DB Locking** — Did not simulate high concurrent write/delete operations on SQLite which might trigger database lock errors.
- **PyInstaller Runtime Behaviors** — The frozen binary packaging setup in `backend/main.py` was not tested because the E2E tests and verification scripts were run against the source code python execution environment.
