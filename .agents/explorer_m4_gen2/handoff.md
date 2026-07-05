# Handoff Report - explorer_m4_gen2

## 1. Observation
We examined the workspace files related to the frontend modals, API connections, mock payment tier, and the E2E test suite. The following observations were recorded:

### Modals:
* **`src/components/modals/PricingModal.jsx`**:
  * Lines 8–33: Defines `handleUpgrade()` which reads the active user from `localStorage` under `workflow_user` and sends a POST request to `http://127.0.0.1:8000/api/user/upgrade`.
* **`src/components/modals/UploadSourcesModal.jsx`**:
  * Line 60: Uses fetch to post to `http://127.0.0.1:8000/api/documents/url`.
  * Lines 35–39: Displays a dashed upload zone with no associated `<input type="file">` or handlers. It is a dead UI block for file upload.
* **`src/components/modals/UploadModal.jsx`**:
  * Lines 20–25: Uploads a single file to `http://127.0.0.1:8000/api/documents/upload`.
  * Line 4: Signature does not accept `projectId` or `documentId`. It does not forward them to the upload request.
* **`src/components/modals/CreateExamModal.jsx`**:
  * Line 149–151: The "Tạo đề thi" button is hardcoded with `cursor: 'not-allowed'` and has no action handler.
* **`src/components/modals/CreateStudyDocModal.jsx`**:
  * Line 78–80: The "Tạo tài liệu" button is hardcoded with `cursor: 'not-allowed'` and has no action handler.
* **`src/components/modals/ProjectCollaborationModal.jsx`**:
  * Lines 127, 134, 144, 148: Input fields and buttons are disabled when `!projectId` is true. This prevents interaction when only `documentId` (standalone document context) is provided.

### Backend User Upgrade & Models:
* **`backend/db/models.py`**:
  * Line 78: User table defines `status = Column(String, default="free")`.
* **`backend/main.py`**:
  * Lines 278–288: `@app.post("/api/user/upgrade")` receives user email, creates/updates the User row in SQLite database setting `status="premium"`.

### E2E Tests:
* Run command: `python3 run_e2e_tests.py` triggers `pytest tests/e2e --junitxml=tests_result.xml -v`.
* Output: `71 passed in 16.95s`. It generates `TEST_INFRA.md` and `TEST_READY.md`.

---

## 2. Logic Chain
1. Since `CreateExamModal.jsx` and `CreateStudyDocModal.jsx` have no connection to backend generation endpoints `/api/generate_quiz` and `/api/generate_exam_prep` respectively, and their primary trigger buttons are styled as `not-allowed`, these UIs are completely "dead".
2. Because `ProjectCollaborationModal.jsx` uses `disabled={!projectId}` on input controls, it fails to allow users to invite collaborators to standalone documents, which violates the user rule to support both `project_id` and `document_id`.
3. Since `UploadSourcesModal.jsx` lacks file input reference and event handlers for drag-drop, it does not support file upload in the project view.
4. Because `run_e2e_tests.py` starts the backend server when not running, executes `pytest`, and creates markdown reports, we can use it to verify the codebase state.

---

## 3. Caveats
* We assumed that the backend endpoints `/api/generate_quiz` and `/api/generate_exam_prep` do not need extra configuration attributes (such as duration, difficulty level) explicitly in the database model schema, as they are not present in `TopicRequest` parameters. Instead, these options can be integrated as instructions inside the prompt context if necessary.
* No changes were made directly to the codebase since this is a read-only investigation.

---

## 4. Conclusion
To transition from a "dead UI" implementation to a connected state, the following implementation tasks are required:
1. Update `ProjectCollaborationModal.jsx` to enable inputs when `(!projectId && !documentId)` is false.
2. Wire `UploadSourcesModal.jsx` drag-and-drop region using a hidden file input and fetch to `/api/documents/upload`.
3. Support forwarding `projectId` within `UploadModal.jsx`.
4. Import and connect `CreateExamModal.jsx` and `CreateStudyDocModal.jsx` in the sidebar layouts, and connect them to their corresponding backend generation APIs.

---

## 5. Verification Method
1. Execute E2E tests:
   ```bash
   python3 run_e2e_tests.py
   ```
2. Verify JUnit XML output: `tests_result.xml` should report 71/71 tests passed.
3. Check generated documentation: `TEST_INFRA.md` and `TEST_READY.md` should be updated at the workspace root.
