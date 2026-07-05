# Handoff Report

## 1. Observation
- In the initial test run of `python3 run_e2e_tests.py` (executed via task-17), we observed:
  ```
  FAILED tests/e2e/test_tier1_feature_coverage.py::test_f2_roadmap_item_interactivity
  ======================== 1 failed, 73 passed in 11.73s =========================
  ```
- The detailed failure log for `test_f2_roadmap_item_interactivity` showed:
  ```
  # 1. Verify default values (0 for both)
  >       assert items[0]["completed"] == 0
  E       assert 1 == 0
  ```
- Inspecting `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/backend/db/crud.py` showed that `delete_document` and `delete_project` deleted roadmap rows using SQLAlchemy bulk delete queries:
  - In `delete_document`:
    ```python
    db.query(models.Roadmap).filter(models.Roadmap.document_id == doc_id).delete()
    ```
  - In `delete_project`:
    ```python
    db.query(models.Roadmap).filter(models.Roadmap.project_id == project_id).delete()
    ```

## 2. Logic Chain
- SQLAlchemy's bulk `Query.delete()` compiled directly to a database-level `DELETE` statement, which bypassed the SQLAlchemy ORM session unit-of-work. Because it bypassed the ORM session, relationship-defined cascades (like `cascade="all, delete-orphan"` on `Roadmap.items`) were not executed.
- As a result, deleting a document or project deleted its `Roadmap` entries but left orphaned `RoadmapItem` rows in the database referencing the deleted roadmap IDs.
- When new documents or projects were created, SQLite reused the primary key IDs (such as `id = 1` for the `Roadmap`). The new `Roadmap` then incorrectly inherited the orphaned `RoadmapItem` entries of the deleted roadmap, causing the E2E test `test_f2_roadmap_item_interactivity` to fail when it expected newly generated roadmap items to have default values (`completed = 0`).
- By querying the existing roadmaps first and explicitly deleting their related `RoadmapItem` records, we ensure orphaned rows are never left in the database.

## 3. Caveats
- The scope of the fix was kept minimal, specifically modifying `delete_document` and `delete_project` in `backend/db/crud.py` to clean up orphaned `RoadmapItem` rows. No other cascade cleanup behaviors or model mappings were changed.

## 4. Conclusion
- The database cascade delete bug has been successfully resolved. When deleting a document or a project, the associated `RoadmapItem` entries are cleaned up first, preventing orphaned rows from contaminating subsequent queries.

## 5. Verification Method
- Execute the E2E test runner to ensure all 74 tests pass successfully:
  ```bash
  python3 run_e2e_tests.py
  ```
- Verify the code changes in `backend/db/crud.py` under functions `delete_document` and `delete_project` to ensure the associated `RoadmapItem` records are deleted before their parent `Roadmap` records.
