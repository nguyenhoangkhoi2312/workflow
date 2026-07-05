# Scope: Milestone 4 (Dead UI Implementation)

## Architecture
- React frontend components (Modals) located in `src/components/modals/` interacting with backend APIs.
- Backend routes (from request):
  - `POST /api/user/upgrade`
  - `POST /api/documents/upload`
  - `POST /api/generate_quiz` or `POST /api/generate_exam_prep`
  - `POST /api/generate_study_plan`
  - `POST /api/documents/{document_id}/invite` and `GET/POST /api/documents/{document_id}/members`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration & Planning | Explore the files to modify, existing APIs, current tests, and construct the detailed plan | None | DONE |
| 2 | Bind Pricing Modal | Modify `src/components/modals/PricingModal.jsx` to replace alert with upgrade API call/state | M1 | DONE |
| 3 | Bind Drag-and-drop & File Selection | Modify `src/components/modals/UploadSourcesModal.jsx` to add file input, bind ref, onClick, onDragOver, onDrop, and upload FormData | M1 | DONE |
| 4 | Bind Form Inputs and Submissions | Modify `UploadModal.jsx`, `CreateExamModal.jsx`, and `CreateStudyDocModal.jsx` to bind inputs and handle submissions | M1 | DONE |
| 5 | Enable Standalone Document Collaboration | Modify `ProjectCollaborationModal.jsx` to support missing projectId with fallback to documentId | M1 | DONE |
| 6 | Verification and E2E Tests | Run `npm run build` and `python run_e2e_tests.py` to verify all components and test suites pass | M2, M3, M4, M5 | DONE |

## Interface Contracts
- `POST /api/user/upgrade` -> request to set user status to premium
- `POST /api/documents/upload` -> FormData upload with files
- `POST /api/generate_quiz` or `/api/generate_exam_prep` -> generate quiz/exam prep artifacts
- `POST /api/generate_study_plan` -> generate study plan artifact
- `POST /api/documents/{document_id}/invite` and `GET/POST /api/documents/{document_id}/members` -> invite and query members for a standalone document context
