# Original User Request

## Initial Request — 2026-06-29T07:52:27+07:00

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Execute the Teamwork Multi-Agent System on the Project

Implement the interactive "Giáo án" (Study Plan / Roadmap progress tracker) in the Project Studio Sidebar exactly as it appears in Workflow. The feature should display a vertical timeline of study topics, highlight the active topic, and integrate with existing backend APIs to persist user progress.

Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo
Integrity mode: development

## Requirements

### R1. Interactive Study Plan UI in Sidebar
Build the "Giáo án" section inside the left Studio Sidebar (`ProjectStudioSidebar.jsx`). It must display the generated study plan as a vertical list of numbered topics with title and subtext. The UI must match the aesthetic shown in the reference screenshots (status chips, pink/red highlighting for active items).

### R2. Backend Integration & Persistence
The UI must not just use mock data; it must connect to the existing backend APIs (`generate_path` or `generate_study_plan`). The roadmap data must be saved to the database (SQLite) so that the user's progress and active topic state are persisted across page reloads.

### R3. Action Buttons & Navigation
Include "Tạo giáo án" and "Dùng LLM" buttons at the bottom of the list. Clicking "Tạo giáo án" should open the existing configuration modal we just built (`CreateLessonPlanModal` or `StudyPlanModal`). The user should be able to click on different topics to switch the active context.

### R4. Browser Investigation
Use the `browser` subagent (connecting to Chrome DevTools at `127.0.0.1:9222`) to inspect Workflow's implementation of this UI component and replicate its behavior and styling accurately.

## Acceptance Criteria

### UI / UX
- [ ] The Sidebar correctly displays the "Giáo án" section with a vertical timeline of topics.
- [ ] The active topic is visually distinct (pink background, bold red text) from inactive ones.

### Functionality
- [ ] The generated roadmap/study plan is persisted in the database.
- [ ] Reloading the page retains the study plan and the currently active topic.
- [ ] The "Tạo giáo án" button successfully opens the configuration modal.

### Verification Mechanism
- **Programmatic / Agent-as-Judge**: The teamwork agents must write an automated integration test or use the browser agent to click through the local application, generate a study plan, verify it appears in the sidebar, click a topic, reload the page, and assert that the state persists.
