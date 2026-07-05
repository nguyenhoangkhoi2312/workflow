## 2026-06-28T05:21:14Z
You are the E2E Test Developer (archetype: teamwork_preview_worker).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/worker_e2e_setup.
Your parent is 9b79a6e8-7267-4014-8486-1d21cfddb79c (E2E Testing Track Orchestrator).

Your objective is to:
1. Create the `tests/e2e/` directory under `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/`.
2. Implement a complete pytest-based E2E test suite in Python against http://127.0.0.1:8000.
3. Design and implement 71 test cases covering the 4-tier testing methodology for 6 core features:
   - F1: Document ingestion (Upload & URL link)
   - F2: Roadmap generation (both Project & Standalone Document contexts)
   - F3: Quiz generation, submission, and document progress tracking
   - F4: AI / NLP study materials & offline fallbacks (Exam prep, Study plan, Concept map, Suggestions, Learning path)
   - F5: Flashcard generation, due list, and SM-2 spaced repetition updates
   - F6: Project and Standalone Document collaboration (Invites and member listings)

--- MANDATORY INTEGRITY WARNING ---
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

--- DESIGN DETAILS ---
The test cases must be organized as follows:
- `tests/e2e/conftest.py`: contains fixture for base URL (http://127.0.0.1:8000), API helper functions (handling post/get/delete requests, logins, multipart uploads, etc.), and fixtures for setup/teardown of temporary projects/documents to clean up testing state.
- `tests/e2e/test_tier1_feature_coverage.py`: At least 30 test cases (5 per feature F1-F6).
- `tests/e2e/test_tier2_boundary_corner.py`: At least 30 test cases (5 per feature F1-F6).
- `tests/e2e/test_tier3_cross_feature.py`: At least 6 test cases testing interactions (e.g. Ingest -> Quiz -> Submit -> Progress).
- `tests/e2e/test_tier4_real_world.py`: At least 5 complex user scenarios (e.g. full study cycle, collaborative exam prep, spaced repetition mastery, offline fallback).

- `run_e2e_tests.py`: Python test runner script that checks if the backend is running at http://127.0.0.1:8000. If it isn't, it starts the backend (using `uvicorn main:app` or python command, similar to `test_api.py`), runs pytest, collects test execution results, writes `TEST_READY.md` and `TEST_INFRA.md` at the project root, and shutdowns the backend if it started it. If the backend was already running, it just runs pytest and updates the docs.

Create `TEST_INFRA.md` at project root with:
- Test Philosophy
- Feature Inventory (F1-F6)
- Test Architecture (pytest structure, fixtures, runner)
- Real-World Application Scenarios (Tier 4 list)

Create `TEST_READY.md` at project root with:
- Test runner invocation command
- Summary of pytest runs (test counts by tier, count of passed/failed)
- Feature checklist (F1-F6 coverage)

Execute the test suite and verify everything runs. Note that since some of these features (such as standalone document roadmaps/invites, flashcards schema context, nlp offline fallbacks) are not yet fixed by the implementation track, we expect some tests to fail. That is correct and expected! The E2E tests should target the correct, required APIs/schemas, acting as a regression and specification harness.

Write all test files and running scripts. Perform execution and write the reports. When done, write your handoff report to `handoff.md` in your working directory and message me with the paths of all created files and test run summary.
