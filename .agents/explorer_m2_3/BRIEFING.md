# BRIEFING — 2026-06-28T05:20:43Z

## Mission
Analyze Offline local-NLP fallbacks and concept map definition/formula extraction for Milestone 2.

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: explorer
- Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_3
- Original parent: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Milestone: Milestone 2

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Focus on offline local-NLP fallbacks for specific endpoints and backend/nlp/concept_map.py analysis

## Current Parent
- Conversation ID: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Updated: 2026-06-28T05:20:43Z

## Investigation State
- **Explored paths**:
  - `backend/main.py` (endpoints `/api/generate_exam_prep`, `/api/generate_study_plan`, `/api/generate_path`, `/api/suggestions`)
  - `backend/nlp/concept_map.py` (functions `generate_concept_map` and `_vietnamese_concept_map`)
  - `backend/nlp/quizzes.py` and `backend/nlp/notes.py` (for extraction reference)
  - `backend/nlp/vietnamese.py` (for language checks and sentence splits)
- **Key findings**:
  - Identified endpoints currently lack robust offline fallback mechanisms; some raise 400/500 errors, and others use static hardcoded templates.
  - `backend/nlp/concept_map.py` lacks definition and formula extraction for generated concept nodes.
  - Formulated a comprehensive local NLP fallback strategy using TF-IDF sentence centrality, chronological text partitioning, database similarity matching, and regex/indicator-based heuristics.
- **Unexplored areas**:
  - Frontend interaction with mock offline keys during testing.

## Key Decisions Made
- Confirmed strict alignment with read-only constraint.
- Propose new local NLP fallback functions: `generate_offline_exam_prep`, `generate_offline_study_plan`, `generate_offline_learning_path`, `generate_offline_suggestions`.
- Propose matching sentence heuristics `_extract_definition_and_formula` for concept maps.

## Artifact Index
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_3/analysis.md — Detailed analysis and proposed fix strategy
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_3/handoff.md — Handoff report
- /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_3/progress.md — Progress tracker
