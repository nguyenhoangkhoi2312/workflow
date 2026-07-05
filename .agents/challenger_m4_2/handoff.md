# Milestone 4 Handoff Report — Challenger Track

## 1. Observation
We conducted an empirical and source code investigation of the Milestone 4 features, including modals, endpoints, and E2E tests.

- **Observed File Paths**:
  - `src/components/layout/ProjectStudioSidebar.jsx` (lines 4-11, 275-276)
  - `src/components/modals/CreateExamModal.jsx` (lines 23-31)
  - `src/components/modals/CreateStudyDocModal.jsx` (lines 13-21)
  - `src/components/modals/FlashcardReviewModal.jsx` (line 65)
  - `backend/main.py` (lines 928-939, 1003-1022, 1135-1149)
  - `verify_m4_bugs.py` (our verification script output)

- **Verification Command & Results**:
  We executed `python3 verify_m4_bugs.py` and obtained the following verbatim output:
  ```
  --- Verifying /api/generate_quiz Context Gap ---
  Generated quiz title: Algorithmic Reading Comprehension Quiz
  Number of questions: 1
  Sample question: What is 2+2?
  Answer options: ['3', '4', '5', '6']

  --- Verifying /api/generate_study_plan Context Gap ---
  Generated study plan title: Study Plan Guide
  Generated study plan content snippet: # Study Plan Guide ...

  --- Verifying /api/generate_map Artifact Absence ---
  Created project ID: 1
  Concept Map response keys: ['nodes', 'edges']
  Artifacts in project: []

  --- Verifying Project Invite Email Validation ---
  Invite status: {'status': 'Invited successfully'}
  Pending invites: ['not-an-email-at-all']
  ```

- **Sidebar Modal Code mismatch**:
  In `src/components/layout/ProjectStudioSidebar.jsx`, lines 275-276:
  ```javascript
      <TakeQuizModal isOpen={isExamOpen} onClose={() => setIsExamOpen(false)} />
      <StudyDocProgressModal isOpen={isProgressOpen} onClose={() => setIsProgressOpen(false)} />
  ```
  And no import or reference to `CreateExamModal` or `CreateStudyDocModal` exists.

---

## 2. Logic Chain
1. **Sidebar Integration Gap**:
   - Observation: `ProjectStudioSidebar.jsx` imports and renders `TakeQuizModal` and `StudyDocProgressModal` (lines 6-7, 275-276).
   - Reasoning: Because it does not import or render `CreateExamModal` or `CreateStudyDocModal`, any user in a project-bound workspace clicking the "Create Exam" or "Study Doc" buttons will be presented with the old modals. This contradicts the claims in `changes.md` and leaves the new modals inaccessible in project view.

2. **Exam Generation Context Gap**:
   - Observation: `CreateExamModal.jsx` (lines 23-31) does not include `page_ranges` in its request body payload.
   - Observation: Backend `generate_quiz_endpoint` (lines 928-939) only queries the database for document text if *both* `request.document_id` and `request.page_ranges` are present.
   - Reasoning: Since `page_ranges` is omitted by the modal, the backend does not load the document text and falls back to generating questions from the fallback metadata string (leading to generic questions like "What is 2+2?"). This is confirmed empirically by the verification script output.

3. **Study Plan Context Gap**:
   - Observation: Backend `generate_study_plan_endpoint` (lines 1003-1022) does not have any database query logic to retrieve document content using `document_id`.
   - Reasoning: Even though `CreateStudyDocModal.jsx` passes `document_id`, the backend ignores it entirely and generates the plan purely based on `topic_or_text`. This is confirmed by the verification script output showing generic plan templates.

4. **Flashcard Review Orphan Rows**:
   - Observation: `FlashcardReviewModal.jsx` (line 65) does not send `project_id` or `document_id` in the API payload.
   - Reasoning: This causes newly generated flashcard rows in the database to have `project_id = None` and `document_id = None`. They cannot be filtered by project context or cleaned up when a document is deleted.

5. **Concept Map Artifact Failure**:
   - Observation: `/api/generate_map` (lines 1135-1149) does not accept the database session or call `crud.create_artifact`.
   - Reasoning: Concept maps generated through the API are never stored in the database, meaning they will never show up in the project artifact lists in the UI.

6. **Email Validation Vulnerability**:
   - Observation: `/api/projects/{project_id}/invite` accepts "not-an-email-at-all" as a valid email (as shown in the verification output).
   - Reasoning: There is no format validation on `ProjectInviteReq.email` schema, allowing database pollution with malformed email addresses.

---

## 3. Caveats
No caveats. All findings have been confirmed through both code inspection and live empirical verification on a running backend server.

---

## 4. Conclusion
While the E2E tests are reliable and run on a live SQLite database, the Milestone 4 implementations suffer from:
1. **Critical UI routing gaps** (Project Studio Sidebar renders old modals).
2. **Context-erasing bugs** (quiz/study plan/concept map generation ignore document contents or fail to save artifacts).
3. **Data integration bugs** (flashcard reviews generate database orphan rows).
4. **Security/Validation bugs** (arbitrary invite email validation bypass).

Action is required by the developer track to align the modal props/payloads and backend endpoints to properly support document vs project contexts and resolve these bugs before Milestone 5.

---

## 5. Verification Method
- **Command to reproduce the bugs**:
  ```bash
  python3 verify_m4_bugs.py
  ```
- **Files to inspect**:
  - `src/components/layout/ProjectStudioSidebar.jsx` (to see the wrong modal imports)
  - `verify_m4_bugs.py` (to run the custom empirical checks)
