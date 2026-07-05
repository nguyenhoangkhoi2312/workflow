# Milestone 3 Explorer Analysis: React Codebase Context Extraction & Integration

This report details the investigation of the React codebase for Milestone 3, focusing on path checks, modal context extraction, document API filtering, and chat history syncing for both **Project** (`/project/:id`) and **Standalone Document** (`/document/:id`) views.

---

## 1. Sidebar Path Checks: `AppLayout.jsx` and `Sidebar.jsx`

### Current Behavior & Determination
- **`src/components/layout/AppLayout.jsx`**:
  Determines whether to show the detailed `ProjectStudioSidebar` or the generic `StudioSidebar` using:
  ```javascript
  const isDocumentView = location.pathname.startsWith('/document/');
  ```
  It then conditionally renders the sidebar using:
  ```javascript
  {isDocumentView ? <ProjectStudioSidebar selectedPersona={selectedPersona} setSelectedPersona={setSelectedPersona} /> : <StudioSidebar />}
  ```
  Consequently, on a `/project/:id` path, `isDocumentView` is `false`, and the app incorrectly displays the generic `StudioSidebar` instead of `ProjectStudioSidebar`.
  
- **`src/components/layout/Sidebar.jsx`**:
  Determines the detail/workspace view state using:
  ```javascript
  const isDocumentView = location.pathname.startsWith('/document/') || location.pathname.startsWith('/project/');
  ```
  It attempts to get the project ID using `useParams()` at the top-level layout scope:
  ```javascript
  const { id: routeProjectId } = useParams();
  ```
  However, because `Sidebar` is rendered outside the nested child routes in the React Router tree (defined at the root `/` level layout in `App.jsx`), `useParams()` does not resolve nested route params like `:id` and returns `undefined`. Thus, active project navigation highlighting (`isActive = isDocumentView && routeProjectId === String(project.id)`) fails.

### Proposed Modifications
To align both layouts and ensure proper sidebar selection and active state tracking:
1. **In `AppLayout.jsx`**, update `isDocumentView` to check both `/document/` and `/project/` prefixes (matching `Sidebar.jsx`'s definition or rename it to `isWorkspaceView`):
   ```javascript
   const isWorkspaceView = location.pathname.startsWith('/document/') || location.pathname.startsWith('/project/');
   ```
   Render `ProjectStudioSidebar` when `isWorkspaceView` is `true`:
   ```javascript
   {isWorkspaceView ? <ProjectStudioSidebar selectedPersona={selectedPersona} setSelectedPersona={setSelectedPersona} /> : <StudioSidebar />}
   ```
2. **In `Sidebar.jsx`**, replace the unreliable `useParams()` check with manual URL pathname parsing:
   ```javascript
   const match = location.pathname.match(/^\/(project|document)\/([^/]+)/);
   const routeProjectId = match && match[1] === 'project' ? match[2] : null;
   ```
   This ensures that the correct project folder is highlighted when active.

---

## 2. Modals Context Extraction & Resolution Strategy

We examined seven modals under `src/components/modals/`. The current context resolution logic and required changes for each are documented below:

| Modal File | Current Extraction Logic | Limitations / Bug | Required Code Modification |
|---|---|---|---|
| **`TakeQuizModal.jsx`** | Fetches all documents using `/api/documents`. Extracts the document ID by parsing the hash for `#/document/:id`: `window.location.hash.match(/#\/document\/(\d+)/)` | 1. Queries all documents globally.<br>2. Completely ignores project context (`#/project/:id`).<br>3. Cannot resolve document context under a project. | Update `useEffect` to extract both `docId` and `projId` from the location hash, query `/api/documents?project_id=projId` if a project context exists, and resolve the active document (falling back to `sessionStorage`'s `active_document_id`). |
| **`SmartNotesModal.jsx`** | Fetches all documents. Extracts the document ID by matching `#/document/:id` in `window.location.hash`. | Same as above. | Apply identical active document resolution strategy as `TakeQuizModal.jsx` (shown in detail below). |
| **`ConceptMapModal.jsx`** | Fetches all documents. Extracts the document ID by matching `#/document/:id` in `window.location.hash`. | Same as above. | Apply identical active document resolution strategy. |
| **`FlashcardReviewModal.jsx`** | Fetches all documents. Extracts the document ID by matching `#/document/:id` in `window.location.hash`. | Same as above. | Apply identical active document resolution strategy. |
| **`StudyPlanModal.jsx`** | Fetches all documents. Extracts the document ID by matching `#/document/:id` in `window.location.hash`. | Same as above. | Apply identical active document resolution strategy. |
| **`StudyDocProgressModal.jsx`** | Fetches all documents. Extracts the document ID by matching `#/document/:id` in `window.location.hash`. | Same as above. | Apply identical active document resolution strategy. |
| **`DueFlashcardModal.jsx`** | Fetches all due flashcards globally using `GET /api/flashcards/due`. No project/document context extraction. | Users review cards from all documents/projects mixed together rather than in the active workspace context. | Parse `docId` and `projId` from the location hash. Append context query parameters to the endpoint: `http://127.0.0.1:8000/api/flashcards/due?project_id=...&document_id=...` depending on active context. |

### Concrete Modal Update Snippet (Active Document Resolution)
In `TakeQuizModal`, `SmartNotesModal`, `ConceptMapModal`, `FlashcardReviewModal`, `StudyPlanModal`, and `StudyDocProgressModal`, replace the document fetching and active document selection logic with this unified resolution hook/logic:

```javascript
// Within useEffect for modal opening
const matchDoc = window.location.hash.match(/#\/document\/([^/]+)/);
const matchProj = window.location.hash.match(/#\/project\/([^/]+)/);
const docId = matchDoc ? parseInt(matchDoc[1]) : null;
const projId = matchProj ? parseInt(matchProj[1]) : null;

let url = 'http://127.0.0.1:8000/api/documents';
if (projId) {
  url += `?project_id=${projId}`;
}

fetch(url)
  .then(res => res.json())
  .then(data => {
    setDocuments(data.documents);
    if (data.documents && data.documents.length > 0) {
      let doc = data.documents[data.documents.length - 1]; // default latest
      if (docId) {
        const found = data.documents.find(d => d.id === docId);
        if (found) doc = found;
      } else {
        // Retrieve the document user is viewing currently from session storage
        const storedId = sessionStorage.getItem('active_document_id');
        if (storedId) {
          const found = data.documents.find(d => String(d.id) === String(storedId));
          if (found) doc = found;
        }
      }
      setActiveDoc(doc);
      // For modals like ConceptMap / Flashcards, trigger generation
      if (typeof generateMap === 'function') generateMap(doc.content);
      if (typeof loadCards === 'function') loadCards(doc.content);
    } else {
      setError("Chưa có tài liệu trong dự án này.");
    }
  });
```

---

## 3. Document Viewer API Filtering: `DocumentViewer.jsx`

In a project context (`/project/:id`), we must scope the documents retrieved by the main viewer to prevent documents from other projects from showing.

### Implementation Strategy
1. **Detect Route Context**:
   Determine whether the route is a project using:
   ```javascript
   const isProjectRoute = location.pathname.startsWith('/project/');
   ```
2. **Retrieve Filtered Documents**:
   Modify the `fetchDocuments` side-effect to depend on `[id, isProjectRoute]` and construct the API request dynamically:
   ```javascript
   useEffect(() => {
     const fetchDocuments = async () => {
       try {
         let url = 'http://127.0.0.1:8000/api/documents';
         if (isProjectRoute && id) {
           url += `?project_id=${id}`;
         }
         const response = await fetch(url);
         const data = await response.json();
         setDocuments(data.documents);
         
         // Select the appropriate active document
         if (data.documents.length > 0) {
           if (!isProjectRoute && id) {
             const matchedDoc = data.documents.find(d => String(d.id) === String(id));
             setActiveDocId(matchedDoc ? matchedDoc.id : data.documents[data.documents.length - 1].id);
           } else {
             // Default to the last document in the project/list
             setActiveDocId(data.documents[data.documents.length - 1].id);
           }
         } else {
           setActiveDocId(null);
         }
       } catch (err) {
         console.error("Failed to fetch documents", err);
       }
     };
     fetchDocuments();
   }, [id, isProjectRoute]);
   ```
3. **Persist the Active Document**:
   Store the active document ID in `sessionStorage` whenever it changes, enabling other components (like modals and sidebars) to sync seamlessly:
   ```javascript
   useEffect(() => {
     if (activeDocId) {
       sessionStorage.setItem('active_document_id', activeDocId);
     }
   }, [activeDocId]);
   ```

---

## 4. Chat History Loading & Saving in `DocumentViewer.jsx`

Currently, chat history is not persistent in the frontend; the `messages` array starts empty and resets on mount. The backend, however, provides dedicated endpoints for fetching history and automatically saves chat messages when `project_id` or `document_id` is supplied to `POST /api/chat`.

### Implementation Strategy

1. **Load Chat History on View / Context Change**:
   Add a `useEffect` hook to load historical messages based on the active route view:
   ```javascript
   useEffect(() => {
     const fetchChatHistory = async () => {
       if (!id) {
         setMessages([]);
         return;
       }
       try {
         const url = isProjectRoute 
           ? `http://127.0.0.1:8000/api/projects/${id}/messages`
           : `http://127.0.0.1:8000/api/documents/${id}/messages`;
           
         const response = await fetch(url);
         if (response.ok) {
           const data = await response.json();
           const formatted = data.messages.map(m => ({
             role: m.role,
             text: m.content
           }));
           setMessages(formatted);
         }
       } catch (err) {
         console.error("Failed to load chat history", err);
       }
     };
     fetchChatHistory();
   }, [id, isProjectRoute, activeDocId]);
   ```

2. **Save Chat Messages with Correct Context**:
   Update `sendMessage` to pass the correct identifiers in the body payload to the `POST /api/chat` request:
   ```javascript
   const sendMessage = async (text) => {
     const content = (text ?? input).trim();
     if (!content || isTyping) return;
     setInput('');
     setMessages(prev => [...prev, { role: 'user', text: content }]);
     setIsTyping(true);
     
     // Construct the contextual payload
     const payload = {
       message: content,
       context: activeDoc ? activeDoc.content.slice(0, 6000) : '',
       persona: selectedPersona
     };
     
     if (isProjectRoute && id) {
       payload.project_id = Number(id);
       if (activeDocId) {
         payload.document_id = Number(activeDocId);
       }
     } else if (!isProjectRoute && id) {
       payload.document_id = Number(id);
       if (activeDoc && activeDoc.project_id) {
         payload.project_id = Number(activeDoc.project_id);
       }
     }
     
     try {
       const response = await fetch('http://127.0.0.1:8000/api/chat', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(payload)
       });
       const data = await response.json();
       setMessages(prev => [...prev, { role: 'assistant', text: data.response || '...' }]);
     } catch (err) {
       console.error(err);
       setMessages(prev => [...prev, { role: 'assistant', text: '⚠️ Không kết nối được tới máy chủ.' }]);
     } finally {
       setIsTyping(false);
     }
   };
   ```

---
*End of Report*
