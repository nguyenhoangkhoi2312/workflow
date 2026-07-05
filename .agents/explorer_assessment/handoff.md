# Codebase Auditor Handoff Report

## 1. Observation

### A. Non-functional / Stubbed Frontend Elements
1. **PricingModal Upgrade Button**:
   - File: `src/components/modals/PricingModal.jsx` (Line 68)
   - Code: `onClick={() => alert("Chức năng thanh toán đang được phát triển!")}`
2. **UploadSourcesModal Drag & Drop/Click Zone**:
   - File: `src/components/modals/UploadSourcesModal.jsx` (Lines 35–39)
   - Code:
     ```jsx
     <div style={{ border: '2px dashed var(--border-medium)', borderRadius: '16px', padding: '48px 24px', textAlign: 'center', cursor: 'pointer', backgroundColor: 'white', marginBottom: '24px' }}>
       <Upload size={24} color="var(--text-secondary)" style={{ margin: '0 auto 12px' }} />
       <div style={{ fontWeight: 700, color: '#1B2A4E', marginBottom: '8px' }}>Drag files here or click to choose</div>
       <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>PDF, DOCX, PNG, JPG, WebP, MP4, MP3...</div>
     </div>
     ```
     *Observation*: This div has no `onClick`, `onDragOver`, or `onDrop` handlers, and there is no hidden `<input type="file">`. Clicking it does nothing.
3. **UploadSourcesModal API Mismatch**:
   - File: `src/components/modals/UploadSourcesModal.jsx` (Line 60)
   - Code: `const res = await fetch('http://127.0.0.1:8000/api/documents/url', {`
   - *Observation*: The backend `/api/documents/ingest_url` expects URL payloads, while the frontend calls `/api/documents/url`, leading to a 404 response.
4. **UploadModal Form Submission Decorative Fields**:
   - File: `src/components/modals/UploadModal.jsx` (Lines 16–37, 80–141)
   - *Observation*: `handleSubmit` only appends the `file` to `FormData` and sends it to `/api/documents/upload`. All the dropdowns and text inputs (Trường, Ngành, Môn học, Giảng viên, Ghi chú...) have no state variables attached and are completely decorative.
5. **CreateExamModal Submit Button & Form**:
   - File: `src/components/modals/CreateExamModal.jsx` (Lines 33–141, 149–151)
   - Code:
     ```jsx
     <button style={{ padding: '12px 32px', backgroundColor: '#9CA3AF', border: 'none', borderRadius: '24px', fontWeight: 600, color: 'white', cursor: 'not-allowed' }}>
       Tạo đề thi
     </button>
     ```
     *Observation*: The submit button is hardcoded as `disabled` with `cursor: 'not-allowed'` and has no `onClick`. The entire form has no state hook bindings or handlers.
6. **CreateStudyDocModal Submit Button & Form**:
   - File: `src/components/modals/CreateStudyDocModal.jsx` (Lines 31–68, 78–80)
   - Code:
     ```jsx
     <button style={{ padding: '12px 32px', backgroundColor: '#B890A3', border: 'none', borderRadius: '24px', fontWeight: 600, color: 'white', cursor: 'not-allowed' }}>
       Tạo tài liệu
     </button>
     ```
     *Observation*: Similarly, the submit button is styled as disabled with no handler, and form fields are decorative only.
7. **Unused / Dead Code (GenerateQuizModal)**:
   - File: `src/components/modals/GenerateQuizModal.jsx`
   - *Observation*: The component is defined but is never imported or rendered anywhere in the application.
8. **Unused API Utility Functions**:
   - File: `src/utils/api.js`
   - *Observation*: Functions such as `askAssistant`, `generateFlashcards`, `generatePath`, `generateQuiz`, `generateNotes`, and `getSuggestions` are defined but never imported. Instead, pages make inline HTTP `fetch` requests.

### B. Failing / Mocked Backend Features
1. **Mock Path Fallback in `/api/generate_path`**:
   - File: `backend/main.py` (Lines 742–770)
   - Code:
     ```python
     if not current_key or current_key.startswith("AQ"):
         return {
             "title": f"Learning Path: {request.topic}",
             "description": f"An algorithmically generated structured path...",
             "modules": [ ... ]
         }
     ```
     *Observation*: If no API key is set, or if the key starts with `"AQ"`, the endpoint immediately returns hardcoded mock modules instead of generating dynamic content.
2. **Extremely Heuristic Suggestions Fallback in `/api/suggestions`**:
   - File: `backend/main.py` (Lines 1083–1098)
   - *Observation*: If no API key is provided, it does a simple word length filter and returns generic categories ("General Study", "Reading Comprehension", "Vocabulary").
3. **No Offline Fallback for Exam Prep / Study Plan**:
   - File: `backend/main.py` (Lines 925–928, 946–949)
   - *Observation*: If `current_key` is not provided, both `/api/generate_exam_prep` and `/api/generate_study_plan` immediately raise an HTTP 400/500 error.
4. **Mock Project Members**:
   - File: `backend/main.py` (Lines 338–346, 424–427)
   - Code: `members_data = [{"email": "owner@local.app", "role": "owner"}]`
   - *Observation*: Under `/api/projects/{project_id}/members` and `/api/documents/{document_id}/members`, if the database lists no members, a mock owner profile is returned.
5. **Offline Concept Map Lacks Definitions and Formulas**:
   - File: `backend/nlp/concept_map.py` (Lines 77–81)
   - Code: `formatted_nodes = [{"id": n, "label": n.title()} for n in nodes]`
   - *Observation*: The database schema `ConceptNodeSchema` expects `id`, `label`, `definition`, and `formula`. The offline generator only provides `id` and `label`. Consequently, clicking concept nodes in offline maps always displays "Không có định nghĩa chi tiết."

### C. Violations of User Rule: "Handle Project vs. Standalone Document Contexts"
1. **Database Schema Constraints**:
   - File: `backend/db/models.py` (Lines 125–132, 134–144)
   - Code:
     ```python
     class ChatMessage(Base):
         __tablename__ = "chat_messages"
         id = Column(Integer, primary_key=True, index=True)
         project_id = Column(Integer, ForeignKey("projects.id")) # No document_id!
         ...
     class Artifact(Base):
         __tablename__ = "artifacts"
         id = Column(Integer, primary_key=True, index=True)
         project_id = Column(Integer, ForeignKey("projects.id")) # No document_id!
         ...
     ```
     *Observation*: Both tables lack a `document_id` column, meaning chat messages and generated artifacts cannot be natively stored for standalone documents.
   - File: `backend/db/models.py` (Lines 6–18)
     *Observation*: The `Flashcard` table lacks both `project_id` and `document_id` columns, rendering flashcards global across all users/projects/documents.
2. **Backend/CRUD Inconsistencies**:
   - File: `backend/db/crud.py` (Lines 126–134)
   - Code: `create_artifact` and `get_artifacts` only accept `project_id`.
   - File: `backend/main.py` (Lines 885–887, 922–924, 943–945)
   - Code: Artifacts (quizzes, exam prep sheets, study plans) are only saved if `request.project_id` is present. In Standalone Document mode, they are completely ephemeral and not persisted.
3. **Sidebar Mismatch Layout Bug**:
   - File: `src/components/layout/AppLayout.jsx` (Line 13)
   - Code: `const isDocumentView = location.pathname.startsWith('/document/');`
   - File: `src/components/layout/Sidebar.jsx` (Line 10)
   - Code: `const isDocumentView = location.pathname.startsWith('/document/') || location.pathname.startsWith('/project/');`
   - *Observation*: Because `AppLayout` checks only `/document/` while `Sidebar` checks both, viewing `/project/:id` renders the generic `StudioSidebar` instead of `ProjectStudioSidebar`, breaking the workspace layout and hiding project roadmaps/artifacts.
4. **Global Document Fetching inside Projects**:
   - File: `src/pages/DocumentViewer.jsx` (Lines 29–30)
   - Code: `const response = await fetch('http://127.0.0.1:8000/api/documents');`
   - *Observation*: Bypasses passing `project_id` to `/api/documents`. Consequently, the project viewer displays every uploaded document globally rather than filtering by project documents.
5. **No Chat History Persistence**:
   - File: `src/pages/DocumentViewer.jsx` (Lines 76–84)
   - *Observation*: The chat fetch request does not specify `project_id` in the body payload, so `request.project_id` defaults to `None` in the backend. As a result, project chats are never saved in the database, and the UI never loads past history.
6. **Modal Hash Parsing Context Bugs**:
   - Files:
     - `src/components/modals/TakeQuizModal.jsx` (Lines 23–25)
     - `src/components/modals/SmartNotesModal.jsx` (Lines 37–39)
     - `src/components/modals/ConceptMapModal.jsx` (Lines 60–62)
     - `src/components/modals/FlashcardReviewModal.jsx` (Lines 27–29)
     - `src/components/modals/StudyPlanModal.jsx` (Lines 33–35)
     - `src/components/modals/StudyDocProgressModal.jsx` (Lines 32–34)
   - Code: `const match = window.location.hash.match(/#\/document\/(\d+)/);`
   - *Observation*: These modals parse the active document ID by regex-matching the URL hash. If the user is on the `/project/:id` route, the match returns null, forcing the modals to default to the globally last-uploaded document, exposing data across unrelated projects/documents.
7. **Collaboration Invite Form Disabled in Document Context**:
   - File: `src/components/modals/ProjectCollaborationModal.jsx` (Lines 127, 134, 144)
   - Code: `disabled={!projectId}`
   - *Observation*: The invitation form fields are disabled if `projectId` is missing. This completely prevents users from adding collaborators to a Standalone Document, despite the backend exposing a `/api/documents/{document_id}/invite` endpoint.

### D. Build and Run Commands & Tests
1. **Starting Frontend**: `npm run dev` or `npm run electron:dev` (runs Vite dev server on port 5173).
2. **Starting Backend**: `./venv/bin/python main.py` inside `backend/` directory (runs on port 8000).
3. **Status**: A backend server is currently already running and listening on port 8000.
4. **Build**: Frontend build succeeds via `npm run build`.
5. **Testing**: There are no unit or integration tests present for either the backend or the frontend. No testing frameworks (e.g., pytest, jest) are configured in `requirements.txt` or `package.json`.

---

## 2. Logic Chain

1. **Finding Non-functional UI Elements**:
   - Grepping `alert(` revealed pricing upgrade buttons stubbed with `alert("Chức năng thanh toán đang được phát triển!")` in `PricingModal.jsx`.
   - Inspecting the UI modals (`UploadSourcesModal.jsx`, `CreateExamModal.jsx`, `CreateStudyDocModal.jsx`) showed forms with hardcoded `disabled` attributes or no bindings on input elements.
   - Grepping `url` in `UploadSourcesModal.jsx` revealed the fetch request calling `/api/documents/url`. Comparing this with backend routes in `main.py` (which defines `@app.post("/api/documents/ingest_url")`) confirms a path mismatch.

2. **Finding Backend/NLP Mock Fallbacks**:
   - Analyzing `/api/generate_path` and `/api/suggestions` in `backend/main.py` revealed that if no key is present or starts with `AQ`, mock response schemas are returned instead of executing AI logic.
   - Inspecting `/api/generate_exam_prep` and `/api/generate_study_plan` showed they throw 400/500 errors directly instead of having offline fallbacks.
   - Inspecting `backend/nlp/concept_map.py` revealed that the offline `generate_concept_map` logic returns formatted nodes with only `id` and `label`, causing `ConceptMapModal.jsx` to lack definitions and formulas.

3. **Finding Context Compatibility Violations**:
   - Inspecting `models.py` showed that `ChatMessage` and `Artifact` tables only possess `project_id`, making it physically impossible to persist chats or generated study materials for standalone documents.
   - Comparing `AppLayout.jsx` and `Sidebar.jsx` path parsing showed a mismatch: `AppLayout` only triggers document mode on `/document/`, whereas `Sidebar` triggers it on both `/document/` and `/project/`. This breaks the workspace layout when opening projects.
   - Inspecting regexes in `TakeQuizModal`, `SmartNotesModal`, etc. showed they match `/document/:id` in URL hashes. When rendering projects via `/project/:id`, this regex fails, causing these modals to resolve a document from other workspaces.
   - Inspecting `ProjectCollaborationModal.jsx` showed that the input fields and buttons are disabled unless `projectId` is present, meaning users cannot invite anyone to standalone documents despite backend availability.

---

## 3. Caveats

- **No local Ollama testing**: Although local status checks are exposed, we could not run local LLM verification because Ollama is not installed/running locally.
- **Dependency-level tests**: Internal dependency tests inside `node_modules` and `venv` were ignored since they do not test custom application logic.
- **MinIO caching**: The readme mentions caching to MinIO, but we did not inspect MinIO instances as the local sqlite server (`omilearn_local.db` / `local.db`) is the direct backend store.

---

## 4. Conclusion

The application has multiple structural, routing, and functional deficiencies:
1. **Metadata Decorativeness**: The upload metadata inputs and configuration forms (Exam & Study Doc builders) are entirely mock stubs that do not function.
2. **Context Violation**: The User Rule "Handle Project vs. Standalone Document Contexts" is violated at every layer:
   - Database layer lacks columns for document-level chats and artifacts.
   - Routing and sidebar layout break when switching to `/project/`.
   - Modals use fragile hash-parsing that fails in the project context.
   - Frontend disables collaboration for standalone documents.
3. **API Mismatch**: Link ingestion fails due to the `/api/documents/url` vs `/api/documents/ingest_url` endpoint mismatch.
4. **Mocked Responses**: Several key generation pathways fall back to hardcoded strings when Gemini keys are missing.

---

## 5. Verification Method

1. **Verify API Mismatch**: Run `curl -X POST http://127.0.0.1:8000/api/documents/url` to confirm it returns `404 Not Found`. Run `curl -X POST http://127.0.0.1:8000/api/documents/ingest_url` to confirm it exists.
2. **Verify Database Columns**: Open the database using `sqlite3 backend/local.db` or `sqlite3 backend/omilearn_local.db` and run `.schema chat_messages` and `.schema artifacts` to verify they do not have a `document_id` column.
3. **Verify App Build**: Run `npm run build` from the root workspace directory to confirm the frontend compiles.
4. **Verify Backend Address in Use**: Run `lsof -i :8000` to verify a process is currently running on the port.
5. **Verify Layout Mismatch**: Inspect `src/components/layout/AppLayout.jsx` line 13 and `src/components/layout/Sidebar.jsx` line 10.
