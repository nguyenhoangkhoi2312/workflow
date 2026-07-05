# BRIEFING — 2026-06-28T16:36:16+07:00

## Mission
Empirically challenge and verify correctness of the offline NLP fallback functions (`generate_offline_exam_prep`, `generate_offline_study_plan`, `generate_offline_learning_path`, and `generate_offline_suggestions`) and run E2E test suite.

## 🔒 My Identity
- Archetype: teamwork_preview_challenger
- Roles: critic, specialist
- Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/challenger_m2_1
- Original parent: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Milestone: Milestone 2
- Instance: 1 of 1

## 🔒 Key Constraints
- Review-only — do NOT modify implementation code
- Run verification code empirically (do not trust logs/claims)
- Write challenge report to `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/challenger_m2_1/challenge.md`

## Current Parent
- Conversation ID: 5a43dc16-2746-417e-b1fe-966ca61856b2
- Updated: 2026-06-28T16:38:50+07:00

## Review Scope
- **Files to review**: backend/nlp/concept_map.py, backend/nlp/vietnamese.py
- **Interface contracts**: schemas for NLP fallback outputs
- **Review criteria**: correctness, schema conformance, no errors under extreme inputs (empty, long, special, non-ASCII)

## Key Decisions Made
- Created and ran a custom stress-testing harness (`backend/stress_test_nlp.py`) verifying all four offline fallback functions against edge inputs.
- Verified E2E test suite by executing `python run_e2e_tests.py` and obtaining 71/71 passing tests.

## Artifact Index
- `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/challenger_m2_1/challenge.md` — Challenge report

## Attack Surface
- **Hypotheses tested**: Checked robustness of local fallback functions when processing empty text, null bytes, special characters, unicode text, very long English text (>1,000,000 chars), and very long Vietnamese text.
- **Vulnerabilities found**: Confirmed `ValueError: [E088]` in spaCy when processing non-Vietnamese texts longer than 1,000,000 characters in `generate_offline_exam_prep`, `generate_offline_study_plan`, `generate_offline_suggestions`, and `generate_offline_learning_path` (when accessing a document exceeding spaCy's max length).
- **Untested angles**: Pyvi performance degradation under very large payloads was only bounded by reducing the test run multipliers (no native limit is enforced in code, potentially leading to high latency/resource usage).

## Loaded Skills
- None loaded.

