# Handoff Report - Branding & Test Compliance

## 1. Observation
- **File**: `src/components/layout/ProjectStudioSidebar.jsx`
  - *Line 151*: `<button onClick={() => alert(`Link chia sẻ tài liệu công khai: https://omilearn.com/share/${doc.id}`)}...`
- **File**: `src/components/modals/PricingModal.jsx`
  - *Line 53*: `Chào mừng bạn đến với Omilearn Pro. Tất cả các tính năng nâng cao đã được mở khóa.`
  - *Line 87*: `Nâng cấp Omilearn Pro`
- **File**: `src/pages/DocumentExplorer.jsx`
  - *Line 100*: `Tài liệu được đồng bộ tự động mỗi 10 phút từ Google Drive, cache về MinIO và xem bằng viewer nội bộ của Omilearn.`
- **File**: `src/pages/LandingPage.jsx`
  - *Line 28*: `Omilearn`
- **E2E Test Run**: Command `python3 run_e2e_tests.py` ran. Initially, 70/71 tests passed, with `test_f1_upload_unicode_characters` failing:
  ```
  tests/e2e/test_tier2_boundary_corner.py::test_f1_upload_unicode_characters FAILED
  ...
  E       UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4 in position 10: invalid continuation byte
  ```
- **Backend File Retrieval Logic**: `backend/main.py` lines 848-854:
  ```python
  @app.get("/api/documents/{document_id}/file")
  async def get_document_file(document_id: int):
      import glob
      files = [f for f in glob.glob(os.path.join(UPLOAD_DIR, f"{document_id}.*")) if not f.endswith('.txt')]
  ```
  And `backend/uploads/` contained pre-existing dangling `.pdf` files matching IDs of uploaded `.txt` files (e.g., `11.pdf` and `11.txt`), causing the text file retrieve test to serve the binary PDF instead.

## 2. Logic Chain
1. By examining the frontend React codebase (Observations 1-4), we located all user-facing instances of 'OmiLearn' and 'Omilearn' that needed replacement.
2. By executing precise code replacements using `replace_file_content` and `multi_replace_file_content`, we successfully renamed all target instances to `Workflow`.
3. Running `npm run build` confirmed that the frontend compiles cleanly under the new branding names.
4. Analyzing the E2E test failure (Observation 5) revealed a UnicodeDecodeError when trying to decode the returned source file content of a text upload.
5. Examining the backend file serving endpoint (Observation 6) showed it unconditionally filters out `.txt` extensions, expecting them to be auxiliary cache files.
6. Because `backend/uploads/` contained pre-existing dangling files like `11.pdf` from previous mock runs, the backend matched `11.pdf` instead of the original `11.txt`, serving binary PDF data to the test that expects plain text.
7. We modified `backend/main.py` to first check the database record for the document's original filename suffix. If the suffix matches `.txt`, we do not filter out the `.txt` extension, and we retrieve the correct original file. This resolves the encoding/decoding conflict and ensures correct file serving.
8. Re-running the E2E test suite resulted in all 71/71 tests passing successfully.

## 3. Caveats
- We assumed that auxiliary `.txt` files should only be filtered out when the original document suffix is not `.txt`. If the original document suffix is `.txt`, the text file itself is the original source media and must be served.

## 4. Conclusion
All user-facing branding issues have been resolved. The React frontend builds cleanly and the entire E2E test suite (71/71 tests) passes.

## 5. Verification Method
- **Frontend Build**: Run `npm run build` from the project root.
- **E2E Suite**: Run `python3 run_e2e_tests.py` from the project root. Verify that 71 tests pass.
- **Files to Inspect**:
  - `src/components/layout/ProjectStudioSidebar.jsx`
  - `src/components/modals/PricingModal.jsx`
  - `src/pages/DocumentExplorer.jsx`
  - `src/pages/LandingPage.jsx`
  - `backend/main.py`
