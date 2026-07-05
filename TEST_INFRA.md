# TEST INFRASTRUCTURE DOCUMENTATION

## Test Philosophy
The E2E test suite acts as both a regression safety net and a specification harness. It is designed to verify the correct, required APIs and database schemas under a 4-tier testing methodology, supporting local offline-first NLP logic and multi-context views (Project and Standalone Document).

## Feature Inventory (F1-F6)
- **F1: Document Ingestion**: Verifies text file upload, project-bound uploads, URL link ingestion, YouTube transcript extraction, and safe deletion.
- **F2: Roadmap Generation**: Covers roadmap creation, step completion, and step listing for both Project and Standalone Document contexts.
- **F3: Quiz & Progress**: Validates multiple-choice quiz generation from document content, score submission, page-range selection, and document progress tracking.
- **F4: AI / NLP & Fallbacks**: Tests learning path, concepts mapping, exam prep, study plan, and auto-fallback to local NLP logic if API keys are missing/invalid.
- **F5: Flashcards & SM-2**: Assesses spaced repetition flashcard generation, due list, review state changes, and verification of SM-2 math calculations.
- **F6: Collaboration**: Tests invite creation, roles (owner, editor, viewer), and members listing for both Project and Standalone Document workspaces.

## Test Architecture
- `tests/e2e/conftest.py`: Session-wide base URL setup, fixture projects/documents/folders, and full `ApiClient` helper functions encapsulating endpoints.
- `tests/e2e/test_tier1_feature_coverage.py`: 30 baseline tests checking happy paths for all 6 features.
- `tests/e2e/test_tier2_boundary_corner.py`: 30 boundary and negative tests checking empty inputs, invalid keys, large payloads, unicode, non-existent objects, and out-of-bound inputs.
- `tests/e2e/test_tier3_cross_feature.py`: 6 integration tests evaluating multi-step workflows.
- `tests/e2e/test_tier4_real_world.py`: 5 real-world user scenarios representing full study cycles, collaboration, spaced repetition, offline fallbacks, and standalone document workspaces.

## Real-World Application Scenarios (Tier 4)
1. **Full Study Cycle**: Alex signs in, creates project, uploads documents, generates roadmap/suggestions, reviews cards, takes quiz, submits, and views stats.
2. **Collaborative Exam Prep**: Lead student uploads syllabus, invites peers, generates cheat sheet/concept map, and posts comments to sync.
3. **Spaced Repetition Mastery**: Focuses on memory retention transitions under SM-2 spaced repetition (e.g. perfect vs blackout states).
4. **Offline Fallback**: Verifies robust offline-first behavior when no key is specified, falling back to local NLP library methods.
5. **Standalone Document Workspace**: Researcher uploads a document, maps roadmap, invites co-author, generates quiz, and tracks document progress.
