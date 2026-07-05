# Progress Log

Last visited: 2026-06-28T09:36:00Z

## Current Task
Completed backend schema migrations, offline NLP fallbacks, and test verification.

## To-Do List
- [x] Investigate existing backend files (`models.py`, `crud.py`, `main.py`, `concept_map.py`)
- [x] Apply changes from changes.patch to `backend/db/models.py`, `backend/db/crud.py`, `backend/main.py`
- [x] Implement `_extract_definition_and_formula` and update `generate_concept_map` and `_vietnamese_concept_map` in `backend/nlp/concept_map.py`
- [x] Implement offline local-NLP generators (`generate_offline_exam_prep`, `generate_offline_study_plan`, `generate_offline_learning_path`, `generate_offline_suggestions`) in `backend/nlp/concept_map.py`
- [x] Integrate offline generators into API endpoints in `backend/main.py`
- [x] Verify using pytest in `backend/` directory
- [x] Add/update tests to cover these offline fallbacks and schema changes
- [x] Write implementation/handoff report
