# Workflow — Build Handoff for Antigravity (Gemini 3.1 Pro, High)

You are continuing development of **Workflow**, a local-first study app for Vietnamese
university students (HUST / HCMUT / etc.). The goal is to clone the feature set of the
reference product at **omilearn.com**, branded as **Workflow** everywhere in this repo.

Work in small, verified steps. After each change that's visible in the browser, run the app
and confirm it. Match the existing code style exactly (inline styles, Vietnamese UI strings).

---

## How to run (IMPORTANT)

**Backend** (FastAPI, port 8000) — must run from the venv, NOT system python:
```bash
cd backend && venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
- The venv has `google.antigravity`, `pyvi`, `pdfplumber`, `fastapi`, `uvicorn`. System python does NOT.
- It runs **without `--reload`**, so **restart it after every backend edit**.

**Frontend** (React + Vite, port 5173):
```bash
npm run dev
```
Launch config is in `.claude/launch.json` (name: `frontend`). The app is also wrapped in
**Electron** (`nodeIntegration: true`, so `window.require('fs'|'electron'|...)` works in renderer).

---

## Architecture

- **Frontend:** React 18 + Vite + react-router-dom (**HashRouter** — routes look like `#/document/7`).
  Pages: `src/pages/{DocumentExplorer,DocumentViewer,ExamViewer,Settings}.jsx`.
  Layout: `src/components/layout/{AppLayout,Sidebar,StudioSidebar,ProjectStudioSidebar,Topbar}.jsx`
  (NOTE: `Topbar.jsx` is **dead code** — not imported anywhere. The app has no global top bar;
  the **Sidebar** is the global chrome.)
  Modals: `src/components/modals/*.jsx`. **All styling is inline `style={{}}`** — no CSS framework.
  Brand colors: `--brand-primary` (maroon), `#1B2A4E` (navy text), `--brand-secondary`, `--bg-tertiary`.
- **Backend:** FastAPI (`backend/main.py`) + SQLAlchemy + SQLite (`backend/workflow_local.db`).
  Models (`backend/db/models.py`): `Flashcard` (SM-2 spaced repetition), `Document` (id, filename,
  content, upload_date — **no file column**), `QuizScore`.
  NLP engine (offline by design): `backend/nlp/{flashcards,quizzes,concept_map,notes,readability,
  vietnamese,vi_desegment}.py`. Public fns: `extract_flashcards`, `extract_quiz`,
  `generate_concept_map`, `extract_notes`, `score_difficulty`.
- **AI:** `agent_run()` in main.py calls a `google.antigravity` Agent (Gemini) with a hard timeout
  and **falls back to the local NLP engine** on timeout/error. The Gemini API key is a deliberate
  placeholder — study tools must work fully offline via the Python NLP engine.
- **Vietnamese handling:** `vietnamese.is_vietnamese()` detects VN text and routes to `vi_*` helpers.
  Dense exam PDFs extract with lost spaces ("Côngthức"); `vi_desegment.desegment()` re-splits glued
  syllables via DP, and `vi_clean_sentences()` calls it on every sentence.

### Backend API (all under `http://127.0.0.1:8000`)
`POST /api/chat` · `POST /api/generate_flashcards` · `POST /api/documents/upload` ·
`GET /api/documents` (returns `{id,filename,content,upload_date,has_file}`) ·
`DELETE /api/documents/{id}` · **`GET /api/documents/{id}/file`** (serves raw PDF) ·
`POST /api/generate_path` · `POST /api/generate_quiz` · `POST /api/quizzes/submit` ·
`GET /api/documents/{id}/progress` · `POST /api/generate_notes` · `GET /api/flashcards/due` ·
`POST /api/flashcards/review` · `POST /api/score_difficulty` · `POST /api/generate_map` ·
`POST /api/suggestions`

### Google OAuth (already configured)
`.env` (exists on disk, untracked by git) holds `VITE_GOOGLE_OAUTH_CLIENT_ID` and
`VITE_GOOGLE_DRIVE_API_KEY`. GIS is loaded via the exported `loadGis()` in `src/utils/googleDrive.js`.
Do NOT hardcode secrets; read from `import.meta.env.VITE_*`.

---

## What was completed this session (do not redo)

1. **Vietnamese de-segmentation fix.** `backend/nlp/vietnamese.py` `vi_clean_sentences()` now always
   calls `desegment()` (removed a too-high `len(tok) > 12` gate that disabled de-gluing on real 6–9
   char glued bigrams). `backend/nlp/readability.py` `_vietnamese_difficulty()` de-glues per sentence
   before POS-tagging. Verified: flashcards/quiz/concept-map/notes now produce clean spaced terms.

2. **Quiz "Đối chiếu" is now a real PDF viewer (not extracted text).** User requirement:
   *"it must be pdf viewer not extracted text"*.
   - Backend (`main.py`): added `UPLOAD_DIR = backend/uploads`; upload handler now copies the raw PDF
     to `uploads/{doc.id}.pdf`; `GET /api/documents/{id}/file` serves it (`FileResponse`,
     `media_type=application/pdf`, 404 if missing); `GET /api/documents` includes `has_file`.
   - Frontend (`src/components/modals/TakeQuizModal.jsx`): the right panel is now an `<iframe>` PDF
     viewer (`src=".../documents/{id}/file#view=FitH"`), width 440px, modal widened to 1180px. The old
     keyword-highlight-on-text logic was removed. Falls back to extracted text only when no raw PDF.
   - `backend/uploads/` is gitignored; doc 7's PDF was backfilled. **"Nâng cấp Pro" was removed** earlier.

3. **Google account login (just added, NEEDS VERIFICATION).**
   - `src/utils/googleAuth.js` (NEW): `signInWithGoogle()` (GIS token flow, scope `openid email profile`,
     fetches `oauth2/v3/userinfo`, stores `{name,email,picture,sub}` in `localStorage['workflow_user']`),
     `signOutGoogle()`, `getStoredUser()`, `isAuthConfigured()`. Reuses the Drive Client ID.
   - `src/utils/googleDrive.js`: `loadGis()` is now `export`ed.
   - `src/components/layout/Sidebar.jsx`: bottom section now shows a Google account control — a
     "Đăng nhập với Google" button (with the multi-color G) when logged out, or an avatar + name +
     email row that opens a dropdown with "Đăng xuất" when logged in.
   - To verify the logged-in UI without driving the real Google popup, inject a fake user:
     `localStorage.setItem('workflow_user', JSON.stringify({name:'Hoàng Khôi',email:'x@gmail.com',picture:''}))`
     then reload.

---

## Target (from the real omilearn.com screenshots) — the backlog

Build these to match the reference product (branded **Workflow** here). Suggested priority order:

1. **Branding**: all UI must say "Workflow" (Sidebar logo, Topbar, DocumentViewer toggle, hero copy) — done; keep it that way in new UI.
2. **Global top bar** (currently none): center brand "Workflow", a "Search material..." pill, a dark-mode
   **moon toggle**, and the **account avatar top-right** with the dropdown (name / email / Đăng xuất).
   Consider moving the Google account control from the Sidebar into this top bar to match the reference exactly.
3. **Real PDF viewer for "Xem ngay"** (`DocumentViewer.jsx` currently renders `activeDoc.content` via
   ReactMarkdown — that's extracted text, must become a PDF viewer using `GET /api/documents/{id}/file`):
   header "Bản xem trước PDF", controls **Zoom − / Zoom +**, **Trang X / Y**, **Cuộn liên tục**,
   buttons **Tải file gốc** (download original) and **Tạo đề thi ngay** (open the quiz modal), **Làm mới**.
   The same rule — *PDF viewer, not extracted text* — applies everywhere a PDF source is shown.
4. **OmiGuide chat + teacher personas.** A `Chat chính` / `OmiGuide` toggle. Persona selector with 4
   personas, each setting the chat system-prompt/tone:
   - **Gia sư thân thiện** ("OmiGuide") — friendly 1-1 tutor, easy examples; chip "Muốn học nhẹ nhàng, có ví dụ đời thường".
   - **Coach nghiêm túc** ("Coach Omi") — strict, sets standards, gives a task after each answer; chip "Muốn học có kỷ luật, biết mình sai ở đâu".
   - **Socratic hỏi gợi mở** ("Socratic Omi") — leads with questions, doesn't reveal answers fast; chip "Muốn hiểu sâu bản chất, không chỉ nhớ".
   - **Bạn học Gen Z** ("Omi Buddy") — young, energetic, short bullets, fun analogies; chip "Muốn học nhanh, dễ nhớ, đỡ khô khan".
   Quick chips under the input: **Tạo quiz nhanh, Tạo flashcard, Giải thích lại, Cho ví dụ**. Input: "Hỏi OmiGuide hoặc yêu cầu quiz/flashcard...".
5. **Project structure.** `+ New Project`, project list in the left sidebar, project view header
   "OMIGUIDE / {title} / N source attached", `1 members`.
6. **GIÁO ÁN (lesson plan / roadmap).** Generate numbered learning objectives from the sources (each
   "Thuộc phần: ..."), with **Tạo giáo án** and **Dùng LLM** buttons. Studio (right): **Upload, Roadmap,
   Study plan (Study...), Search**. Sections **UPLOADED** (sources, "Sẵn sàng để hỏi") and **RECENT ARTIFACTS**.
7. **"Upload learning sources" modal** to match the reference product: drag-drop **PDF, DOCX, PNG, JPG, WebP, MP4, MP3**,
   plus a **Links** section (`+ Add link`, "Add YouTube, website or any URL"), **Cancel / Done**.
   (Current `UploadModal.jsx` is simpler; `SearchMaterialsModal.jsx` already stubs the search-links modal.)
8. **Dark mode** (the moon toggle) and the AI-TOKENS usage / Báo lỗi-Feedback chrome.

---

---

## BACKEND BUILD — full instructions

This section is the backend work needed to support the whole Workflow feature set. Build it
incrementally and keep the **offline-by-design** contract: **every AI feature MUST have a
deterministic local-NLP fallback** so the app works with no API key.

### Backend conventions you MUST follow
- **Stack:** FastAPI + SQLAlchemy + SQLite (`backend/workflow_local.db`). Models in
  `backend/db/models.py`, DB helpers in `backend/db/crud.py`, request/response schemas as
  `pydantic.BaseModel` classes near the top of `backend/main.py`, NLP in `backend/nlp/*`.
- **AI + fallback pattern (copy this for every generator):**
  ```python
  current_key = get_api_key(request.api_key)
  if current_key:
      try:
          config = LocalAgentConfig(api_key=current_key, response_schema=SomeSchema, capabilities=FAST_CAPS)
          data = await agent_run(config, prompt)            # structured=True by default
          if data: return {...}                              # persist + return
      except Exception as e:
          print(f"[feature] AI failed, offline fallback: {e}")
  return {...}                                               # offline NLP result (always works)
  ```
  Use `structured=False` for free-text (chat). Always **reply in the same language** as the input
  — detect with `nlp.vietnamese.is_vietnamese(text)` and route VN text through the `vi_*` helpers.
- **SQLite migrations:** `Base.metadata.create_all()` does NOT add columns to existing tables.
  When you add a column to an existing model, either run a one-off `ALTER TABLE`, delete the dev
  `workflow_local.db` to recreate it, or (preferred for blobs/files) store on disk keyed by id like
  the existing `backend/uploads/{id}.pdf` so no schema change is needed.
- **Restart the backend after every edit** (`cd backend && venv/bin/python -m uvicorn main:app
  --host 127.0.0.1 --port 8000`). Verify each endpoint with `curl` before moving on.
- Existing CRUD: `get_documents`, `create_document`, `delete_document`, `get_flashcards`,
  `get_due_flashcards`, `create_flashcard`, `update_flashcard_sm2`, `create_quiz_score`,
  `get_quiz_scores`. Existing schemas: `ChatRequest`, `FlashcardRequest/List`, `LearningPathSchema`,
  `QuizSchema`, `NoteSchema`, `ConceptMapSchema`, `QuizSubmitRequest`, `ReviewRequest`, etc.

### 1. Projects (the app is now project-based — Sidebar has a PROJECTS list)
- **Model `Project`**: `id, name, description, created_at`.
- **Link documents to projects:** add `project_id` (nullable FK) to `Document`, or a `project_sources`
  join table for many-to-many. Add `crud` helpers + cascade cleanup on delete (like `delete_document`).
- **Endpoints:** `POST /api/projects` (create), `GET /api/projects` (list, with source counts),
  `GET /api/projects/{id}` (detail + attached sources + recent artifacts), `DELETE /api/projects/{id}`,
  `POST /api/projects/{id}/sources` (attach existing/new doc), `DELETE /api/projects/{id}/sources/{doc_id}`.

### 2. Multi-format source ingestion (Upload modal accepts PDF/DOCX/PNG/JPG/WebP/MP4/MP3 + links)
Extend `POST /api/documents/upload` (and add `POST /api/documents/ingest_url`):
- **PDF** → `pdfplumber` (done) + keep raw file (done).
- **DOCX** → `python-docx` text extraction. **Images** (PNG/JPG/WebP) → OCR (`pytesseract` if
  available, else store + mark `needs_ocr`). **MP4/MP3** → transcription (`faster-whisper`/`whisper`
  if available, else store raw + mark `transcript_pending`). **URL/YouTube** → fetch & extract
  readable text (YouTube → transcript API/`youtube-transcript-api`; web → readability/`trafilatura`).
- **Store the raw file for ALL types** (generalize `uploads/{id}{ext}`) and make
  `GET /api/documents/{id}/file` serve the correct `media_type` (not hardcoded PDF). Add a `kind`
  field (pdf/docx/image/audio/video/link) to the documents list so the frontend picks the right viewer.
- Each new extractor needs graceful degradation if its lib isn't installed (return text="" + a flag,
  never 500). Add new deps to `backend/requirements.txt`.

### 3. OmiGuide chat: personas + source-grounded answers + history
- **Persona:** add `persona` to `ChatRequest` and switch the system prompt. The 4 personas
  (name → tone):
  - `friendly` → **OmiGuide**: thân thiện, kiên nhẫn như gia sư 1-1; giải thích ngắn rồi hỏi lại 1 câu kiểm tra hiểu; không phán xét.
  - `coach` → **Coach Omi**: nghiêm túc, thẳng vấn đề, đặt tiêu chuẩn; sau mỗi câu trả lời giao 1 bài tập nhỏ / tiêu chí hoàn thành.
  - `socratic` → **Socratic Omi**: dẫn dắt bằng câu hỏi gợi mở, không bật đáp án ngay; luôn hỏi 1-2 câu cho học sinh tự suy luận trước.
  - `genz` → **Omi Buddy**: trẻ trung, năng lượng, bullet ngắn, analogies vui vừa đủ, luôn có bước tiếp theo.
- **Grounding (RAG):** accept `project_id`; build context from the project's attached sources. Start
  simple (concatenate + truncate to a token budget); upgrade to chunk + keyword/embedding retrieval
  for large source sets. Offline fallback = the existing `offline_doc_answer`.
- **History:** `ChatMessage` model (`id, project_id, role[user|assistant], content, persona,
  created_at`). `POST /api/chat` persists both turns; `GET /api/projects/{id}/messages` returns history.

### 4. Lesson plan / roadmap (GIÁO ÁN) + Artifacts (RECENT ARTIFACTS)
- **Roadmap:** `POST /api/projects/{id}/roadmap` → ordered objectives, each
  `{order, title, section}` ("Thuộc phần: ..."). AI (`response_schema`) with an offline fallback that
  derives objectives from `nlp` keywords/sections of the sources. Reuse/extend the existing
  `/api/generate_path` (`LearningPathSchema`).
- **Artifact store:** `Artifact` model (`id, project_id, type[quiz|flashcards|notes|concept_map|
  roadmap], title, data(JSON as String), created_at`). When any generator runs for a project, also
  save an artifact. Endpoints: `GET /api/projects/{id}/artifacts` (list, newest first),
  `GET /api/artifacts/{id}` (full data). This powers "RECENT ARTIFACTS".

### 5. Search learning materials (the Search modal)
- `POST /api/search_materials` `{query}` → list of `{title, url, source[youtube|web|material], snippet}`.
  Use a real search/YouTube API if a key is configured; otherwise return a clearly-labeled empty/stub
  result (the modal copy already says "Nhập từ khóa rồi bấm Search để lấy tài liệu thật từ API").

### 6. Google Drive auto-sync (hero: "đồng bộ mỗi 10 phút … cache về MinIO")
- Frontend already does Drive OAuth (`src/utils/googleDrive.js`) and imports via the upload endpoint.
  Backend: optional `POST /api/drive/sync` to ingest a batch, and a background scheduler
  (`asyncio`/APScheduler) for the 10-minute sync. MinIO/object-storage caching is optional — local
  `uploads/` is fine for now; document MinIO as a later swap.

### 7. Users & AI-token usage (optional but in the UI)
- If you persist per-user data: `User` model (`id, google_sub, email, name, picture`), verify the
  Google ID token server-side (`POST /api/auth/google`), and stamp `user_id` on projects/documents.
- **AI tokens:** the sidebar shows "AI TOKENS … còn lại / Đã dùng". Track usage (a `TokenUsage` row or
  counter per request) and expose `GET /api/usage`.

### Build order (recommended)
Projects → generalized multi-format ingestion + `kind`/`/file` media types → persona+grounded chat
with history → roadmap + artifact store → search materials → Drive sync → users/usage.

---

## Gotchas
- Restart the backend after backend edits (no auto-reload). Run it from `backend/venv`.
- Vite Fast Refresh preserves `useMemo`/state across edits — for a clean test, hard-reload the page.
- Existing documents uploaded before this session have **no raw PDF on disk**, so `has_file` is false and
  the PDF viewer must fall back gracefully. New uploads (and the backfilled doc 7) work.
- The quiz modal is opened by the Studio sidebar's **"Create Exam"** button (`setIsExamOpen`).
- Don't enter real credentials or complete the Google consent popup programmatically — that's the user's action.
