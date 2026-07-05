## 2026-06-29T00:59:02Z
Perform a forensic integrity audit on the interactive "Giáo án" (Roadmap progress tracker) implementation.

Inspect the codebase files modified by the worker:
- `backend/db/models.py`
- `backend/db/crud.py`
- `backend/main.py`
- `src/components/layout/ProjectStudioSidebar.jsx`
- `tests/e2e/test_tier1_feature_coverage.py`
- `tests/e2e/test_tier2_boundary_corner.py`

Check for:
1. Hardcoded test results or expected values to bypass tests.
2. Dummy/facade implementations.
3. Circumventing tasks using external APIs/tools.
4. Branding compliance (no OmiLearn/OmiGuide leaks in user-facing UI).
5. Proper project/document context handling.

Write your final audit verdict and report to `.agents/auditor_m6/handoff.md`. Indicate clearly if the audit is CLEAN or if there is an INTEGRITY VIOLATION.
