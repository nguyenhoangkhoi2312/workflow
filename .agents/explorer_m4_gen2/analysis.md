# Codebase Exploration Report - Milestone 4 (Dead UI Implementation)

## Executive Summary
This report analyzes the front-end modals, API connection patterns, user tiering mechanisms, and E2E testing infrastructure of the application to guide the implementation of Milestone 4. Key findings include two completely dead/unmounted modals (`CreateExamModal.jsx` and `CreateStudyDocModal.jsx`), a disabled collaboration feature for standalone document contexts in `ProjectCollaborationModal.jsx`, and a missing file upload handler in `UploadSourcesModal.jsx`. 

---

## 1. Analysis of the 6 Modal Components

### 1. `src/components/modals/PricingModal.jsx`
* **Current State**: Fully functional. It displays the free and pro tier features.
* **Usage**: Imported and rendered in `Topbar.jsx`.
* **Action Flow**: When clicking "Nâng cấp ngay", it executes `handleUpgrade()`, which:
  1. Reads the current user's email from `localStorage` (`workflow_user`).
  2. Sends a POST request to `/api/user/upgrade`.
  3. Updates the `status` of the user object in `localStorage` to `premium`.
  4. Transitions the modal UI to a success state.

### 2. `src/components/modals/UploadSourcesModal.jsx`
* **Current State**: Partially functional.
* **Usage**: Imported and rendered in `ProjectStudioSidebar.jsx` (within a project context).
* **Action Flow**:
  * **Link Addition**: The text input for links (YouTube/web URLs) is wired to a POST fetch request targeting `http://127.0.0.1:8000/api/documents/url` with the `project_id`.
  * **File Upload**: The drag-and-drop file upload area is a **dead UI element**. It has no `<input type="file">` element, no event handlers for drag-over or drop, and no upload function implementation.

### 3. `src/components/modals/UploadModal.jsx`
* **Current State**: Functional for standalone uploads.
* **Usage**: Imported and rendered in `StudioSidebar.jsx` (the general, non-project workspace view).
* **Action Flow**: Allows selecting a file (`.pdf`, `.docx`, `.txt`) and displays mock classification fields (School, Major, Course, etc.). Clicking "Upload" sends a POST request with `FormData` containing the file to `http://127.0.0.1:8000/api/documents/upload`.
* **Issue**: It does not take a `projectId` prop or send it to the backend. It only uploads files as standalone documents.

### 4. `src/components/modals/CreateExamModal.jsx`
* **Current State**: **Completely dead/unwired UI**.
* **Usage**: Not imported or rendered anywhere in the application.
* **Action Flow**: The "Tạo đề thi" button is hardcoded with `cursor: 'not-allowed'` and `backgroundColor: '#9CA3AF'` and has no `onClick` handler. The file upload button is also a dead visual element.

### 5. `src/components/modals/CreateStudyDocModal.jsx`
* **Current State**: **Completely dead/unwired UI**.
* **Usage**: Not imported or rendered anywhere in the application.
* **Action Flow**: The "Tạo tài liệu" button is disabled via styling (`cursor: 'not-allowed'`) and has no click handler.

### 6. `src/components/modals/ProjectCollaborationModal.jsx`
* **Current State**: Functional for projects, but **broken for standalone documents**.
* **Usage**: Imported and rendered in `Topbar.jsx` and `DocumentViewer.jsx`.
* **Issue**: While the backend endpoints support both projects and standalone documents (`/api/projects/{id}/invite` vs `/api/documents/{id}/invite`), the React JSX strictly disables inputs and buttons if `projectId` is missing:
  * `disabled={!projectId}` on inputs and buttons (lines 127, 134, 144).
  * This prevents users from inviting collaborators in standalone document contexts.

---

## 2. Frontend Network/API Request Patterns

* **Standard Framework**: The frontend utilizes native browser `fetch` calls. No global Axios instance is configured.
* **Base URL Determination**: In `src/utils/api.js`, the base URL is determined dynamically:
  ```javascript
  const API_BASE = window.location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';
  ```
  However, throughout the components (e.g., `UploadModal.jsx`, `UploadSourcesModal.jsx`, `ProjectCollaborationModal.jsx`), base URLs are hardcoded as `http://127.0.0.1:8000`.
* **Headers & Authentication**:
  * Requests that send JSON use standard headers: `{'Content-Type': 'application/json'}`.
  * In `src/utils/api.js`, `getHeaders()` fetches `gemini_api_key` from `localStorage` and appends it as the `X-API-Key` header.
  * The user's active session is loaded from `localStorage.getItem('workflow_user')`.

---

## 3. Backend User Tiers and Mock Payment Logic

* **Database Schema**: The `User` model in `backend/db/models.py` defines status as:
  ```python
  status = Column(String, default="free")
  ```
* **Upgrade Endpoint**: In `backend/main.py`, a POST endpoint is exposed to set a user's status to `"premium"`:
  ```python
  @app.post("/api/user/upgrade")
  def upgrade_user(req: UpgradeRequest, db: Session = Depends(get_db)):
      db_user = db.query(models.User).filter(models.User.email == req.email).first()
      if not db_user:
          db_user = models.User(email=req.email, name=req.email.split('@')[0], status="premium")
          db.add(db_user)
      else:
          db_user.status = "premium"
      db.commit()
      db.refresh(db_user)
      return {"status": "premium", "email": req.email}
  ```
* **User Session State**:
  * Stored under the `localStorage` key `workflow_user`.
  * Object structure: `{ name: "...", email: "...", picture: "...", sub: "...", status: "premium" | "free" }`.

---

## 4. E2E Test Suite details

* **Test Suite Script**: `run_e2e_tests.py` is the orchestrator file.
* **Execution Command**:
  ```bash
  python3 run_e2e_tests.py
  ```
* **Script Behavior**:
  1. Checks if the backend server is running on `127.0.0.1:8000`.
  2. Spawns `uvicorn main:app` using Python virtual environment interpreter if the server is offline.
  3. Executes `pytest tests/e2e --junitxml=tests_result.xml -v`.
  4. Parses results from `tests_result.xml` and writes `TEST_INFRA.md` and `TEST_READY.md`.
  5. Tears down the background server if it spawned it.

---

## 5. Detailed Analysis and Proposed Changes for Modal Implementation

### 1. `src/components/modals/ProjectCollaborationModal.jsx`
* **Change Goal**: Enable collaboration invites in standalone document workspaces.
* **Proposed Diff**:
  ```diff
  @@ -124,3 +124,3 @@
                   onChange={e => setEmail(e.target.value)}
                   style={{ flex: 1, padding: '10px 16px', borderRadius: '12px', border: '1px solid #E5E7EB', fontSize: '0.875rem', outline: 'none' }}
  -                disabled={!projectId}
  +                disabled={!projectId && !documentId}
                 />
  @@ -131,3 +131,3 @@
                     onChange={e => setRole(e.target.value)}
  -                  style={{ width: '100%', padding: '10px 32px 10px 16px', borderRadius: '12px', border: '1px solid #E5E7EB', fontSize: '0.875rem', outline: 'none', appearance: 'none', backgroundColor: 'white', cursor: !projectId ? 'not-allowed' : 'pointer', fontWeight: 600, color: '#374151' }}
  -                  disabled={!projectId}
  +                  style={{ width: '100%', padding: '10px 32px 10px 16px', borderRadius: '12px', border: '1px solid #E5E7EB', fontSize: '0.875rem', outline: 'none', appearance: 'none', backgroundColor: 'white', cursor: (!projectId && !documentId) ? 'not-allowed' : 'pointer', fontWeight: 600, color: '#374151' }}
  +                  disabled={!projectId && !documentId}
                   >
  @@ -141,3 +141,3 @@
                 <button 
  -                onClick={handleInvite}
  -                disabled={isInviting || !email || !projectId}
  -                style={{ 
  -                  padding: '0 20px', borderRadius: '12px', border: 'none', 
  -                  backgroundColor: (!email || !projectId) ? '#D1D5DB' : 'var(--brand-primary)', color: 'white', 
  -                  fontWeight: 600, fontSize: '0.875rem', cursor: (!email || !projectId) ? 'not-allowed' : 'pointer',
  +                onClick={handleInvite}
  +                disabled={isInviting || !email || (!projectId && !documentId)}
  +                style={{ 
  +                  padding: '0 20px', borderRadius: '12px', border: 'none', 
  +                  backgroundColor: (!email || (!projectId && !documentId)) ? '#D1D5DB' : 'var(--brand-primary)', color: 'white', 
  +                  fontWeight: 600, fontSize: '0.875rem', cursor: (!email || (!projectId && !documentId)) ? 'not-allowed' : 'pointer',
                     display: 'flex', alignItems: 'center', gap: '8px', transition: 'all 0.2s'
  ```

### 2. `src/components/modals/UploadSourcesModal.jsx`
* **Change Goal**: Enable file uploading in the drag-and-drop workspace UI component.
* **Proposed Modifications**:
  1. Add a hidden `<input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileSelect} />` inside the modal.
  2. Implement `handleFileSelect` and drag/drop event triggers.
  3. Implement `uploadFile`:
     ```javascript
     const uploadFile = async (selectedFile) => {
       setIsUploading(true);
       try {
         const formData = new FormData();
         formData.append('file', selectedFile);
         if (projectId) formData.append('project_id', projectId);
         
         const res = await fetch('http://127.0.0.1:8000/api/documents/upload', {
           method: 'POST',
           body: formData,
         });
         if (res.ok) {
           setUploadStatus('success');
         } else {
           setUploadStatus('error');
         }
       } catch (err) {
         setUploadStatus('error');
       } finally {
         setIsUploading(false);
       }
     };
     ```

### 3. `src/components/modals/UploadModal.jsx`
* **Change Goal**: Make `UploadModal.jsx` compatible with project contexts by accepting `projectId` as an optional prop and forwarding it to the backend.
* **Proposed Modifications**:
  1. Update component signature: `const UploadModal = ({ isOpen, onClose, onUpload, projectId }) => {`
  2. Inside `handleSubmit()`, add `projectId` to the `FormData` if it exists:
     ```javascript
     if (projectId) {
       formData.append('project_id', projectId);
     }
     ```

### 4. `src/components/modals/CreateExamModal.jsx`
* **Change Goal**: Wire the Exam generation configuration form to the backend endpoint `/api/generate_quiz` and make it active.
* **Proposed Modifications**:
  1. Accept props: `({ isOpen, onClose, projectId, documentId, onSuccess })`.
  2. Create states for options: `title`, `description`, `timeLimit`, `numberOfQuestions`, `difficulty`, `language`, `pastedText`, and `selectedFile`.
  3. Add file inputs and drag-drop handlers for files.
  4. Implement `handleCreateQuiz`:
     ```javascript
     const handleCreateQuiz = async () => {
       setIsLoading(true);
       try {
         let textContent = pastedText;
         
         // If a file was selected, upload it first to get text/doc representation, 
         // or send its text if read locally
         if (selectedFile) {
           const formData = new FormData();
           formData.append('file', selectedFile);
           if (projectId) formData.append('project_id', projectId);
           
           const uploadRes = await fetch('http://127.0.0.1:8000/api/documents/upload', {
             method: 'POST',
             body: formData
           });
           if (uploadRes.ok) {
             const docData = await uploadRes.json();
             // use docData.id
           }
         }
         
         const payload = {
           topic_or_text: textContent || `Generate exam: ${title}`,
           project_id: projectId ? parseInt(projectId) : null,
           document_id: documentId ? parseInt(documentId) : null,
         };
         
         const res = await fetch('http://127.0.0.1:8000/api/generate_quiz', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(payload)
         });
         
         if (res.ok) {
           if (onSuccess) onSuccess();
           onClose();
         }
       } catch (err) {
         console.error(err);
       } finally {
         setIsLoading(false);
       }
     };
     ```
  5. Replace the "Create Exam" click handler in sidebars to show `CreateExamModal` first instead of skipping directly to `TakeQuizModal`.

### 5. `src/components/modals/CreateStudyDocModal.jsx`
* **Change Goal**: Wire the study prep document configuration form to the backend endpoint `/api/generate_exam_prep` and make it active.
* **Proposed Modifications**:
  1. Accept props: `({ isOpen, onClose, projectId, documentId, onSuccess })`.
  2. Implement input fields binding state and file selection.
  3. Implement `handleCreateStudyDoc` which calls `POST http://127.0.0.1:8000/api/generate_exam_prep` with the source text, `project_id`, and `document_id`.
  4. Close modal and invoke `onSuccess` on success.
  5. In sidebars, bind the "Study Doc" button to trigger `CreateStudyDocModal` rather than skipping to `StudyDocProgressModal`.
