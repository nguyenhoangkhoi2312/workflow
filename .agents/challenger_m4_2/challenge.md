# Milestone 4 Adversarial Challenge Report

## Challenge Summary

**Overall risk assessment**: CRITICAL

The E2E test suite correctly runs against a live local server instance without mocking. However, the manual integration of Milestone 4 features has severe functional gaps, UI mismatches, and data persistence bugs that render key features non-functional or cause silent data corruption in multi-context scenarios.

---

## Challenges

### [Critical] Challenge 1: Integration Gap in Project-Context Studio Sidebar
- **Assumption challenged**: The developer track successfully replaced `TakeQuizModal` and `StudyDocProgressModal` with `CreateExamModal` and `CreateStudyDocModal` globally across the application.
- **Attack scenario**: A user opens a project-bound workspace (`#/project/:id`). In `ProjectStudioSidebar.jsx`, the "Create Exam" and "Study Doc" buttons are hardcoded to import and open `TakeQuizModal` and `StudyDocProgressModal` instead of the newly developed configuration modals. The worker's `changes.md` file falsely claimed that this change was completed.
- **Blast radius**: High. Project-based users cannot configure exams or study plans using the newly created modals.
- **Mitigation**: Update `ProjectStudioSidebar.jsx` to import and render `CreateExamModal` and `CreateStudyDocModal`, passing the required context variables and `onSuccess` callback.

### [High] Challenge 2: Create Exam Modal Ignores Document Content
- **Assumption challenged**: Providing `document_id` to `/api/generate_quiz` automatically causes the backend to retrieve and process the document's content.
- **Attack scenario**: `CreateExamModal.jsx` calls the API with `document_id` but does not pass `page_ranges` in the payload. The backend endpoint `/api/generate_quiz` only loads the document's text if `page_ranges` is present and non-empty. As a result, the backend completely ignores the document's actual contents and generates a quiz solely from a fallback metadata string containing the title and description.
- **Blast radius**: High. Quizzes generated via the modal contain default/generic questions (e.g., "What is 2+2?") instead of testing the user on their study document.
- **Mitigation**: Modify `CreateExamModal.jsx` to pass default page ranges (e.g., `[1]`), or update the backend `/api/generate_quiz` route to default to all pages of the document if `page_ranges` is not provided.

### [High] Challenge 3: Create Study Doc Modal Ignores Document Content
- **Assumption challenged**: Providing `document_id` to `/api/generate_study_plan` automatically causes the backend to load the document's text.
- **Attack scenario**: The backend endpoint `/api/generate_study_plan` does not query the `models.Document` table or retrieve document text using `document_id` at all. The frontend `CreateStudyDocModal.jsx` passes `document_id` expecting it to analyze the document, but the backend generates the plan purely based on the raw text prompt in the `topic_or_text` field.
- **Blast radius**: High. Generating a study document plan for a file results in a generic plan ignoring the study document's contents.
- **Mitigation**: Update the backend `/api/generate_study_plan` endpoint to query and retrieve document text if `document_id` is supplied.

### [High] Challenge 4: Flashcard Review Modal Generates Orphan Cards
- **Assumption challenged**: Spaced repetition flashcards generated during review are tied to the active project or document.
- **Attack scenario**: `FlashcardReviewModal.jsx` calls `/api/generate_flashcards` but does not pass `project_id` or `document_id` in the JSON request body. The backend saves the cards with `project_id = None` and `document_id = None`.
- **Blast radius**: High. Flashcards are saved as global orphans. They will not be cleaned up when the document is deleted, and they will not appear when listing flashcards due for a project.
- **Mitigation**: Pass the active `projectId` and `documentId` in the body payload when calling `/api/generate_flashcards` from `FlashcardReviewModal.jsx`.

### [Medium] Challenge 5: Concept Map and Smart Notes Do Not Persist Artifacts
- **Assumption challenged**: Generating concept maps and smart notes saves them in the database as artifacts.
- **Attack scenario**: Unlike `generate_quiz` or `generate_study_plan`, the `/api/generate_map` and `/api/generate_notes` endpoints do not accept the `db` session and do not call `crud.create_artifact`.
- **Blast radius**: Medium. Concept maps and smart notes are never saved, making the "Tóm tắt Artifact" sidebar list unable to display them.
- **Mitigation**: Update `/api/generate_map` and `/api/generate_notes` endpoints to accept the database session and call `crud.create_artifact` to save the results.

### [Medium] Challenge 6: Owner Hidden in Collaboration Members List
- **Assumption challenged**: The active members list shows the project owner alongside invited members.
- **Attack scenario**: In `ProjectCollaborationModal.jsx`, the logic hides the owner row if there is at least one active member in `activeMembers` that is not `"owner@local.app"`.
- **Blast radius**: Medium. When a user invites another classmate, the project owner disappears from the list of active members in the UI.
- **Mitigation**: Keep the owner row visible in the collaboration modal by always rendering the owner independently of the dynamic `activeMembers` list.

### [Low] Challenge 7: Missing Email Format Validation on Project Invites
- **Assumption challenged**: Project invitation emails must be in a valid format.
- **Attack scenario**: A user invites an arbitrary string like `not-an-email-at-all` to the project. The backend accepts it and inserts it into the database.
- **Blast radius**: Low. Database becomes polluted with malformed invite emails.
- **Mitigation**: Use Pydantic's `EmailStr` in the backend `ProjectInviteReq` schema or add validation regex before committing to the DB.

---

## Stress Test Results

- **Create Exam with Document ID but no page ranges** → Expected: Quiz generated from document content → Actual: Quiz generated from empty/metadata fallback string → **FAIL**
- **Create Study Plan with Document ID** → Expected: Study plan generated from document content → Actual: Study plan generated from empty/metadata fallback string → **FAIL**
- **Generate Concept Map** → Expected: Concept map generated and saved to DB artifacts → Actual: Map generated but no artifact created in DB → **FAIL**
- **Project Invite with invalid email** → Expected: Validation failure (422) → Actual: Accepted with status `Invited successfully` → **FAIL**

---

## Unchallenged Areas

- **E2E test environment reliability** — Not challenged as the E2E test runner successfully starts the actual FastAPI backend server on a local port, performs HTTP integrations, and verifies DB entities directly against the SQLite database. There are no mocks or stubbed tests.
