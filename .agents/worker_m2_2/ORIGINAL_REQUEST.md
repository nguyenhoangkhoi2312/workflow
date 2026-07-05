## 2026-06-28T09:30:03Z

You are Worker 2 (archetype: teamwork_preview_worker), a replacement for Worker 1.
Your working directory is /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/worker_m2_2.
Your task is to implement the code modifications for Milestone 2: Backend Stability & Schema Contexts.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please execute the following tasks:
1. Read the changes from /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_1/changes.patch. Apply these database models, CRUD, and API endpoint updates to the codebase:
   - Make the database schema changes in `backend/db/models.py` (making ChatMessage and Artifact project_id columns nullable and adding document_id; adding project_id and document_id to Flashcard).
   - Implement the schema patching function in `backend/main.py` and run it on startup before `Base.metadata.create_all(bind=engine)`.
   - Update `backend/db/crud.py` to filter/save messages, artifacts, and flashcards by both `project_id` and `document_id`.
   - Expose `/api/documents/url` in `backend/main.py` as an alias for `/api/documents/ingest_url` using stacked FastAPI decorators:
     ```python
     @app.post("/api/documents/ingest_url")
     @app.post("/api/documents/url")
     def ingest_url(request: UrlIngestRequest, db: Session = Depends(get_db)):
     ```
   - Update API routes in `backend/main.py` (like `/api/chat`, `/api/generate_flashcards`, `/api/flashcards/due`, `/api/generate_quiz`, `/api/generate_exam_prep`, `/api/generate_study_plan`) to accept, pass, and save both project_id and document_id parameters, and to query artifacts/messages by document_id as well.

2. Implement offline local-NLP fallbacks:
   - In `backend/nlp/concept_map.py`, add `_extract_definition_and_formula(concept, sentences, is_vn=False)` helper to extract concept definition and formula from the sentences. Update `generate_concept_map` and `_vietnamese_concept_map` to populate `definition` and `formula` on concept nodes returned to the frontend (conforming to `ConceptNodeSchema`).
   - Implement the offline generator functions `generate_offline_exam_prep(text)`, `generate_offline_study_plan(text)`, `generate_offline_learning_path(topic, db=None)`, and `generate_offline_suggestions(text)` in `backend/nlp/concept_map.py` (or a similar module). Use TF-IDF sentence centrality, text parsing, and heuristics as described in the analysis report `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_3/analysis.md`.
   - In `backend/main.py`, integrate these offline NLP generators into `/api/generate_exam_prep`, `/api/generate_study_plan`, `/api/generate_path`, and `/api/suggestions`. Make sure that when the API key is not provided (e.g. starts with "AQ"), or when the AI agent call fails, the endpoints catch the error, run the offline generator, save the generated artifact if appropriate, and return it without returning 400 or 500 error codes.

3. Run build/tests inside the `backend` directory using `pytest` or any available test runner, and verify they pass.
4. Write your implementation report to your folder.
5. Report back when finished.
