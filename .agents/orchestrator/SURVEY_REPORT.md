# SURVEY & FEATURE COMPARISON REPORT

This report provides a comprehensive cross-check and comparison of 5 core feature flows between the cloud-based **OmiLearn** service and the local **Workflow** application.

---

## 1. Flow 1: Document Ingestion & Storage

### OmiLearn (Cloud Service)
- **Ingestion Route**: File uploads are sent to cloud APIs, processed asynchronously on remote servers, and stored in cloud-hosted databases (e.g., PostgreSQL/S3).
- **Text Extraction**: Runs on remote workers using cloud-based OCR or document parsing services.
- **Branding/UI**: Displays OmiLearn branding and syncs files automatically across multiple devices via user accounts.

### Workflow (Local App)
- **Ingestion Route**: Uploads are saved to a local `uploads/` directory. Metadata is stored in a local SQLite database (`local.db` or `omilearn_local.db`).
- **Text Extraction**: Processes files locally and generates `.txt` cache files for extraction to speed up subsequent reads. Auxiliary `.txt` files are filtered out during directory serving to avoid UI rendering breaks.
- **Multi-Context Integration**: Supports both `project_id` and `document_id` scopes at database, API, and frontend levels.
- **Branding**: Completely rebranded to **Workflow**. No instances of "OmiLearn" are shown to the user.

---

## 2. Flow 2: Roadmap Generation & Personalization

### OmiLearn (Cloud Service)
- **Generation**: Calls commercial LLMs (e.g., OpenAI, Gemini) to generate personalized study roadmaps based on user goals.
- **Connectivity**: Requires constant internet access. If the API is unreachable, roadmap generation fails.

### Workflow (Local App)
- **Generation**: Supports LLM roadmap generation via the user's custom API key.
- **Offline Fallback**: When no API key is specified (or the key is invalid), Workflow automatically falls back to its offline-first local NLP pipeline (using `pyvi` and `nltk` to extract terms and structure modules), ensuring the feature remains functional offline.
- **Scope Compliance**: Roadmaps support both Project-wide learning paths and Standalone Document-specific paths.

---

## 3. Flow 3: AI Learning Tools (Quizzes & Concept Maps)

### OmiLearn (Cloud Service)
- **Quiz Generation**: Remote server uses LLMs to parse the uploaded study material and generate multiple-choice quizzes.
- **Concept Maps**: Generates interactive mind maps with semantic relations between terms using remote LLM prompts.

### Workflow (Local App)
- **Quiz Generation**: Quizzes can be generated from the document viewer. An offline NLP fallback parses key sentences and formats multiple-choice questions when the user is offline.
- **Concept Maps**: Local NLP fallback uses text mining to identify terms, generate relations, and extract detailed nodes containing `id`, `label`, `definition`, and `formula` (parsed from the text), displaying them interactively inside the UI.
- **Persistence**: Generated quizzes and concept maps are persisted locally to the SQLite `artifacts` table under either `project_id` or `document_id`.

---

## 4. Flow 4: Spaced Repetition (Flashcards & SM-2)

### OmiLearn (Cloud Service)
- **Flashcard Review**: Card sets are generated on the server and synced to cloud databases.
- **Spaced Repetition Algorithm**: Computes review intervals on the server.

### Workflow (Local App)
- **Flashcard Review**: Flashcards are saved in the local SQLite `flashcards` table, properly indexed by either `project_id` or `document_id`.
- **Spaced Repetition Algorithm**: Runs the SuperMemo-2 (SM-2) algorithm locally. When a user rates their recall (0-5), the system computes the next review interval, repetition count, and ease factor on the local SQLite store immediately.

---

## 5. Flow 5: Collaboration & Workspaces

### OmiLearn (Cloud Service)
- **Sharing**: Generates public sharing links hosted under `https://omilearn.com/share/:id`.
- **Permissions**: Invites users to cloud-hosted workspaces with specific access controls.

### Workflow (Local App)
- **Sharing**: Replaced public sharing URLs to use `https://workflow.com/share/:id` instead of OmiLearn.
- **Permissions**: Supports local collaboration simulation where users can invite members by email and assign roles (Owner, Editor, Viewer). The FastAPI backend manages the invite and member schema models, verifying permissions for both Project and Standalone Document contexts.
