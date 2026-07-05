## 2026-06-28T09:35:07Z
You are the Milestone 3 Modals Context Developer (worker).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/worker_m3_modals.

Your task is to fix context resolution logic inside the following React modals to correctly support both `/document/:id` and `/project/:id` active route patterns:

1. **`src/components/modals/TakeQuizModal.jsx`**
2. **`src/components/modals/SmartNotesModal.jsx`**
3. **`src/components/modals/ConceptMapModal.jsx`**
4. **`src/components/modals/FlashcardReviewModal.jsx`**
5. **`src/components/modals/StudyPlanModal.jsx`**
6. **`src/components/modals/StudyDocProgressModal.jsx`**

For these 6 modals:
- Extract `docId` and `projId` from `window.location.hash` (match both `#\/document\/([^/]+)` and `#\/project\/([^/]+)`).
- Fetch documents from `http://127.0.0.1:8000/api/documents` (append `?project_id=projId` to the query if `projId` exists).
- Resolve the correct active document:
  - If `docId` is matched, find it in the fetched documents.
  - Else if `active_document_id` is set in `sessionStorage` (synced by `DocumentViewer`), fall back to finding that document.
  - Else fall back to the last/default document in the returned array.
  - Correctly set the active document state and trigger any related content loads/generation functions.

7. **`src/components/modals/DueFlashcardModal.jsx`**:
- Extract `docId` and `projId` from `window.location.hash`.
- Append context query params to the endpoint: `http://127.0.0.1:8000/api/flashcards/due?project_id=...&document_id=...` depending on active context (if `projId` exists, set `project_id`, if `docId` exists or if `active_document_id` is in `sessionStorage`, set `document_id`).

Refer to the Explorer Analysis at `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m3/analysis.md` for details.

Run `npm run build` from the frontend directory to ensure the codebase builds and compiles without errors. Report your findings and results in your handoff report.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
