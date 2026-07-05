## Challenge Summary

**Overall risk assessment**: MEDIUM

Offline NLP fallback functions are generally robust and conformant to target schemas across various edge-case inputs (empty texts, special characters, SQL injections, emojis, and non-ASCII scripts). However, they fail catastrophically (raising a spaCy `ValueError: [E088]`) when processing non-Vietnamese texts exceeding 1,000,000 characters.

---

## Challenges

### [High] Challenge 1: spaCy Max Length Input Crash

- **Assumption challenged**: Assuming input text size will always be within spaCy's default character processing constraints.
- **Attack scenario**: A user requests a Study Plan, Exam Prep, Suggestions, or Learning Path for a large English/non-Vietnamese document or textbook exceeding 1,000,000 characters.
- **Blast radius**: The backend throws a `ValueError: [E088]` from `spacy.language.Language.__call__`, aborting processing and returning a 500 error to the client.
- **Mitigation**: Truncate the text payload to a safe upper bound (e.g., 200,000 characters) in `clean_text` or at the entry point of the fallback functions before spaCy processing.

### [Medium] Challenge 2: Unbounded Latency in Vietnamese POS Tagging

- **Assumption challenged**: Assuming pyvi POS tagging processes large payloads fast enough to be run synchronously.
- **Attack scenario**: A user uploads a moderately large Vietnamese document (e.g., 500KB - 5MB) and triggers the fallback NLP generators.
- **Blast radius**: The process hangs for tens of seconds in `ViPosTagger.postagging()`, blocking the synchronous flow and potentially causing timeout/starvation of resources.
- **Mitigation**: Enforce an upper bound on document length processed by pyvi or process the text in chunks.

---

## Stress Test Results

| Scenario / Input | Function | Expected Behavior | Actual Behavior | Result |
| --- | --- | --- | --- | --- |
| **Empty String** | All functions | Return default schema matching structures | Correctly returned default schemas | **PASS** |
| **Spaces & Newlines** | All functions | Return default schema matching structures | Correctly returned default schemas | **PASS** |
| **Null Byte (`\x00`)** | All functions | Clean or process without exception | Successfully processed | **PASS** |
| **Special Characters** | All functions | Return valid schemas without error | Successfully processed | **PASS** |
| **HTML / SQL Injection** | All functions | Return valid schemas without executing code / error | Successfully processed | **PASS** |
| **Unicode & Emojis** | All functions | Handle unicode symbols without crashing | Successfully processed | **PASS** |
| **Vietnamese (Standard)** | All functions | Route via Vietnamese processing and return schemas | Correctly segmented and returned schemas | **PASS** |
| **Cyrillic, Arabic, Chinese**| All functions | Route via English spaCy path and return schemas | Successfully processed via English path | **PASS** |
| **Very Long English (>1M chars)**| `exam_prep`, `study_plan`, `suggestions` | Process safely or truncate | Crashed with spaCy `ValueError: [E088]` | **FAIL** |
| **Very Long English (>1M chars)**| `learning_path` (db=None) | Fallback to default template schema | Correctly returned template schema | **PASS** |
| **Very Long Vietnamese** | All functions | Process safely without spaCy error | Completed successfully, but with high latency | **PASS** |
| **Mock DB Standard Document**| `learning_path` | Rank documents and build path | Successfully ranked and generated modules | **PASS** |
| **Mock DB Long En Doc (>1M chars)**| `learning_path` | Process safely or truncate | Crashed with spaCy `ValueError: [E088]` | **FAIL** |
| **Mock DB Long Vi Doc** | `learning_path` | Process safely without spaCy error | Completed successfully | **PASS** |

---

## Unchallenged Areas

- **Concurrency**: Multiple concurrent heavy requests processing large texts simultaneously was not evaluated under CPU stress.
