# Original User Request

## Initial Request — 2026-06-28T16:39:43+07:00

You are the Milestone 4 (Dead UI Implementation) Sub-orchestrator (archetype: self).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/sub_orch_m4.
Your parent is 46ac9098-2da1-4b75-9ea3-afc667e125d1 (Project Orchestrator).

Your task is to implement Milestone 4:
1. Initialize SCOPE.md under your working directory to define your plan and tracking.
2. Bind the Pricing Modal:
   - Modify `src/components/modals/PricingModal.jsx` to replace `alert("Chức năng thanh toán đang được phát triển!")` with functional logic. For example, make a POST request to a mock payment endpoint or backend `POST /api/user/upgrade` to set the user status to "premium" (storing this in localStorage/user state), or show a payment success state/dialog without utilizing raw browser alerts.
3. Bind the Drag-and-drop & File Selection:
   - In `src/components/modals/UploadSourcesModal.jsx`, add a hidden `<input type="file">` ref-bound to the drag-and-drop box. Add `onClick` to the drop-box to trigger click on the file input. Add `onDragOver` and `onDrop` to handle file drops, and send the selected files via FormData POST to `/api/documents/upload`.
4. Bind Form Inputs and Submissions:
   - Bind inputs (Trường, Ngành, Môn học, etc.) in `src/components/modals/UploadModal.jsx` to states and include them in document upload payloads.
   - Bind form fields in `src/components/modals/CreateExamModal.jsx`. Remove `disabled` on the submit button. Implement a submit handler that calls the backend quiz generator `/api/generate_quiz` or exam prep generator `/api/generate_exam_prep` and successfully updates the active workspace artifacts.
   - Bind form fields in `src/components/modals/CreateStudyDocModal.jsx`. Remove `disabled` on the submit button. Implement a submit handler that calls `/api/generate_study_plan` or similar backend APIs and saves the new learning plan artifact.
5. Enable Standalone Document Collaboration:
   - Modify `src/components/modals/ProjectCollaborationModal.jsx`. Ensure that when `projectId` is missing but `documentId` (or hash document context) is present, the fields are NOT disabled and the invitation forms function correctly using the backend `/api/documents/{document_id}/invite` and `/api/documents/{document_id}/members` endpoints.
6. Verify your changes. Build the frontend (`npm run build`) and run E2E tests (`python run_e2e_tests.py`) to confirm that all UI clicks and integrations pass successfully.
7. Document all changes and verification test results in `handoff.md` and communicate completion back to the parent.

Ensure you spawn subagents (e.g. teamwork_preview_worker, teamwork_preview_challenger) to make code changes and verify. DO NOT write code yourself. Verbatim warning: DO NOT CHEAT. All implementations must be genuine.
