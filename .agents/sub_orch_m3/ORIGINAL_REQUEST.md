# Original User Request

## 2026-06-28T09:30:50Z

You are the Milestone 3 (Frontend Layout & Context Sync) Sub-orchestrator (archetype: self).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/sub_orch_m3.
Your parent is 46ac9098-2da1-4b75-9ea3-afc667e125d1 (Project Orchestrator).

Your task is to implement Milestone 3:
1. Initialize SCOPE.md under your working directory to define your plan and tracking.
2. Fix the routing layout bugs in the React frontend:
   - Fix `src/components/layout/AppLayout.jsx` and `src/components/layout/Sidebar.jsx` path checks. Ensure that opening a project view route `/project/:id` correctly loads and displays `ProjectStudioSidebar` and matches the project workspace layout rather than rendering the generic `StudioSidebar`.
   - Fix all modals (e.g. `TakeQuizModal.jsx`, `SmartNotesModal.jsx`, `ConceptMapModal.jsx`, `FlashcardReviewModal.jsx`, `StudyPlanModal.jsx`, `StudyDocProgressModal.jsx`, `DueFlashcardModal.jsx`) that parse the active context using a fragile URL hash match like `/document/:id`. Ensure they check the current route (both `/document/:id` and `/project/:id`) and resolve the correct active context (setting `project_id` and/or `document_id` appropriately).
3. Fix document listing and viewer filtering:
   - In project view page(s) (e.g. `src/pages/DocumentViewer.jsx`), filter the documents by appending `?project_id=...` to the `/api/documents` API request so that only the project's documents are displayed, rather than listing all documents globally.
4. Integrate chat history and message saving with context:
   - Ensure the chat interface in `DocumentViewer.jsx` saves and loads history with `project_id` or `document_id` depending on the active view context, preventing project chats from getting lost or defaulting to None.
5. Verify your changes. Build the frontend (`npm run build`) and verify it compiles without errors. Run any relevant E2E tests using `python run_e2e_tests.py` to verify that layout and context APIs function as expected.
6. Document your changes and test results in `handoff.md` and communicate completion back to the parent.

Ensure you spawn subagents (e.g. teamwork_preview_worker, teamwork_preview_challenger) to make code changes and verify. DO NOT write code yourself. Verbatim warning: DO NOT CHEAT. All implementations must be genuine.
