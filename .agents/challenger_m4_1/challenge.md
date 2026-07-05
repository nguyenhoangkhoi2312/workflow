## Challenge Summary

**Overall risk assessment**: HIGH

Milestone 4 implementation introduces several critical database leaks, context isolation failures, and dead UI behaviors. While the pytest test suite runs and passes successfully, the verification scripts reveal that deleting projects/documents leaves orphan database records. Furthermore, multiple React modals ignore project and document contexts, causing data to be generated globally.

---

## Challenges

### [High] Challenge 1: Database Leaks and Orphan Records during Cascade Deletes

- **Assumption challenged**: Deleting a project or a document cleans up all associated records in the database.
- **Attack scenario**: 
  - Execution of `tests/verify_db_migration.py` shows that deleting a document directly leaks `ProjectMember` and `ProjectInvite` records matching the deleted document's `document_id`.
  - When a project is deleted, its documents are cascade-deleted at the DB level, bypassing `crud.delete_document`. Because there are no SQLAlchemy model relationship cascades (or foreign key cascades) defined for `QuizScore`, `Roadmap`, and `Flashcard` under `Document`, deleting the project leaves all their document-level records orphaned in the database.
- **Blast radius**: Storage bloat, relational inconsistency, and memory leakages inside the SQLite database.
- **Mitigation**: 
  - Add explicit SQLAlchemy cascades (`cascade="all, delete-orphan"`) on `Document` model for `QuizScore`, `Roadmap`, and `Flashcard`.
  - Update `crud.delete_document` to delete matching `ProjectMember` and `ProjectInvite` records before deleting the document.

### [High] Challenge 2: Context Isolation Bypass in React Modals

- **Assumption challenged**: Frontends preserve isolation between Project context and Standalone Document context.
- **Attack scenario**: 
  - The `FlashcardReviewModal` component makes a POST request to `/api/generate_flashcards` but only sends `{ topic_or_text, api_key }`. It does not pass `project_id` or `document_id`. Thus, all flashcards generated via this modal are stored globally (with `project_id = null` and `document_id = null`), leaking into other documents and projects.
  - Similarly, `ConceptMapModal` calls `/api/generate_map` and `SmartNotesModal` calls `/api/generate_notes` without supplying `project_id` or `document_id` in their request bodies.
- **Blast radius**: Direct violation of the multi-context user rules, leading to shared study flashcards and artifacts cross-contaminating unrelated workspaces.
- **Mitigation**: Modify the modals to accept `projectId` and `documentId` as props and pass them in their fetch payloads.

### [Medium] Challenge 3: Unimplemented Collaboration Invite Acceptance API

- **Assumption challenged**: Classmates can accept invitations to collaborate on projects or documents.
- **Attack scenario**: 
  - The `ProjectCollaborationModal` allows sending invites to external users, inserting a row in the `project_invites` table.
  - However, there are no endpoints in `backend/main.py` that allow accepting or joining an invite, meaning invites remain permanently `pending` and cannot transition to `ProjectMember`.
- **Blast radius**: Collaboration feature is a dead end; users cannot actually share or collaborate on documents beyond listing pending invite emails.
- **Mitigation**: Implement a POST `/api/invites/{invite_id}/accept` backend endpoint to convert pending invites to active project/document members.

### [Low] Challenge 4: Dead Components and Static Buttons

- **Assumption challenged**: All UI components are wired up and functioning.
- **Attack scenario**:
  - `StudyDocProgressModal.jsx` is completely unused and never imported anywhere in the React app.
  - The "Study Doc" button in the sidebars maps to `CreateStudyDocModal` instead of showing analytics.
  - The "Tải lên file từ máy" (Upload file from computer) button in both `CreateExamModal.jsx` and `CreateStudyDocModal.jsx` is purely static and does not trigger any file picker or input handler.
- **Blast radius**: Dead code in the production bundle, misleading UI controls, and broken user flows for creating exam/study docs from local files.
- **Mitigation**: Clean up or route the modals properly, and hook up the upload buttons to actual `<input type="file">` controls.

---

## Stress Test Results

- **Project Deletion Cascade** → Expected all document-level dependent tables to be cleared → Actual: `QuizScore`, `Roadmap`, and `Flashcard` records with `project_id = null` leaked → **FAIL**
- **Document Deletion Cascade** → Expected project members and invites bound to document to be cleared → Actual: `ProjectMember` and `ProjectInvite` records leaked → **FAIL**
- **Flashcard Context Generation** → Expected cards to be bound to project or document → Actual: Cards generated without `project_id` and `document_id` (created globally) → **FAIL**
- **Test Suite Execution** → Expected test command `backend/venv/bin/python3 run_e2e_tests.py` to run synchronously and verify all happy/unhappy API routes → Actual: 71/71 tests passed and results parsed correctly → **PASS**

---

## Unchallenged Areas

- **OAuth & File Ingestion Pipelines** — Out of scope for Milestone 4 verification constraints.
