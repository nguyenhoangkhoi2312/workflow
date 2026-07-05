# explorer_m6_investigation Handoff Report

## 1. Observation
The following direct observations were made during the read-only investigation:

- **Database models in `backend/db/models.py`**:
  Lines 34–45:
  ```python
  class RoadmapItem(Base):
      __tablename__ = "roadmap_items"

      id = Column(Integer, primary_key=True, index=True)
      roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
      step_number = Column(Integer)
      title = Column(String)
      description = Column(String, nullable=True)
      completed = Column(Integer, default=0) # 0 or 1 for boolean

      roadmap = relationship("Roadmap", back_populates="items")
  ```
  The table contains a `completed` column (type `Integer`) but no column for active topic tracking (e.g. `active`).

- **Database schema patching in `backend/main.py`**:
  Lines 50–87:
  ```python
  def patch_database_schema(engine):
      from sqlalchemy import inspect, text
      inspector = inspect(engine)
      
      with engine.begin() as conn:
          if "users" in inspector.get_table_names():
              ...
  ```
  This routine automatically patches tables at runtime using raw SQL `ALTER TABLE` statements to ensure backward compatibility.

- **Vite application layout in `src/components/layout/AppLayout.jsx`**:
  Line 27:
  ```javascript
  {isDocumentView ? <ProjectStudioSidebar selectedPersona={selectedPersona} setSelectedPersona={setSelectedPersona} /> : <StudioSidebar />}
  ```
  The `ProjectStudioSidebar` is rendered on the right side of the main layout, as a right sidebar.

- **Roadmap rendering in `src/components/layout/ProjectStudioSidebar.jsx`**:
  Lines 208–229:
  ```javascript
  roadmapItems.map((item, idx) => (
    <div key={item.id} style={{ display: 'flex', gap: '16px', position: 'relative', paddingBottom: idx === roadmapItems.length - 1 ? '0' : '20px' }}>
      {idx !== roadmapItems.length - 1 && (
        <div style={{ position: 'absolute', left: '11px', top: '24px', bottom: '0', width: '2px', backgroundColor: 'var(--border-medium)', zIndex: 1 }}></div>
      )}
      <div style={{ flex: '0 0 auto', position: 'relative', zIndex: 2 }}>
        <div style={{ 
          width: '24px', height: '24px', borderRadius: '50%', 
          backgroundColor: item.completed ? 'var(--brand-primary)' : 'white', 
          border: `2px solid ${item.completed ? 'var(--brand-primary)' : 'var(--border-medium)'}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: item.completed ? 'white' : 'var(--text-muted)'
        }}>
          {item.completed ? <Check size={14} strokeWidth={3} /> : <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>{item.step_number}</span>}
        </div>
      </div>
      <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid var(--border-light)', padding: '12px', borderRadius: '12px', boxShadow: 'var(--shadow-sm)' }}>
        <h4 style={{ margin: '0 0 4px', fontSize: '0.85rem', fontWeight: 700, color: '#1B2A4E' }}>{item.title}</h4>
        <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{item.description}</p>
      </div>
    </div>
  ))
  ```
  The checklist container lacks click bindings on the circle/card elements and visual active highlighting.

- **Browser state from AppleScript inspection**:
  We ran `osascript` to get tab URLs in the open Google Chrome browser:
  ```
  1, :, 1, - hopeful-galileo, - http://localhost:5173/documents#/document/1
  1, :, 2, - Inspect with Chrome Developer Tools, - chrome://inspect/#remote-debugging
  1, :, 3, - Omilearn - AI học tập, lộ trình học và ôn tập thông minh, - https://omilearn.com/project
  ```
  This confirmed that Chrome exposes the main local development environment alongside the reference OmiLearn site.

- **Test suite infrastructure in `run_e2e_tests.py`**:
  Line 51:
  ```python
  cmd = [venv_python, "-m", "pytest", "tests/e2e", "--junitxml=tests_result.xml", "-v"]
  ```
  The project test suite is run by calling `python3 run_e2e_tests.py` to trigger pytest in `tests/e2e`.

---

## 2. Logic Chain
1. Since the `RoadmapItem` model has a `completed` integer column (representing status) but there are no endpoints in `backend/main.py` nor CRUD queries in `backend/db/crud.py` to alter it, we cannot toggle progress from the frontend.
2. Since there is no database column in either `Roadmap` or `RoadmapItem` to mark an active/selected step, active topic selection cannot currently be persisted.
3. Adding `active = Column(Integer, default=0)` to `RoadmapItem` represents the cleanest, most migration-safe way to store active topic selection in SQLite without creating circular table references or heavy migrations.
4. Because the `patch_database_schema` routine automatically manages SQLite table extensions, we must update it to include the `active` column so the database migrates cleanly without manual SQLite commands.
5. In `ProjectStudioSidebar.jsx`, because the elements lack click handlers, we must bind circle click to a `completed` toggle patch request, and card container click to an `active` selection patch request.
6. To make active selection functional, we can retrieve the active step in `chat_endpoint` inside `main.py` and prepend its description to the system prompt context. This makes the AI tutor context-aware of the current topic.

---

## 3. Caveats
- No remote debugger inspection of OmiLearn's inner styles was completed since Chrome's loopback debugger returned 404. However, AppleScript was successfully used to map local and external tab states, and the OmiLearn-specific styling rules (maroon colors, soft tan lines, cream background cards) were derived directly from the application's rules context.
- We assumed the SQLite DB can be altered dynamically using the existing `patch_database_schema(engine)` handler on startup; this was tested and proven by prior schema modifications in the codebase.

---

## 4. Conclusion
We have mapped the codebase layout and created a comprehensive technical implementation plan in `analysis.md` to build the interactive "Giáo án" (Study Plan / Roadmap progress tracker) feature. It details model extensions, CRUD functions, HTTP endpoints, AI prompt integrations, frontend styling changes, and testing strategies.

---

## 5. Verification Method
To independently verify this design and follow-up implementation:
1. **Inspecting Design**: Verify the details in `.agents/explorer_m6_investigation/analysis.md` for completeness.
2. **Database Verification**: Ensure `models.py` has `active = Column(Integer, default=0)` on `RoadmapItem`. Verify table updates by starting the backend and opening SQLite:
   ```bash
   sqlite3 backend/omilearn_local.db ".schema roadmap_items"
   ```
   Ensure the `active` column is present.
3. **E2E Test Execution**: Run the test suite:
   ```bash
   python3 run_e2e_tests.py
   ```
   Assert that newly written tests in `tests/e2e/test_tier1_feature_coverage.py` targeting `/api/roadmap/items/{item_id}` pass.
