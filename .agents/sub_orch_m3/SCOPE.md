# Scope: Milestone 3 (Frontend Layout & Context Sync)

## Architecture
- **Routing & Layout**: The React frontend uses react-router-dom. `AppLayout.jsx` and `Sidebar.jsx` manage layout context and render sidebars based on active paths.
- **Modal Context**: Various study/review modals extract `document_id` and `project_id` from the URL or state to sync with backend APIs. They should dynamically handle both `/document/:id` and `/project/:id` active routes.
- **Document List Filtering**: `DocumentViewer.jsx` list views must filter documents belonging to a project by passing `project_id` query param to `/api/documents`.
- **Chat Context Sync**: The chat interface in `DocumentViewer.jsx` should sync messages with `project_id` or `document_id`.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Routing Layout | Fix path checks in `AppLayout.jsx` and `Sidebar.jsx` for `/project/:id` to show `ProjectStudioSidebar`. | None | DONE |
| 2 | Modal Context | Update study modals to resolve `project_id`/`document_id` correctly on both project/document routes. | None | DONE |
| 3 | Document Filtering | Update `DocumentViewer.jsx` (and related project view pages) to filter documents by project_id. | None | DONE |
| 4 | Chat History Context | Update chat context in `DocumentViewer.jsx` to load/save chat history using project_id or document_id. | None | DONE |
| 5 | End-to-End Verification | Build frontend, run compiler checks, and verify all routing/sync behavior passes via tests. | 1, 2, 3, 4 | DONE |

## Interface Contracts
- **Documents API**: `/api/documents?project_id=<id>` returns only documents matching the specified project ID.
- **Chat API**: Saves/loads messages scoped by `project_id` or `document_id` parameter.
- **Frontend Route Patterns**:
  - Project Studio View: `/project/:id` (renders project-level workspace)
  - Document Studio View: `/document/:id` (renders document-level workspace)
