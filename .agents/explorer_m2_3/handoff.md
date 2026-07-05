# Handoff Report - Explorer 3

## 1. Observation

Direct observations made in the codebase:

- **API Endpoints**:
  - `/api/generate_exam_prep` (`backend/main.py:899`):
    ```python
    @app.post("/api/generate_exam_prep")
    async def generate_exam_prep_endpoint(request: TopicRequest, db: Session = Depends(get_db)):
    ```
    Raises `HTTPException(status_code=400, detail="No valid AI key provided for exam prep.")` when no API key is provided and raises `HTTPException(status_code=500, detail="AI processing failed for exam prep.")` upon failure.
  - `/api/generate_study_plan` (`backend/main.py:934`):
    ```python
    @app.post("/api/generate_study_plan")
    async def generate_study_plan_endpoint(request: TopicRequest, db: Session = Depends(get_db)):
    ```
    Raises `HTTPException(status_code=400, detail="No valid AI key provided for study plan.")` when no API key is provided and raises `HTTPException(status_code=500, detail="AI processing failed for study plan.")` upon failure.
  - `/api/generate_path` (`backend/main.py:740`):
    ```python
    @app.post("/api/generate_path")
    async def generate_path(request: LearningPathRequest, x_api_key: str | None = Header(default=None)):
    ```
    Returns a static dictionary when `current_key` is None/starts with "AQ":
    ```python
    if not current_key or current_key.startswith("AQ"):
        return {
            "title": f"Learning Path: {request.topic}",
            # ... hardcoded placeholder structure ...
        }
    ```
  - `/api/suggestions` (`backend/main.py:1079`):
    ```python
    @app.post("/api/suggestions")
    async def generate_suggestions(request: TopicRequest, x_api_key: str | None = Header(default=None)):
    ```
    Performs naive space splitting with Counter for the fallback:
    ```python
    if not current_key or current_key.startswith("AQ"):
        words = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in request.topic_or_text.split() if len(re.sub(r'[^a-zA-Z]', '', w)) > 5]
        # ...
    ```

- **Concept Map Generation**:
  - `generate_concept_map` and `_vietnamese_concept_map` (`backend/nlp/concept_map.py`):
    Currently formats nodes only with `id` and `label`:
    ```python
    formatted_nodes = [{"id": n, "label": n.title()} for n in nodes]
    ```
    This misses the `definition` and `formula` fields expected by `ConceptNodeSchema` defined in `backend/main.py:219`:
    ```python
    class ConceptNodeSchema(BaseModel):
        id: str
        label: str
        definition: str = Field(...)
        formula: str | None = Field(...)
    ```

---

## 2. Logic Chain

1. **Endpoint Limitations**: Since the current endpoints for Exam Prep, Study Plan, Learning Path, and Suggestions do not have a robust offline generator and fail under key absence or exception states (Observation 1), they must be retrofitted to run local NLP fallback generators.
2. **Concept Map Violations**: Because the current concept nodes do not populate `definition` and `formula` (Observation 2), the frontend lacks this metadata in the offline rendering modes.
3. **Extraction Approach**: To extract definitions and formulas, we can search document sentences containing each concept word (Observation 2). We can apply text search filters (English vs. Vietnamese indicators) and algebraic symbols filters (like `=`) to dynamically extract this metadata.
4. **Resolution Strategy**: Resolving these deficiencies requires adding helper functions (`_extract_definition_and_formula`, `generate_offline_exam_prep`, `generate_offline_study_plan`, `generate_offline_learning_path`, `generate_offline_suggestions`) and updating `backend/main.py` endpoints to invoke them in their error/fallback paths.

---

## 3. Caveats

- We did not implement or test the code changes since our role is strictly read-only.
- The similarity mapping for `generate_offline_learning_path` assumes the availability of related documents in the SQLite database to guide path generation. If no documents exist or the similarity score is low, it safely falls back to standard topic templates.

---

## 4. Conclusion

The codebase lacks structured offline NLP fallbacks for major endpoints and concept maps. Implementing the proposed fix strategy will align the backend with Milestone 4 criteria: ensuring robust offline support across exam prep, study plan, learning paths, suggestions, and concept map metadata.

---

## 5. Verification Method

- Inspect the generated report in `/Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo/.agents/explorer_m2_3/analysis.md` to confirm the proposed fix logic.
- Verify that unit tests (e.g. `pytest backend/tests/`) pass after the implementer applies the changes.
