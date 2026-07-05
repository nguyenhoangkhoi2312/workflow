# BRIEFING — 2026-06-28T12:22:34+07:00

## Mission
Implement backend database schema updates, API changes for Project vs. Document context, and offline NLP fallback generators.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/worker_m2_1
- Original parent: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Milestone: Milestone 2: Backend Stability & Schema Contexts

## 🔒 Key Constraints
- Support both Project contexts (`project_id`) and Standalone Document contexts (`document_id`).
- Offline local-NLP fallbacks must be robust and not fail when API keys are not provided or API calls fail.

## Current Parent
- Conversation ID: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Updated: not yet

## Task Summary
- **What to build**: Update models.py, main.py, and crud.py to support document_id; write schema patch logic; implement local-NLP fallbacks in concept_map.py; integrate fallbacks into endpoints.
- **Success criteria**: Tests pass, DB is patched on startup, offline generators work correctly when key starts with "AQ".
- **Interface contracts**: PROJECT.md / SCOPE.md
- **Code layout**: backend/db, backend/nlp, backend/main.py

## Key Decisions Made
- None yet.

## Artifact Index
- None yet.

## Change Tracker
- **Files modified**: None yet.
- **Build status**: TBD
- **Pending issues**: None.

## Quality Status
- **Build/test result**: TBD
- **Lint status**: TBD
- **Tests added/modified**: None.

## Loaded Skills
- None.
