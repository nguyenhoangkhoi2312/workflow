# Original User Request

## Initial Request — 2026-06-28T12:20:26+07:00

You are the Milestone 2 (Backend Stability & Schema Contexts) Sub-orchestrator (archetype: self).
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/sub_orch_m2.
Your parent is 46ac9098-2da1-4b75-9ea3-afc667e125d1 (Project Orchestrator).

Your task is to implement Milestone 2:
1. Initialize SCOPE.md under your working directory to define your plan and tracking.
2. Modify `backend/db/models.py` to support BOTH Project and Standalone Document contexts for Chats, Artifacts, and Flashcards (the User Rule):
   - Add `document_id` (Integer, ForeignKey("documents.id"), nullable=True) column to `ChatMessage` and `Artifact` tables.
   - Add `project_id` (Integer, ForeignKey("projects.id"), nullable=True) and `document_id` (Integer, ForeignKey("documents.id"), nullable=True) columns to `Flashcard` table.
3. Add a startup schema-patching routine in `backend/main.py` (e.g., at the top of `models.Base.metadata.create_all(bind=engine)`) to dynamically alter the SQLite tables (`chat_messages`, `artifacts`, `flashcards`) and add these columns if they do not exist. This ensures existing databases do not trigger sqlalchemy column errors.
4. Modify `backend/db/crud.py` to support these new fields (e.g., `create_flashcard`, `get_flashcards`, `get_due_flashcards` should filter or store by project_id/document_id context; `create_artifact`, `get_artifacts` should store and load by document_id; `save_chat_message`, `get_chat_history` should store and load by document_id).
5. Expose `/api/documents/url` in `backend/main.py` as an alias or direct endpoint for URL ingestion (alongside `/api/documents/ingest_url`) to resolve the frontend mismatch.
6. Implement robust offline local-NLP fallbacks for:
   - `/api/generate_exam_prep` and `/api/generate_study_plan` (avoid throwing 400/500 errors; instead extract content from document text using TextRank/TF-IDF and format as markdown study guide/plan).
   - `/api/generate_path` and `/api/suggestions` (instead of returning hardcoded static mocks, extract key terms/sentences from the document library to produce dynamic modules and suggestions).
   - In `backend/nlp/concept_map.py`, update `generate_concept_map` to populate `definition` and `formula` (extracted from document sentences where the concept word occurs) for each node, conforming to `ConceptNodeSchema`.
7. Test the backend endpoints to verify they do not crash and work offline correctly.
8. Document all your changes and verification tests in `handoff.md` and communicate completion back to the parent.

Ensure you spawn subagents (e.g. teamwork_preview_worker, teamwork_preview_challenger) to perform code changes and run tests. DO NOT write code yourself. Verbatim warning: DO NOT CHEAT. All implementations must be genuine.
