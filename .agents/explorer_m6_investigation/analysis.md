# Analysis & Design Report: Interactive "Giáo án" (Roadmap) Feature

This report documents the current architecture of the Roadmap ("Giáo án") feature and outlines a concrete implementation plan for making it interactive with backend persistence, active topic selection, and OmiGuide-compliant UI.

---

## 1. Backend Current State & Gap Analysis

We researched the backend files (`backend/db/models.py`, `backend/db/crud.py`, `backend/main.py`) to examine how the roadmap is structured, generated, and served.

### A. Database Models (`backend/db/models.py`)
Currently, the roadmap tables are defined as follows:
- **`Roadmap`**:
  - `id`: Primary key
  - `project_id`: Nullable integer (foreign key to `projects.id`)
  - `document_id`: Nullable integer (foreign key to `documents.id`)
  - `created_at`: Datetime
  - `items`: Relationship to `RoadmapItem` with cascade delete.
- **`RoadmapItem`**:
  - `id`: Primary key
  - `roadmap_id`: ForeignKey to `roadmaps.id`
  - `step_number`: Integer
  - `title`: String
  - `description`: String (nullable)
  - `completed`: Integer (default `0`) - acts as boolean (`0` = pending, `1` = completed)

**What is missing:**
1. **Persistence of Active Topic Selection**: There is no column to represent which roadmap item is currently active (highlighted) for the project or document.
2. **Schema Migration Support**: Adding a new column directly to SQLite will fail for existing databases without a patching routine.

**Design Recommendation:**
We recommend adding an `active = Column(Integer, default=0)` (representing boolean active/inactive state) to the `RoadmapItem` model.
- **Rationale**: Storing `active` on the item is highly robust. When an item is set to active (`1`), the backend will automatically set `active` to `0` for all other items in the same roadmap. This avoids circular foreign keys or complex schema alterations on the parent `Roadmap` table.

### B. Database CRUD (`backend/db/crud.py`)
Currently, `crud.py` only implements:
- `create_roadmap(db, project_id, items)`: Deletes previous roadmaps/items for a project and creates a new one. (Note: Project vs. Standalone Document logic is split; standalone uses inline DB operations in `main.py`).
- `get_roadmap(db, project_id)`: Fetches the latest roadmap for a project.

**What is missing:**
1. **Interactive Updates**: A CRUD function to update `completed` status and `active` selection status of a `RoadmapItem`.

### C. API Endpoints (`backend/main.py`)
Current endpoints:
- `GET /api/projects/{project_id}/roadmap`
- `POST /api/projects/{project_id}/roadmap/generate`
- `GET /api/documents/{document_id}/roadmap`
- `POST /api/documents/{document_id}/roadmap/generate`

**What is missing:**
1. **Update API Endpoint**: A `PATCH /api/roadmap/items/{item_id}` endpoint to update the `completed` or `active` fields of a specific step.
2. **AI Chat Integration**: The chatbot endpoint (`POST /api/chat`) does not include the currently active roadmap step title and description in the prompting context, so the AI is unaware of what the user is currently studying.

---

## 2. Frontend Current State & Gap Analysis

We researched `src/components/layout/ProjectStudioSidebar.jsx` and `src/components/modals/StudyPlanModal.jsx`.

### A. Project Studio Sidebar Layout & Style
- `ProjectStudioSidebar.jsx` serves as the right sidebar inside the workspace view (`AppLayout.jsx` renders it on the right).
- The **"GIÁO ÁN"** section renders a vertical timeline of `roadmapItems`:
  - Circle on the left shows checkmark (if `completed`) or step number.
  - Line on the left connects circles vertically.
  - Card on the right shows title and description.
- **The Gap**:
  - Clicking the circle does not toggle completion status.
  - The cards are not selectable/clickable.
  - There is no styling or layout highlighting for the active step.
  - There are no quick action buttons to study or trigger AI features for a step.

### B. Context Support (Project vs. Standalone Document)
- The sidebar fetches and generates roadmap items correctly under both contexts by detecting the URL context:
  - If URL starts with `/project/`, it sets `projectId` from URL and uses project endpoints.
  - Otherwise, it treats it as a standalone document context (`id` from useParams) and uses document endpoints.
- This dual-context support must be maintained when implementing the interactive toggling and active selection.

---

## 3. UI/UX Design for "Giáo án" (Timeline)

Aligned with the **OmiLearn** styling and constraints defined in `AGENTS.md`:
1. **Timeline Checkboxes (Step Circle)**:
   - Clicking the circle triggers a toggle between completed and pending states.
   - Visual: completed circles have a maroon background (`#8A334C`), while pending circles have a thin tan/grey border (`#D6C5B3`) with step numbers.
2. **Active Topic Highlight**:
   - Clicking a step card sets it as the active topic.
   - **Active Card Styles**:
     - Background: Warm light beige cream (`#FDF8F5` or `#FAFAF9`).
     - Border: `2px solid var(--brand-primary)` (`#8A334C`).
     - Shadow: Subtle glow (`0 4px 12px rgba(138, 51, 76, 0.1)`).
     - Title text: Bold Maroon color (`#8A334C`).
   - **Inactive Card Styles**:
     - Background: Pure White (`#FFFFFF`).
     - Border: `1px solid var(--border-light)` (`#E5E7EB`).
     - Title text: Dark navy color (`#1B2A4E`).
3. **Connecting Lines**:
   - Sleek 2px vertical lines centered behind the circles.
   - Color: Tan border color (`#D6C5B3`).
4. **Action Buttons (Pills) inside Active Card**:
   - In OmiGuide, learning tools must be easily accessible. We will add a small row of action links or icon pills at the bottom of the active card:
     - **Hỏi AI (Chat)**: Prefills chat input with `"Hãy giảng giải chi tiết về chủ đề: [Title] trong tài liệu."` and sends it.
     - **Tạo Quiz**: Triggers quiz generation for this specific topic scope.
     - **Luyện Flashcard**: Directs user to flashcard review for the topic.

---

## 4. Technical Implementation Plan

### Part 1: Backend Database & Schema Changes
1. **Model Modification (`backend/db/models.py`)**:
   Add `active` column to `RoadmapItem`:
   ```python
   class RoadmapItem(Base):
       __tablename__ = "roadmap_items"
       id = Column(Integer, primary_key=True, index=True)
       roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
       step_number = Column(Integer)
       title = Column(String)
       description = Column(String, nullable=True)
       completed = Column(Integer, default=0)
       active = Column(Integer, default=0) # New: 0 or 1 for active selection status
   ```

2. **Schema Migration Routine (`backend/main.py`)**:
   Update `patch_database_schema` to dynamically inject the `active` column on startup for existing SQLite databases:
   ```python
   if "roadmap_items" in inspector.get_table_names():
       cols = [c["name"] for c in inspector.get_columns("roadmap_items")]
       if "active" not in cols:
           conn.execute(text("ALTER TABLE roadmap_items ADD COLUMN active INTEGER DEFAULT 0"))
   ```

### Part 2: Backend CRUD & API Endpoints
1. **CRUD Functions (`backend/db/crud.py`)**:
   Add `update_roadmap_item` to handle updating properties:
   ```python
   def update_roadmap_item(db: Session, item_id: int, completed: bool = None, active: bool = None):
       db_item = db.query(models.RoadmapItem).filter(models.RoadmapItem.id == item_id).first()
       if not db_item:
           return None
       
       if completed is not None:
           db_item.completed = 1 if completed else 0
           
       if active is not None:
           if active:
               # Deactivate all other items in the same roadmap
               db.query(models.RoadmapItem).filter(
                   models.RoadmapItem.roadmap_id == db_item.roadmap_id,
                   models.RoadmapItem.id != item_id
               ).update({models.RoadmapItem.active: 0})
               db_item.active = 1
           else:
               db_item.active = 0
               
       db.commit()
       db.refresh(db_item)
       return db_item
   ```

2. **Create Request Schema (`backend/main.py`)**:
   ```python
   class RoadmapItemUpdate(BaseModel):
       completed: bool | None = None
       active: bool | None = None
   ```

3. **Expose Endpoints (`backend/main.py`)**:
   Create the route for item updates:
   ```python
   @app.patch("/api/roadmap/items/{item_id}")
   async def update_roadmap_item_endpoint(item_id: int, req: RoadmapItemUpdate, db: Session = Depends(get_db)):
       item = crud.update_roadmap_item(db, item_id=item_id, completed=req.completed, active=req.active)
       if not item:
           raise HTTPException(status_code=404, detail="Roadmap item not found")
       return {
           "id": item.id,
           "step_number": item.step_number,
           "title": item.title,
           "description": item.description,
           "completed": item.completed,
           "active": item.active
       }
   ```
   Modify `GET` endpoints for project/document roadmaps to return `active` status:
   ```python
   # Return active attribute
   return {"items": [{"id": i.id, "step_number": i.step_number, "title": i.title, "description": i.description, "completed": i.completed, "active": i.active} for i in sorted(roadmap.items, key=lambda x: x.step_number)]}
   ```

4. **Enhance Chat AI Context (`backend/main.py` in `chat_endpoint`)**:
   Extract active step from DB and inject it into prompt context:
   ```python
   active_step_context = ""
   if request.project_id:
       rm = db.query(models.Roadmap).filter(models.Roadmap.project_id == request.project_id).first()
       if rm:
           active_item = db.query(models.RoadmapItem).filter(models.RoadmapItem.roadmap_id == rm.id, models.RoadmapItem.active == 1).first()
           if active_item:
               active_step_context = f"Chủ đề người học đang tập trung trong lộ trình: '{active_item.title}' - Mô tả: '{active_item.description}'."
   elif request.document_id:
       rm = db.query(models.Roadmap).filter(models.Roadmap.document_id == request.document_id).first()
       if rm:
           active_item = db.query(models.RoadmapItem).filter(models.RoadmapItem.roadmap_id == rm.id, models.RoadmapItem.active == 1).first()
           if active_item:
               active_step_context = f"Chủ đề người học đang tập trung trong lộ trình: '{active_item.title}' - Mô tả: '{active_item.description}'."
               
   # Prepend to persona prompt
   if active_step_context:
       persona_prompt = f"{active_step_context}\n{persona_prompt}"
   ```

### Part 3: Frontend Project Studio Sidebar
1. **Interactive Toggle and Select Logic (`src/components/layout/ProjectStudioSidebar.jsx`)**:
   Add handlers to toggle completion and select active status:
   ```javascript
   const handleToggleCompleted = async (itemId, currentCompleted) => {
     try {
       const res = await fetch(`http://127.0.0.1:8000/api/roadmap/items/${itemId}`, {
         method: 'PATCH',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ completed: !currentCompleted })
       });
       if (res.ok) {
         setRoadmapItems(prev => prev.map(item => 
           item.id === itemId ? { ...item, completed: !currentCompleted } : item
         ));
       }
     } catch (err) {
       console.error(err);
     }
   };

   const handleSelectActive = async (itemId, currentActive) => {
     try {
       const res = await fetch(`http://127.0.0.1:8000/api/roadmap/items/${itemId}`, {
         method: 'PATCH',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ active: !currentActive })
       });
       if (res.ok) {
         setRoadmapItems(prev => prev.map(item => 
           item.id === itemId 
             ? { ...item, active: !currentActive } 
             : { ...item, active: false } // de-activate others locally
         ));
       }
     } catch (err) {
       console.error(err);
     }
   };
   ```

2. **Render Updates in UI**:
   Update timeline list container to bind clicks and display states:
   ```javascript
   roadmapItems.map((item, idx) => {
     const isActive = !!item.active;
     const isCompleted = !!item.completed;
     
     return (
       <div key={item.id} style={{ display: 'flex', gap: '16px', position: 'relative', paddingBottom: idx === roadmapItems.length - 1 ? '0' : '20px' }}>
         {idx !== roadmapItems.length - 1 && (
           <div style={{ position: 'absolute', left: '11px', top: '24px', bottom: '0', width: '2px', backgroundColor: '#D6C5B3', zIndex: 1 }}></div>
         )}
         
         {/* Checkbox circle trigger completed toggle */}
         <div 
           onClick={() => handleToggleCompleted(item.id, isCompleted)}
           style={{ flex: '0 0 auto', position: 'relative', zIndex: 2, cursor: 'pointer' }}
         >
           <div style={{ 
             width: '24px', height: '24px', borderRadius: '50%', 
             backgroundColor: isCompleted ? '#8A334C' : 'white', 
             border: `2px solid ${isCompleted ? '#8A334C' : '#D6C5B3'}`,
             display: 'flex', alignItems: 'center', justifyContent: 'center',
             color: isCompleted ? 'white' : 'var(--text-muted)',
             transition: 'all 0.2s'
           }}>
             {isCompleted ? <Check size={14} strokeWidth={3} /> : <span style={{ fontSize: '0.7rem', fontWeight: 700 }}>{item.step_number}</span>}
           </div>
         </div>
         
         {/* Step card trigger active select */}
         <div 
           onClick={() => handleSelectActive(item.id, isActive)}
           style={{ 
             flex: 1, 
             backgroundColor: isActive ? '#FDF8F5' : 'white', 
             border: isActive ? '2px solid #8A334C' : '1px solid var(--border-light)', 
             padding: '12px', 
             borderRadius: '12px', 
             boxShadow: isActive ? '0 4px 12px rgba(138, 51, 76, 0.1)' : 'var(--shadow-sm)',
             cursor: 'pointer',
             transition: 'all 0.2s'
           }}
         >
           <h4 style={{ margin: '0 0 4px', fontSize: '0.85rem', fontWeight: 700, color: isActive ? '#8A334C' : '#1B2A4E' }}>{item.title}</h4>
           <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{item.description}</p>
           
           {/* Context-Driven Study Pills for Active Item */}
           {isActive && (
             <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
               <button 
                 onClick={(e) => {
                   e.stopPropagation();
                   // Bind custom text to parent/document chat prompt or input
                   const chatInput = document.querySelector('input[type="text"], textarea');
                   if (chatInput) {
                     const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                     setter.call(chatInput, `Hãy hướng dẫn tôi học chủ đề "${item.title}": ${item.description}`);
                     chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                   }
                 }}
                 style={{ background: 'transparent', border: '1px solid #8A334C', color: '#8A334C', padding: '4px 8px', borderRadius: '16px', fontSize: '0.65rem', fontWeight: 700, cursor: 'pointer' }}
               >
                 Hỏi AI
               </button>
               <button 
                 onClick={(e) => {
                   e.stopPropagation();
                   alert("Chuyển sang module luyện thi / quiz của bước này.");
                 }}
                 style={{ background: 'transparent', border: '1px solid #D6C5B3', color: 'var(--text-secondary)', padding: '4px 8px', borderRadius: '16px', fontSize: '0.65rem', fontWeight: 600, cursor: 'pointer' }}
               >
                 Tạo Quiz
               </button>
             </div>
           )}
         </div>
       </div>
     );
   })
   ```

---

## 5. E2E Test Strategy

To verify this implementation, we will update E2E tests:
1. **Tier 1 (Happy Path)**:
   Add tests in `tests/e2e/test_tier1_feature_coverage.py` under the roadmap section:
   - Get project/document roadmap items.
   - Pick first roadmap item.
   - Send `PATCH /api/roadmap/items/{item_id}` to set `completed` to `true`.
   - Re-retrieve roadmap, assert `completed` is indeed `1` for that item.
   - Send `PATCH /api/roadmap/items/{item_id}` to set `active` to `true`.
   - Re-retrieve roadmap, assert `active` is `1` for that item and `0` for all other items.
2. **Tier 2 (Boundary Cases)**:
   Add checks in `tests/e2e/test_tier2_boundary_corner.py`:
   - Send update request to non-existent `item_id` (assert 404).
   - Send invalid payload fields (assert validation failure).
   - Toggle completion status back and forth multiple times.
