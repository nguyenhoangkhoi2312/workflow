# Forensic Audit Handoff Report

## Forensic Audit Report

**Work Product**: Interactive "Giáo án" (Roadmap progress tracker) implementation files:
- `backend/db/models.py`
- `backend/db/crud.py`
- `backend/main.py`
- `src/components/layout/ProjectStudioSidebar.jsx`
- `tests/e2e/test_tier1_feature_coverage.py`
- `tests/e2e/test_tier2_boundary_corner.py`

**Profile**: General Project
**Verdict**: CLEAN

### Phase Results
- **Hardcoded test output check**: PASS — Source code inspection and runtime execution show no hardcoded test outputs or bypass strings.
- **Facade implementation check**: PASS — Database CRUD, models, and FastAPI routes contain genuine application logic.
- **Pre-populated artifact check**: PASS — No pre-populated artifacts/logs exist before testing.
- **Branding compliance check**: PASS — User-facing UI files and response objects do not contain any references to "OmiLearn" or "OmiGuide". All references are correctly mapped to "Workflow".
- **Proper project/document context check**: PASS — Features and database models support both `project_id` and `document_id` cleanly.
- **Build and test run**: PASS (with clean database) — Running uvicorn and pytest from a clean DB completes with all 74 E2E tests passing.

---

## 5-Component Handoff Report

### 1. Observation
1. **Source Code Modifications**:
   - `backend/db/models.py` successfully added `Roadmap` and `RoadmapItem` models, supporting both `project_id` and `document_id`.
   - `backend/db/crud.py` added `create_roadmap`, `get_roadmap`, and `update_roadmap_item`.
   - `backend/main.py` added endpoints `GET /api/projects/{project_id}/roadmap`, `POST /api/projects/{project_id}/roadmap/generate`, `GET /api/documents/{document_id}/roadmap`, `POST /api/documents/{document_id}/roadmap/generate`, and `PATCH /api/roadmap/items/{item_id}`.
   - `src/components/layout/ProjectStudioSidebar.jsx` integrated interactive UI elements, calling the generate and get roadmap endpoints.
   - `tests/e2e/test_tier1_feature_coverage.py` and `tests/e2e/test_tier2_boundary_corner.py` added standard integration tests for roadmap interactivity and boundaries.

2. **Initial Test Run Execution**:
   - Executing `python3 run_e2e_tests.py` on the pre-existing database led to a test failure:
     ```
     FAILED tests/e2e/test_tier1_feature_coverage.py::test_f2_roadmap_item_interactivity
     AssertionError: assert 1 == 0
     ```
   
3. **Database Inspection**:
   - Querying `sqlite_sequence` and `roadmap_items` tables showed that orphan `RoadmapItem` rows existed in the database matching reused primary keys:
     ```
     [(22, 2, 1, 'Đọc hiểu cơ bản', 'Nắm vững các khái niệm nền tảng trong tài liệu.', 1, 0)]
     ```
   
4. **Delete Cascade Bug**:
   - In `backend/db/crud.py`, the `delete_project` and `delete_document` functions contain the following code:
     ```python
     db.query(models.Roadmap).filter(models.Roadmap.project_id == project_id).delete()
     ```
     SQLAlchemy bulk deletes (`query.delete()`) bypass relationship cascading, leaving orphaned child rows in `roadmap_items` table.

5. **Clean Database Test Execution**:
   - Deleting the `backend/omilearn_local.db` file and running `python3 run_e2e_tests.py` resulted in all tests passing:
     ```
     ============================= 74 passed in 11.54s ==============================
     ```

### 2. Logic Chain
- **Step 1**: The initial failure of `test_f2_roadmap_item_interactivity` indicated that `completed` was retrieved as `1` immediately after the roadmap generation, instead of the default `0`.
- **Step 2**: The inspection of `backend/db/models.py` showed that `RoadmapItem.completed` has `default=0`.
- **Step 3**: Database query logs revealed that orphan `RoadmapItem` rows from previous E2E test runs with `completed=1` and `roadmap_id=2` existed in the sqlite database.
- **Step 4**: Checking the CRUD methods in `backend/db/crud.py` showed that `delete_project` and `delete_document` perform bulk query deletes on the `Roadmap` table without cleaning up the child `RoadmapItem` entries.
- **Step 5**: When a new project is created in a subsequent test, it obtains a reused roadmap ID, loading the old orphan `RoadmapItem`s.
- **Step 6**: Deleting the database and executing the tests on a clean database resolves the issue because no orphan rows exist, verifying that the implementation logic itself is authentic and passes testing.
- **Conclusion**: There are no integrity violations (e.g. cheats, facades, branding leaks). The implementation is authentic, with a logic correctness defect in the cleanup database cascade.

### 3. Caveats
- Browser-based automated UI testing (e.g. via Puppeteer/Selenium) was not executed as the audit is restricted to the modified backend/frontend files and CLI tests.
- High concurrency scenarios were not tested.

### 4. Conclusion
The Interactive "Giáo án" (Roadmap progress tracker) implementation is **CLEAN** of any integrity violations under Development Mode.
- No facades or hardcoded test bypasses were discovered.
- The UI matches the branding requirements (using "Workflow" and no OmiLearn/OmiGuide leaks).
- Proper project/document contexts are supported.
- **Actionable recommendation**: Update `delete_project` and `delete_document` in `backend/db/crud.py` to correctly delete associated `RoadmapItem`s first or trigger cascades so database pollution does not occur.

### 5. Verification Method
To independently verify the test suite:
1. Ensure no backend processes are running on port 8000.
2. Delete the dirty database if present:
   ```bash
   rm backend/omilearn_local.db
   ```
3. Run the automated E2E test suite:
   ```bash
   python3 run_e2e_tests.py
   ```
4. Verify that all 74 tests pass.
