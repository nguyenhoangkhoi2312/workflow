## 2026-06-29T00:56:09Z
Implement the interactive "Giáo án" (Study Plan / Roadmap progress tracker) in the Project Studio Sidebar with backend persistence (SQLite).

Follow the design in `.agents/explorer_m6_investigation/analysis.md` and ensure compliance with all project rules in `.agents/AGENTS.md`.

Here is the exact task list:

1. **Backend Database & Schema Updates**:
   - In `backend/db/models.py`, add `active` column (type `Integer`, default `0`) to `RoadmapItem`.
   - In `backend/main.py`'s `patch_database_schema` routine, add an automated SQLite ALTER TABLE statement to add the `active` column to `roadmap_items` if it does not exist.

2. **Backend CRUD & API Endpoint Development**:
   - In `backend/db/crud.py`, add `update_roadmap_item(db: Session, item_id: int, completed: bool = None, active: bool = None)` to toggle `completed` status and `active` status. When `active` is set to `True`, deactivate all other items in the same roadmap.
   - In `backend/main.py`, define the request schema `RoadmapItemUpdate` and add the `PATCH /api/roadmap/items/{item_id}` endpoint.
   - Update `GET /api/projects/{project_id}/roadmap` and `GET /api/documents/{document_id}/roadmap` in `backend/main.py` to return the `active` attribute for each roadmap item.
   - In `backend/main.py`'s `chat_endpoint`, fetch the active roadmap item for the project or document, and prepend its details (title and description) to the system prompt context so the AI tutor is context-aware of the current topic.

3. **Frontend Sidebar UI Integration**:
   - Modify `src/components/layout/ProjectStudioSidebar.jsx` to fetch the `active` status of roadmap items.
   - Bind click handlers:
     - Click on the checkbox circle toggles `completed` status via `PATCH /api/roadmap/items/{item_id}`.
     - Click on the card container toggles `active` selection status via `PATCH /api/roadmap/items/{item_id}`.
   - Apply CSS styling matching the OmiLearn style guidelines:
     - Circles: completed has maroon background (`#8A334C`) and checkmark; pending has thin tan/grey border (`#D6C5B3`) and step number.
     - Active Card: background beige cream (`#FDF8F5`), border `2px solid #8A334C`, title text bold Maroon (`#8A334C`), subtle box-shadow.
     - Inactive Card: background White, border `1px solid var(--border-light)`, title text navy (`#1B2A4E`).
     - Connection Line: center-aligned vertical lines with `#D6C5B3` color.
   - Implement action buttons inside the active card:
     - **Hỏi AI (Chat)**: Prefills the chat input text box/textarea with `Hãy hướng dẫn tôi học chủ đề "[Title]": [Description]` and triggers an input event.
     - **Tạo Quiz**: A button with placeholder alert/link action as appropriate.

4. **Verification**:
   - Add new E2E tests in `tests/e2e/test_tier1_feature_coverage.py` and `tests/e2e/test_tier2_boundary_corner.py` targeting the new patch endpoint, status toggling, and active item switching.
   - Run `python3 run_e2e_tests.py` to ensure all tests pass (71+ tests).

**MANDATORY INTEGRITY WARNING**:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please report your progress and write your final handoff in `.agents/worker_m6_implementation/handoff.md`.
