# BRIEFING — 2026-06-29T07:55:00+07:00

## Mission
Investigate codebase and design the interactive "Giáo án" (Study Plan / Roadmap tracker) feature.

## 🔒 My Identity
- Archetype: Teamwork explorer (read-only)
- Roles: Read-only investigator, analyzer
- Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m6_investigation
- Original parent: 80dbe471-e631-4283-8d73-85e18fcf4926
- Milestone: explorer_m6_investigation

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Design "Giáo án" feature matching OmiLearn UI (look, feel, active highlight, connecting lines, buttons)
- Research specific files (backend: models, crud, main; frontend: ProjectStudioSidebar)
- Maintain Project vs. Standalone Document contexts

## Current Parent
- Conversation ID: 80dbe471-e631-4283-8d73-85e18fcf4926
- Updated: 2026-06-29T07:55:00+07:00

## Investigation State
- **Explored paths**:
  - `backend/db/models.py` (Database model structure)
  - `backend/db/crud.py` (CRUD query helpers)
  - `backend/main.py` (API endpoints and schema patching)
  - `backend/nlp/roadmap.py` (Roadmap generation prompts)
  - `src/components/layout/ProjectStudioSidebar.jsx` (Sidebar UI component)
  - `src/components/modals/StudyPlanModal.jsx` (Lộ trình/Study plan generator UI modal)
  - `src/components/modals/CreateLessonPlanModal.jsx` (Lesson plan modal details)
  - `src/components/layout/AppLayout.jsx` (Vite Page layout mapping)
  - `tests/e2e/test_tier1_feature_coverage.py` (E2E testing scripts)
  - `tests/e2e/conftest.py` (Client helpers)
  - `run_e2e_tests.py` (Test runner script)
- **Key findings**:
  - `completed` column exists in `RoadmapItem` model but lacks update endpoints.
  - Active selection is completely missing from both DB and frontend. We proposed adding an `active` column to `RoadmapItem` and updating `patch_database_schema(engine)` for automatic SQLite migrations on startup.
  - We designed a `PATCH /api/roadmap/items/{item_id}` endpoint to toggle `completed` and `active` status.
  - We integrated active roadmap topic selection directly into the system message builder of the `/api/chat` endpoint.
  - We designed interactive mouse click events in `ProjectStudioSidebar.jsx` (clicking circles toggles completed, clicking cards highlights active state) along with study pills (Hỏi AI, Tạo Quiz) matching OmiLearn UI.
- **Unexplored areas**: None.

## Key Decisions Made
- Chose Option B (storing `active` flag on `RoadmapItem`) over Option A (storing `active_item_id` on `Roadmap`) for better database migration safety and CRUD simplicity in SQLite.
- Integrated the active roadmap step topic into the `/api/chat` prompt context to provide a cohesive experience.

## Artifact Index
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m6_investigation/ORIGINAL_REQUEST.md — Original user request log
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m6_investigation/BRIEFING.md — Investigation briefing and state index
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m6_investigation/progress.md — Task checklist and liveness heartbeat
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m6_investigation/analysis.md — Technical design and analysis of the "Giáo án" feature
