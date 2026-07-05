# Scope: E2E Testing Track

## Architecture
- **E2E Test Runner**: Uses `pytest` to run tests programmatically.
- **API Target**: Backend FastAPI app running on `http://127.0.0.1:8000`.
- **E2E Testing Modules**:
  - `tests/e2e/conftest.py` - pytest fixtures, client setup, project/document creation & teardown helpers.
  - `tests/e2e/test_tier1_feature_coverage.py` - Feature coverage tests (F1-F6, >=30 cases).
  - `tests/e2e/test_tier2_boundary_corner.py` - Boundary/corner case tests (F1-F6, >=30 cases).
  - `tests/e2e/test_tier3_cross_feature.py` - Interacting feature combinations (>=6 cases).
  - `tests/e2e/test_tier4_real_world.py` - Complex user scenarios (>=5 scenarios).
  - `run_e2e_tests.sh` - Simple shell script to run the entire test suite.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Test Infra Setup | Create pytest configuration, fixtures, API helper client, and verification script skeleton. | None | DONE |
| 2 | Tier 1 & Tier 2 Test Cases | Implement 30 Tier 1 (Feature Coverage) and 30 Tier 2 (Boundary & Corner) test cases covering F1-F6. | M1 | DONE |
| 3 | Tier 3 & Tier 4 Test Cases | Implement >=6 Tier 3 (Cross-Feature) and >=5 Tier 4 (Real-World Scenario) test cases. | M2 | DONE |
| 4 | Execution & Reporting | Run the test suite against the local backend, publish `TEST_INFRA.md` and `TEST_READY.md` at project root, and generate a final E2E test report. | M3 | DONE |

## Interface Contracts
### E2E Tests ↔ FastAPI Backend Endpoints
- **F1: Document Ingestion**:
  - `POST /api/documents/upload` (multipart/form-data)
  - `POST /api/documents/ingest_url` (JSON)
- **F2: Roadmap Generation**:
  - `POST /api/projects/{project_id}/roadmap/generate` (JSON)
  - `POST /api/documents/{document_id}/roadmap/generate` (JSON)
- **F3: Quiz Generation & Progress**:
  - `POST /api/generate_quiz` (JSON)
  - `POST /api/quizzes/submit` (JSON)
  - `GET /api/documents/{document_id}/progress` (JSON)
- **F4: AI / NLP Study Materials & Offline Fallbacks**:
  - `POST /api/generate_exam_prep` (JSON)
  - `POST /api/generate_study_plan` (JSON)
  - `POST /api/generate_map` (JSON)
- **F5: Flashcard Generation & Spaced Repetition**:
  - `POST /api/generate_flashcards` (JSON)
  - `GET /api/flashcards/due` (JSON)
  - `POST /api/flashcards/{card_id}/review` (JSON)
- **F6: Project & Standalone Document Collaboration**:
  - `POST /api/projects/{project_id}/invite` (JSON)
  - `POST /api/documents/{document_id}/invite` (JSON)
  - `GET /api/projects/{project_id}/members` (JSON)
  - `GET /api/documents/{document_id}/members` (JSON)
