## 2026-06-29T08:05:45+07:00
Remediate the missing UI components reported by the Victory Auditor.

Specifically:
1. In `src/components/layout/ProjectStudioSidebar.jsx`:
   - Import `CreateLessonPlanModal` from `../modals/CreateLessonPlanModal`.
   - Add state `isCreateLessonPlanOpen` initialized to `false`.
   - Add "Tạo giáo án" and "Dùng LLM" buttons at the bottom of the "GIÁO ÁN" list container (right after the list of `roadmapItems`).
     - Clicking "Tạo giáo án" should set `isCreateLessonPlanOpen(true)` to open the `CreateLessonPlanModal`.
     - Clicking "Dùng LLM" should trigger the existing `generateRoadmap` function in the sidebar.
     - Style these buttons using the OmiGuide/Workflow aesthetics (light cream `#FDF8F5`, maroon `#8A334C` colors, and thin tan borders `#D6C5B3`).
   - Render the `<CreateLessonPlanModal isOpen={isCreateLessonPlanOpen} onClose={() => setIsCreateLessonPlanOpen(false)} projectId={projectId} documentId={isProject ? null : id} onSuccess={fetchData} />` component at the bottom of the JSX return.
2. Run the build `npm run build` and the E2E tests `python3 run_e2e_tests.py` to ensure everything compiles and passes cleanly (74 tests).
3. Report your findings and write your final handoff in `.agents/worker_m6_victory_remediation/handoff.md`.
