# BRIEFING — 2026-06-28T09:30:15Z

## Mission
Implement backend schema updates (making chat messages, artifacts, and flashcards support document_id and project_id), schema patching on startup, and robust offline local-NLP fallback generators.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/worker_m2_2
- Original parent: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Milestone: Milestone 2: Backend Stability & Schema Contexts

## 🔒 Key Constraints
- Handle Project vs. Standalone Document Contexts (from USER_RULES)
- CODE_ONLY network mode
- Keep modifications minimal and correct.
- Verify changes using backend tests.

## Current Parent
- Conversation ID: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Updated: not yet

## Task Summary
- **What to build**: 
  - Nullable project_id columns & new document_id column in ChatMessage, Artifact, Flashcard database models.
  - Startup database schema migration routine in main.py.
  - Updated CRUD operations to handle project_id and document_id parameters.
  - Aligned API endpoints to support dual project/document contexts.
  - Offline local-NLP fallbacks for exam prep, study plan, learning path, suggestions, and concept node definition/formula extraction.
- **Success criteria**:
  - All endpoints return correct schemas even when offline (starts with "AQ" or no API key, or on AI agent failures).
  - All tests pass cleanly.
- **Interface contracts**: backend/main.py
- **Code layout**: backend/db/models.py, backend/db/crud.py, backend/main.py, backend/nlp/concept_map.py

## Key Decisions Made
- Use changes.patch as a base to modify backend/db/models.py, backend/db/crud.py, and backend/main.py.
- Add definition and formula extraction to concept map generation in `backend/nlp/concept_map.py`.
- Put offline NLP fallbacks in `backend/nlp/concept_map.py`.
- Integrate offline NLP generators into `/api/generate_exam_prep`, `/api/generate_study_plan`, `/api/generate_path`, and `/api/suggestions`.
- Cascade deletion in CRUD delete_project and delete_document to prevent database pollution.
- Initialize flashcard repetitions=1 to fit test expectations.
- Support content and role parameters in ChatRequest and return message ID to align with E2E test assertions.

## Change Tracker
- **Files modified**:
  - `backend/nlp/roadmap.py`: replaced vi.truncate_text with text slicing.
  - `backend/nlp/quizzes.py`: added "answer" key mapping correct_id.
  - `backend/db/crud.py`: added cascade deletion cleanup for projects/documents, set flashcard default repetitions to 1 on creation.
  - `backend/main.py`: added project existence checks, re-raised HTTPExceptions in endpoints, added content/role to ChatRequest schema and returned message ID in chat.
- **Build status**: Pass
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pass (71/71 tests passed)
- **Lint status**: Clean
- **Tests added/modified**: E2E tests verified

## Loaded Skills
- None
