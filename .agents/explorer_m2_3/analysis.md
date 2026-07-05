# Analysis: Offline Local-NLP Fallbacks & Concept Map Extraction

This analysis document covers the assessment and proposed fix strategy for Milestone 2: Offline Local-NLP Fallbacks and Concept Map definition/formula extraction.

---

## 1. Current State of API Endpoints

### 1.1 `/api/generate_exam_prep`
- **Location**: `backend/main.py` (lines 899-928)
- **Current Behavior**:
  - Extracts text from the requested document page ranges (if provided) or falls back to raw `topic_or_text`.
  - Determines `current_key` via `get_api_key(request.api_key)`.
  - If `current_key` is set, calls Gemini AI using `ExamPrepSchema`. If it fails, raises a `HTTPException(status_code=500, detail="AI processing failed for exam prep.")`.
  - If `current_key` is not set (e.g. offline engine toggle / mock key starting with "AQ"), raises `HTTPException(status_code=400, detail="No valid AI key provided for exam prep.")`.
- **Limitation**: No offline/local NLP fallback is implemented. The application errors out when offline or when the API key is missing/invalid.

### 1.2 `/api/generate_study_plan`
- **Location**: `backend/main.py` (lines 934-950)
- **Current Behavior**:
  - Determines `current_key` via `get_api_key(request.api_key)`.
  - If `current_key` is set, calls Gemini AI using `StudyPlanSchema`. If it fails, raises `HTTPException(status_code=500, detail="AI processing failed for study plan.")`.
  - If `current_key` is not set, raises `HTTPException(status_code=400, detail="No valid AI key provided for study plan.")`.
- **Limitation**: Like exam prep, it offers no offline fallback and fails with 400/500 errors in offline environments or on API failures.

### 1.3 `/api/generate_path`
- **Location**: `backend/main.py` (lines 740-789)
- **Current Behavior**:
  - Determines `current_key` via `get_api_key(x_api_key)`.
  - If `current_key` is None or starts with "AQ", it immediately returns a static, hardcoded JSON structure containing hardcoded topics (Module 1, 2, 3) interpolating the topic name.
  - If `current_key` is set, calls Gemini AI using `LearningPathSchema`. If it fails, raises a 500 error.
- **Limitation**: The fallback is completely static (hardcoded placeholders) and does not utilize local text documents. Additionally, it fails if the API call throws an exception instead of gracefully falling back.

### 1.4 `/api/suggestions`
- **Location**: `backend/main.py` (lines 1079-1112)
- **Current Behavior**:
  - Determines `current_key` via `get_api_key(x_api_key)`.
  - If `current_key` is None or starts with "AQ", it executes a very basic, naive keyword heuristic: splits `topic_or_text` by whitespace, filters words longer than 5 letters, removes non-alphabetic characters, and selects the top 3 most common words.
  - If `current_key` is set, calls Gemini AI with `SuggestionSchema`. If it fails, raises a 500 error.
- **Limitation**: The naive word splitter does not extract real noun phrases or respect languages (e.g. Vietnamese). Additionally, it crashes with a 500 error on API failures rather than falling back.

---

## 2. Concept Map definition & formula extraction

### 2.1 Current Behavior in `backend/nlp/concept_map.py`
- **Location**: `backend/nlp/concept_map.py` (specifically `generate_concept_map` and `_vietnamese_concept_map`).
- **Current Behavior**:
  - Extracts key noun chunks/concepts from the text corpus.
  - Builds a co-occurrence graph using NetworkX to determine concept importance.
  - Formats nodes for the frontend by returning only `id` and `label` (title-cased):
    ```python
    formatted_nodes = [{"id": n, "label": n.title()} for n in nodes]
    ```
- **Limitation**: The `ConceptNodeSchema` expects `id`, `label`, `definition` (string), and `formula` (optional string). Returning only `id` and `label` violates the schema expectations of the frontend components (which display concept tooltips with definitions and formulas).

---

## 3. Proposed Fix Strategy

### 3.1 Enhancing `backend/nlp/concept_map.py`
To populate `definition` and `formula` for each concept, we propose implementing a heuristic-based sentence search:
1. **Sentence Splitting**: Extract all clean sentences from the document corpus (respecting language settings).
2. **Definition Indicators**: Search for sentences containing the concept followed by definition verbs/phrases:
   - *English*: `is`, `are`, `refers to`, `means`, `is defined as`, `represents`, `is a`, `is an`.
   - *Vietnamese*: `là`, `định nghĩa là`, `nghĩa là`, `bao gồm`, `đề cập đến`.
3. **Formula Heuristic**: Check matching sentences for:
   - An equals sign `=` with letters/numbers on both sides.
   - Core mathematical operators (`+`, `-`, `*`, `/`, `^`, etc.) or formula terms (`formula`, `equation`, `calculate`, `công thức`, `phương trình`).
   - Extract the matching equation substring via regex.

#### Proposed Code for `backend/nlp/concept_map.py`:
```python
import re
from typing import List, Tuple

def _extract_definition_and_formula(concept: str, sentences: List[str], is_vn: bool = False) -> Tuple[str, str | None]:
    """
    Extracts a definition and a formula from a list of sentences where the concept occurs.
    """
    concept_lower = concept.lower()
    matching_sents = [s for s in sentences if concept_lower in s.lower()]
    
    # Definition heuristics
    en_def_indicators = [" is ", " are ", " refers to ", " is defined as ", " means ", " represents ", " is a ", " is an "]
    vi_def_indicators = [" là ", " định nghĩa là ", " nghĩa là ", " bao gồm ", " đề cập đến "]
    
    indicators = vi_def_indicators if is_vn else en_def_indicators
    definition = None
    
    # Priority 1: Sentence containing both the concept and a definition indicator immediately after it
    for sent in matching_sents:
        sent_lower = sent.lower()
        idx = sent_lower.find(concept_lower)
        if idx != -1:
            after_concept = sent_lower[idx + len(concept_lower):]
            if any(ind in after_concept[:50] for ind in indicators):
                definition = sent.strip()
                break
                
    # Priority 2: Sentence containing the concept and any definition indicator anywhere
    if not definition:
        for sent in matching_sents:
            if any(ind in sent.lower() for ind in indicators):
                definition = sent.strip()
                break
                
    # Priority 3: First sentence containing the concept
    if not definition and matching_sents:
        definition = matching_sents[0].strip()
        
    # Priority 4: Default generic sentence
    if not definition:
        if is_vn:
            definition = f"{concept.title()} là một khái niệm quan trọng liên quan đến chủ đề."
        else:
            definition = f"{concept.title()} is a key concept related to the topic."

    # Formula heuristics
    formula = None
    math_symbols = ["+", "-", "*", "/", "^", "√", "∑", "π", "θ", "λ"]
    math_keywords = ["formula", "equation", "calculate", "defined by", "given by", "where", "công thức", "phương trình", "tính bằng"]
    
    for sent in matching_sents:
        sent_lower = sent.lower()
        if "=" in sent_lower:
            parts = sent_lower.split("=")
            if len(parts) >= 2 and any(c.isalnum() for c in parts[0]) and any(c.isalnum() for c in parts[1]):
                if any(sym in sent_lower for sym in math_symbols) or any(kw in sent_lower for kw in math_keywords):
                    match = re.search(r'[a-zA-Z0-9_\(\)\s\+\-\*\/\.\^≈≠≤≥]+=[a-zA-Z0-9_\(\)\s\+\-\*\/\.\^≈≠≤≥]+', sent)
                    if match:
                        extracted = match.group(0).strip()
                        if len(extracted) > 3 and any(ch.isalpha() for ch in extracted):
                            formula = extracted
                            break
                    formula = sent.strip()
                    break

    return definition, formula
```

These extracted definitions and formulas can then be populated directly when building the `formatted_nodes` inside `generate_concept_map` and `_vietnamese_concept_map`.

---

### 3.2 Offline Generators for main.py Endpoints

We propose adding offline NLP fallback generators for Study Plans, Exam Preps, Learning Paths, and Suggestions.

#### 3.2.1 Offline Exam Prep Generator
Uses TF-IDF sentence centrality to build a structured cheat sheet containing a summary and key takeaways:
```python
def generate_offline_exam_prep(text: str) -> dict:
    from nlp.preprocessor import clean_text
    from nlp.vietnamese import is_vietnamese, vi_clean_sentences, vi_keywords
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    text = clean_text(text)
    is_vn = is_vietnamese(text)
    
    if is_vn:
        keywords = vi_keywords(text, top_n=3)
        title = f"Tài liệu ôn thi: {', '.join(keywords).title()}" if keywords else "Tài liệu ôn thi"
        sentences = vi_clean_sentences(text)
    else:
        from nlp.concept_map import nlp as spacy_nlp
        if spacy_nlp:
            doc = spacy_nlp(text)
            sentences = [s.text.strip() for s in doc.sents]
            chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
            from collections import Counter
            common_chunks = [c for c, _ in Counter(chunks).most_common(3) if len(c) > 3 and c not in spacy_nlp.Defaults.stop_words]
            title = f"Exam Prep: {', '.join(common_chunks).title()}" if common_chunks else "Exam Prep Guide"
        else:
            sentences = [s.strip() for s in text.split(".") if s.strip()]
            title = "Exam Prep Guide"
            
    summary = ""
    key_points = []
    if len(sentences) >= 2:
        try:
            matrix = TfidfVectorizer().fit_transform(sentences)
            centrality = cosine_similarity(matrix).sum(axis=1)
            ranked_indices = centrality.argsort()[::-1]
            summary = "\n\n".join(sentences[i] for i in sorted(ranked_indices[:2]))
            key_points = [sentences[i] for i in sorted(ranked_indices[2:8])]
        except Exception:
            summary = "\n\n".join(sentences[:2])
            key_points = sentences[2:7]
    else:
        summary = text
        key_points = sentences
        
    md = f"# {title}\n\n"
    if is_vn:
        md += f"## Tổng quan học tập\n{summary}\n\n"
        md += "## Trọng tâm ôn tập (Kiến thức cốt lõi)\n"
        for i, pt in enumerate(key_points, 1):
            md += f"- **Kiến thức {i}**: {pt}\n"
    else:
        md += f"## Executive Summary / Overview\n{summary}\n\n"
        md += "## Key Learning Points (High Centrality Takeaways)\n"
        for i, pt in enumerate(key_points, 1):
            md += f"- **Key Point {i}**: {pt}\n"
            
    return {"title": title, "markdown_content": md}
```

#### 3.2.2 Offline Study Plan Generator
Partitions sentences into thirds to align with Stages 1 (Foundations), 2 (Deep Dive), and 3 (Review):
```python
def generate_offline_study_plan(text: str) -> dict:
    from nlp.preprocessor import clean_text
    from nlp.vietnamese import is_vietnamese, vi_clean_sentences, vi_keywords
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    text = clean_text(text)
    is_vn = is_vietnamese(text)
    
    if is_vn:
        keywords = vi_keywords(text, top_n=2)
        title = f"Giáo án học tập: {', '.join(keywords).title()}" if keywords else "Giáo án học tập"
        sentences = vi_clean_sentences(text)
    else:
        from nlp.concept_map import nlp as spacy_nlp
        if spacy_nlp:
            doc = spacy_nlp(text)
            sentences = [s.text.strip() for s in doc.sents]
            chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
            from collections import Counter
            common_chunks = [c for c, _ in Counter(chunks).most_common(2) if len(c) > 3 and c not in spacy_nlp.Defaults.stop_words]
            title = f"Study Plan: {', '.join(common_chunks).title()}" if common_chunks else "Study Plan Guide"
        else:
            sentences = [s.strip() for s in text.split(".") if s.strip()]
            title = "Study Plan Guide"
            
    stage1_sents, stage2_sents, stage3_sents = [], [], []
    if len(sentences) >= 3:
        try:
            n = len(sentences)
            s1, s2, s3 = sentences[:n//3], sentences[n//3 : 2*n//3], sentences[2*n//3:]
            
            def get_top_sents(stage_sents, count=2):
                if not stage_sents: return []
                mat = TfidfVectorizer().fit_transform(stage_sents)
                cent = cosine_similarity(mat).sum(axis=1)
                ranked = cent.argsort()[::-1]
                return [stage_sents[i] for i in sorted(ranked[:count])]
                
            stage1_sents = get_top_sents(s1, 2)
            stage2_sents = get_top_sents(s2, 2)
            stage3_sents = get_top_sents(s3, 2)
        except Exception:
            n = len(sentences)
            stage1_sents = sentences[:min(2, n)]
            stage2_sents = sentences[n//3 : min(n//3 + 2, n)]
            stage3_sents = sentences[2*n//3 : min(2*n//3 + 2, n)]
    else:
        stage1_sents = sentences

    md = f"# {title}\n\n"
    if is_vn:
        md += "## Giai đoạn 1: Tiếp cận & Nền tảng (Thời gian: 1 - 2 ngày)\n"
        for s in stage1_sents: md += f"- *Khái niệm trọng tâm*: {s}\n"
        md += "\n## Giai đoạn 2: Chi tiết & Nghiên cứu sâu (Thời gian: 3 - 5 ngày)\n"
        for s in stage2_sents: md += f"- *Nội dung cần làm rõ*: {s}\n"
        md += "\n## Giai đoạn 3: Thực hành & Tự đánh giá (Thời gian: 1 - 2 ngày)\n"
        for s in stage3_sents: md += f"- *Ứng dụng & Kết luận*: {s}\n"
    else:
        md += "## Phase 1: Foundations & Core Terminology (Duration: 1-2 Days)\n"
        for s in stage1_sents: md += f"- *Foundational Point*: {s}\n"
        md += "\n## Phase 2: Deep Dive & Core Mechanism (Duration: 3-5 Days)\n"
        for s in stage2_sents: md += f"- *Core Detail*: {s}\n"
        md += "\n## Phase 3: Review & Self-Assessment (Duration: 1-2 Days)\n"
        for s in stage3_sents: md += f"- *Conclusion / Application*: {s}\n"
        
    return {"title": title, "markdown_content": md}
```

#### 3.2.3 Offline Learning Path Generator
Queries the DB to find documents relevant to the requested `topic` using TF-IDF cosine similarity. If a matching document is found, it extracts key concepts from it and generates the path modules; otherwise, it falls back to a structured template based on the topic string:
```python
def generate_offline_learning_path(topic: str, db = None) -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from nlp.concept_map import nlp as spacy_nlp, _extract_definition_and_formula
    from nlp.vietnamese import is_vietnamese, vi_nouns, vi_clean_sentences
    
    source_doc = None
    if db is not None:
        try:
            import models
            docs = db.query(models.Document).all()
            if docs:
                corpus = [topic] + [doc.content for doc in docs]
                vectorizer = TfidfVectorizer()
                tfidf = vectorizer.fit_transform(corpus)
                similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
                best_idx = similarities.argsort()[::-1][0]
                if similarities[best_idx] > 0.05:
                    source_doc = docs[best_idx]
        except Exception as e:
            print(f"Error querying DB for path relevance: {e}")
            
    if source_doc:
        text = source_doc.content
        is_vn = is_vietnamese(text)
        if is_vn:
            sentences = vi_clean_sentences(text)
            concepts = vi_nouns(text)
            from collections import Counter
            unique_concepts = [c for c, _ in Counter(concepts).most_common(6)]
        else:
            if spacy_nlp:
                doc = spacy_nlp(text)
                sentences = [s.text.strip() for s in doc.sents]
                chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
                from collections import Counter
                unique_concepts = [c for c, _ in Counter(chunks).most_common(6) if len(c) > 3 and c not in spacy_nlp.Defaults.stop_words]
            else:
                sentences = [s.strip() for s in text.split(".") if s.strip()]
                unique_concepts = []
                
        if len(unique_concepts) >= 3:
            modules = []
            num_modules = 3
            concepts_per_module = len(unique_concepts) // num_modules
            for m_idx in range(num_modules):
                m_concepts = unique_concepts[m_idx * concepts_per_module : (m_idx + 1) * concepts_per_module]
                topics = []
                for c in m_concepts:
                    defn, form = _extract_definition_and_formula(c, sentences, is_vn)
                    desc = defn
                    if form: desc += f" (Formula: {form})"
                    topics.append({
                        "title": c.title(),
                        "description": desc[:150] + "..." if len(desc) > 150 else desc,
                        "estimated_time": "45 mins"
                    })
                
                module_title = f"Giai đoạn {m_idx+1}: " if is_vn else f"Module {m_idx+1}: "
                if m_idx == 0: module_title += "Khái niệm nền tảng" if is_vn else "Foundations"
                elif m_idx == 1: module_title += "Kiến thức chuyên sâu" if is_vn else "Core Mechanisms"
                else: module_title += "Ứng dụng & Tổng hợp" if is_vn else "Advanced Applications"
                
                modules.append({"title": module_title, "topics": topics})
                
            return {
                "title": f"Learning Path: {topic.title()}",
                "description": f"Offline generated path based on your document '{source_doc.title}' regarding {topic}.",
                "modules": modules
            }
            
    # Default template fallback
    return {
        "title": f"Learning Path: {topic}",
        "description": f"An algorithmically generated structured path for mastering {topic}.",
        "modules": [
            {
                "title": f"Module 1: Introduction to {topic}",
                "topics": [
                    {"title": f"What is {topic}?", "description": f"Understanding the basic definition and scope of {topic}.", "estimated_time": "30 mins"},
                    {"title": "History and Evolution", "description": f"How the study of {topic} has evolved over time.", "estimated_time": "45 mins"}
                ]
            },
            {
                "title": "Module 2: Core Concepts",
                "topics": [
                    {"title": "Key Principles", "description": f"The fundamental building blocks and rules governing {topic}.", "estimated_time": "60 mins"},
                    {"title": "Important Terminology", "description": "A glossary of terms you must know.", "estimated_time": "45 mins"}
                ]
            },
            {
                "title": "Module 3: Advanced Applications",
                "topics": [
                    {"title": "Real-world Use Cases", "description": f"How {topic} is applied in practical scenarios and industry.", "estimated_time": "90 mins"},
                    {"title": "Next Steps", "description": "Resources and exercises to continue learning.", "estimated_time": "30 mins"}
                ]
            }
        ]
    }
```

#### 3.2.4 Offline Suggestions Generator
Uses Spacy / PyVi to extract the top 3 most common nouns/noun-phrases from the document corpus, routing appropriately:
```python
def generate_offline_suggestions(text: str) -> dict:
    from nlp.preprocessor import clean_text
    from nlp.vietnamese import is_vietnamese, vi_nouns
    from collections import Counter
    import re
    
    text = clean_text(text)
    is_vn = is_vietnamese(text)
    
    if is_vn:
        concepts = vi_nouns(text)
        freq = Counter(concepts)
        most_common = [w for w, _ in freq.most_common(3)]
    else:
        from nlp.concept_map import nlp as spacy_nlp
        if spacy_nlp:
            doc = spacy_nlp(text)
            chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
            freq = Counter(chunks)
            most_common = [c for c, _ in freq.most_common(3) if len(c) > 3 and c not in spacy_nlp.Defaults.stop_words]
        else:
            words = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in text.split() if len(re.sub(r'[^a-zA-Z]', '', w)) > 5]
            freq = Counter(words)
            most_common = [word for word, count in freq.most_common(3)]
            
    path_topic = most_common[0].capitalize() if len(most_common) > 0 else "General Study"
    quiz_topic = most_common[1].capitalize() if len(most_common) > 1 else "Reading Comprehension"
    flashcard_topic = most_common[2].capitalize() if len(most_common) > 2 else "Vocabulary"
    
    if is_vn:
        return {
            "path_topic": f"Giới thiệu về {path_topic}",
            "quiz_topic": f"Các khái niệm {quiz_topic}",
            "flashcard_topic": f"Các thuật ngữ {flashcard_topic} trọng tâm"
        }
    else:
        return {
            "path_topic": f"Introduction to {path_topic}",
            "quiz_topic": f"{quiz_topic} Concepts",
            "flashcard_topic": f"Key {flashcard_topic} Terms"
        }
```

---

### 3.3 Endpoint Integration Strategy

In `backend/main.py`, the endpoints should try-except the AI agent runs, and fall back to these offline generation functions when:
1. `current_key` is not provided (or starts with "AQ" for mock mode).
2. The AI agent fails (raises an exception).

#### Example Integration for `/api/generate_exam_prep`:
```python
@app.post("/api/generate_exam_prep")
async def generate_exam_prep_endpoint(request: TopicRequest, db: Session = Depends(get_db)):
    text_to_process = request.topic_or_text
    # ... extraction from document and page ranges ...
    
    current_key = get_api_key(request.api_key)
    if current_key and not current_key.startswith("AQ"):
        try:
            config = LocalAgentConfig(api_key=current_key, model="gemini-3.1-flash-lite", response_schema=ExamPrepSchema, capabilities=FAST_CAPS)
            prompt = f"Generate a comprehensive Exam Preparation cheat sheet..."
            data = await agent_run(config, prompt)
            if data and data.get("markdown_content"):
                if request.project_id:
                    crud.create_artifact(db, project_id=request.project_id, type="examprep", title=data.get("title", "Tài liệu phòng thi"), content=json.dumps(data))
                return data
        except Exception as e:
            print(f"[exam_prep] AI failed, falling back to offline: {e}")
            
    # Fallback Offline Engine
    from nlp.concept_map import generate_offline_exam_prep
    data = generate_offline_exam_prep(text_to_process)
    if request.project_id:
        crud.create_artifact(db, project_id=request.project_id, type="examprep", title=data.get("title"), content=json.dumps(data))
    return data
```

Similar modifications should be applied to `/api/generate_study_plan`, `/api/generate_path`, and `/api/suggestions`.

---

## 4. Verification Methods

1. **Unit Tests**:
   - Write tests in `backend/tests/test_nlp_fallbacks.py` targeting the new offline generators directly to verify they return correctly formatted dicts with English/Vietnamese content.
   - Mock the database session and verify `/api/generate_path` queries documents for similarity.
2. **API Integration Tests**:
   - Hit `/api/generate_map`, `/api/generate_exam_prep`, `/api/generate_study_plan`, `/api/generate_path`, `/api/suggestions` endpoints with `api_key="OFFLINE"` or invalid keys to verify they return valid JSON structures conforming to schemas instead of 400/500 errors.
