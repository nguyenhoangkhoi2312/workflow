# Original Request

## 2026-06-28T12:20:17+07:00

You are the E2E Testing Track Orchestrator (archetype: self).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/sub_orch_e2e.
Your parent is 46ac9098-2da1-4b75-9ea3-afc667e125d1 (Project Orchestrator).

Your mission is to build the E2E Test Suite and infrastructure for the Omilearn application.
You must follow the instructions in the E2E Testing Track section of the parent's instructions.
Specifically:
1. Initialize SCOPE.md under your working directory defining your plan and milestones.
2. Design and implement a comprehensive test suite (e.g. in `tests/e2e/` or similar) in Python. The tests must run against the backend running on http://127.0.0.1:8000.
3. Design test cases based on the 4-tier approach for the 6 core features:
   - F1: Document ingestion (Upload & URL link)
   - F2: Roadmap generation (both Project & Standalone Document contexts)
   - F3: Quiz generation, submission, and document progress tracking
   - F4: AI / NLP study materials & offline fallbacks (Exam prep, Study plan, Concept map, Suggestions, Learning path)
   - F5: Flashcard generation, due list, and SM-2 spaced repetition updates
   - F6: Project and Standalone Document collaboration (Invites and member listings)
4. Minimum thresholds:
   - Tier 1 (Feature Coverage): at least 30 test cases (5 per feature)
   - Tier 2 (Boundary & Corner Cases): at least 30 test cases (5 per feature)
   - Tier 3 (Cross-Feature combinations): at least 6 test cases
   - Tier 4 (Real-World Application): at least 5 scenarios
5. Write the test runner script or configure pytest so that running a single command runs the entire test suite.
6. Create `TEST_INFRA.md` at the project root detailing your test philosophy, features inventory, test architecture, and scenarios.
7. Once the tests are fully developed, run them (expect failures on features that are not yet fixed by the implementation track) and publish `TEST_READY.md` at the project root.
8. Update progress.md in your working directory and communicate status back to the parent.

Ensure you spawn subagents (e.g. teamwork_preview_worker, teamwork_preview_challenger) to do the actual code writing and execution verification. DO NOT write code yourself.
