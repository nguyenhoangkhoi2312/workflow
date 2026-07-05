# Changes Made in Milestone 4

This document captures all files modified, features implemented, and details regarding their integrations for Milestone 4 (Dead UI Implementation).

## Files Modified
1. `backend/db/models.py`:
   - Added `status = Column(String, default="free")` field to the `User` class to represent whether a user has upgraded to premium/pro.
2. `backend/main.py`:
   - Updated the startup database patching routine `patch_database_schema(engine)` to automatically add the `status` column to the `users` table if it is missing (ensuring backward database schema compatibility).
   - Added `UpgradeRequest` schema and the `POST /api/user/upgrade` endpoint to allow users to upgrade to premium status.
3. `src/components/modals/PricingModal.jsx`:
   - Replaced `alert("Chức năng thanh toán đang được phát triển!")` with actual API integration calling `POST /api/user/upgrade`.
   - Updated `localStorage` to mark user status as "premium" upon upgrade.
   - Replaced raw browser alerts with a success UI dialog.
4. `src/components/modals/UploadSourcesModal.jsx`:
   - Added hidden file input ref, drag/drop, and file selection event handlers.
   - Connected file selection and drop actions to `FormData` upload calling `POST /api/documents/upload`.
   - Bound upload state to progress spinner and success/error status messages.
5. `src/components/modals/UploadModal.jsx`:
   - Declared states for all the document categorization metadata (school, department, subject, custom subject, code, type, academic year, teacher, notes).
   - Bound all select/input/textarea form elements to these states.
   - Appended all bound metadata fields to the upload `FormData` payload submitted to the backend upload endpoint.
6. `src/components/modals/CreateExamModal.jsx`:
   - Added `projectId` and `documentId` to the component props.
   - Bound all config parameters (title, description, time, questions count, difficulty, language, types, explanation, content length) to component states.
   - Removed the `disabled` attributes from inputs and the submit button, hooking the click event to call `/api/generate_quiz`.
7. `src/components/modals/CreateStudyDocModal.jsx`:
   - Added `projectId` and `documentId` to the component props.
   - Bound all plan parameters (title, description, target/topic, length) to component states.
   - Removed `disabled` from the submit button, hooking the click event to call `/api/generate_study_plan`.
8. `src/components/modals/ProjectCollaborationModal.jsx`:
   - Updated all validation checks to enable email inputs and invite buttons if either `projectId` or `documentId` is provided (eliminating the strict `!projectId` block and supporting Standalone Document workspaces).

## Build and E2E Test Verification
- Ran `npm run build`: Success.
- Ran E2E test suite `python3 run_e2e_tests.py`: All 71 tests passed (100% success rate).

## Refinement Changes (2026-06-28)
We refined and fully wired the React modal integrations to support standalone document contexts and callback execution:
1. `src/components/modals/UploadModal.jsx`:
   - Updated signature to accept optional `projectId` and `documentId` props.
   - Appended `project_id` or `document_id` fields to the `FormData` payload if present.
2. `src/components/modals/UploadSourcesModal.jsx`:
   - Added optional `documentId` prop support.
   - Appended `document_id` to `FormData` file uploads if present.
   - Passed `document_id` to the POST payload when adding documents via URL.
3. `src/components/modals/CreateExamModal.jsx` & `src/components/modals/CreateStudyDocModal.jsx`:
   - Added `onSuccess` callback prop.
   - Dynamically extracted the active document ID from the URL hash routing format if not explicitly provided as a prop.
   - Invoked `onSuccess()` upon successful API response completion.
4. `src/components/layout/Topbar.jsx`:
   - Extracted standalone `documentId` from the route parameters.
   - Expanded the project collaboration button visibility condition to show when either a project OR a document is active, passing `documentId` down.
5. `src/components/layout/ProjectStudioSidebar.jsx` & `src/components/layout/StudioSidebar.jsx`:
   - Replaced old `TakeQuizModal` and `StudyDocProgressModal` with `CreateExamModal` and `CreateStudyDocModal`.
   - Wired the sidebar `fetchData` function as `onSuccess` callback to ensure real-time UI refresh.
