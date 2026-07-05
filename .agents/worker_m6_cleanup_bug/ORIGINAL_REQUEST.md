## 2026-06-29T01:00:56Z
Fix the database cascade delete bug in `backend/db/crud.py` where deleting a project or standalone document leaves orphaned `RoadmapItem` rows.

Specifically:
1. In `backend/db/crud.py`, modify `delete_document(db: Session, doc_id: int)`:
   Before calling `db.query(models.Roadmap).filter(models.Roadmap.document_id == doc_id).delete()`, retrieve the existing roadmaps for that document ID and delete their corresponding `RoadmapItem` rows from the database first, just like in `create_roadmap`.
2. In `backend/db/crud.py`, modify `delete_project(db: Session, project_id: int)`:
   Before calling `db.query(models.Roadmap).filter(models.Roadmap.project_id == project_id).delete()`, retrieve the existing roadmaps for that project ID and delete their corresponding `RoadmapItem` rows from the database first.
3. Run the E2E test suite `python3 run_e2e_tests.py` to ensure all 74 tests pass successfully.
4. Report your progress and write your final handoff in `.agents/worker_m6_cleanup_bug/handoff.md`.
