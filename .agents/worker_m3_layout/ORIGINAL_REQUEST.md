## 2026-06-28T09:33:08Z
You are the Milestone 3 Layout & Viewer Developer (worker).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/worker_m3_layout.

Your task is to fix routing layouts, document API filtering, and chat context sync in the React frontend:

1. **Fix `src/components/layout/AppLayout.jsx`**:
   - Update path checks to support both `/document/` and `/project/` path prefixes.
   - Render `ProjectStudioSidebar` (instead of `StudioSidebar`) when the path matches `/document/:id` or `/project/:id`.

2. **Fix `src/components/layout/Sidebar.jsx`**:
   - Extract the active project/workspace context by manually parsing `location.pathname` (using regex or substring) to correctly resolve the project/document ID, since `useParams()` does not resolve nested route params at this level.
   - Highlight the correct active project based on the resolved context.

3. **Fix `src/pages/DocumentViewer.jsx`**:
   - Filter documents by appending `?project_id=...` to the `/api/documents` fetch call when viewing a project context (`/project/:id`).
   - Store the active document ID in `sessionStorage` under `active_document_id` when it changes, to synchronize with modal context extraction.
   - Implement chat history loading on mount and context change by calling `GET /api/projects/:id/messages` (for projects) or `GET /api/documents/:id/messages` (for documents).
   - Update `sendMessage` to pass `project_id` and/or `document_id` to `POST /api/chat` depending on the active route view.

Refer to the Explorer Analysis at `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m3/analysis.md` for specific implementation details and snippets.

Run `npm run build` from the frontend directory to ensure the codebase builds and compiles without errors. Report your findings and results in your handoff report.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
