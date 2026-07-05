# Handoff Report: Milestone 3 Explorer

## 1. Observation
We observed the following code behaviors and definitions in the workspace `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo`:
- **AppLayout.jsx (Line 13)**: `const isDocumentView = location.pathname.startsWith('/document/');` shows that it checks only for `/document/` prefix.
- **AppLayout.jsx (Line 41)**: `{isDocumentView ? <ProjectStudioSidebar selectedPersona={selectedPersona} setSelectedPersona={setSelectedPersona} /> : <StudioSidebar />}` renders `StudioSidebar` (the generic sidebar) when viewing projects.
- **Sidebar.jsx (Line 9-10)**: `const { id: routeProjectId } = useParams();` and `const isDocumentView = location.pathname.startsWith('/document/') || location.pathname.startsWith('/project/');` gets the path check right but useParams fails at layout level.
- **DocumentViewer.jsx (Lines 29-33)**: `const response = await fetch('http://127.0.0.1:8000/api/documents');` does not filter by project_id even if on `/project/:id` route, showing documents from other projects.
- **DocumentViewer.jsx (Lines 76-84)**: `fetch('http://127.0.0.1:8000/api/chat', ...)` does not send `project_id` or `document_id` to save chats, and there is no logic to load chat history from the backend.
- **Modals (e.g. TakeQuizModal.jsx, SmartNotesModal.jsx, ConceptMapModal.jsx, etc.)**:
  ```javascript
  const match = window.location.hash.match(/#\/document\/(\d+)/);
  ```
  This is used to determine active document context, ignoring `/project/:id` completely.
- **DueFlashcardModal.jsx (Line 30)**: `const response = await fetch('http://127.0.0.1:8000/api/flashcards/due');` fetches due cards globally without workspace-level constraints.

## 2. Logic Chain
1. Since `AppLayout.jsx` only checks `location.pathname.startsWith('/document/')` (Observation 1), it renders `StudioSidebar` when matching a `/project/:id` path (Observation 2). Expanding the prefix check resolves this.
2. Since `Sidebar.jsx` is rendered inside `AppLayout` (outside the nested router hierarchy containing `:id`), `useParams()` returns `undefined` (Observation 3). Parsing `location.pathname` manually with a regex resolves this cleanly.
3. Since `DocumentViewer.jsx` fetches `/api/documents` unconditionally without the `project_id` parameter (Observation 4), it lists all documents in the system instead of filtering them to the current project context. Appending `?project_id=...` based on route type resolves this.
4. Since `DocumentViewer.jsx`'s `sendMessage` does not provide `project_id` or `document_id` (Observation 5), chat messages are not stored in the database. Adding them to the payload and adding a `useEffect` history retrieval hook syncs the chats perfectly.
5. Since the modals use hash matching on `/document/:id` (Observation 6), they fail to extract context when on a project view. Enhancing the hash match parser to handle `/project/:id` and querying `?project_id=...` solves context resolution.
6. Since `DueFlashcardModal.jsx` calls `api/flashcards/due` globally (Observation 7), passing the parsed `project_id` and `document_id` parameters restricts the list of cards to be reviewed to the user's active context.

## 3. Caveats
- No caveats. We assume the backend continues running on port 8000.

## 4. Conclusion
The implementation strategy is clear and mapped out in `analysis.md` in detail. The explorer recommends:
1. Standardizing pathname checking and parsing across `AppLayout` and `Sidebar`.
2. Updating `useEffect` in all 7 modals to fetch documents by project context and match against local storage (`active_document_id`) or pathname.
3. Adding request payload attributes to `/api/chat` and a matching history fetching hook in `DocumentViewer.jsx`.

## 5. Verification Method
1. Start frontend and backend servers.
2. Navigate to `#/project/<id>` and verify that `ProjectStudioSidebar` is displayed (and not the generic `StudioSidebar`).
3. Click "Smart Notes", "Take Quiz", etc., inside a project view, and confirm that it resolves the active project document context correctly.
4. Review console network requests to ensure `GET /api/documents?project_id=...` and `GET /api/flashcards/due?project_id=...` are correctly sent.
5. Inspect chat history loading requests `GET /api/projects/{id}/messages` and database persistence.
