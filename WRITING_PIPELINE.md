# Luyện viết (Writing Practice) — Framework, Pipeline & Feature Parity

Modeled on **english.datpmt.com** ("Master English Through Interactive Translation") and
informed by **omilearn.com**. Explored live in Chrome 2026-07 (both practice flows sit
behind sign-in; structure captured from the open pages + level/task/category selectors).

## What the real datpmt site actually does (full complexity — do NOT simplify)

**Three writing modes**, each Level → (Category | Task) → practice:

1. **Sentence** — Level (Beginner/Intermediate/Advanced) → **20 categories**:
   Personal & Communication, Everyday Life, Transportation & Travel, School & Education,
   Work & Business, Public Services, Health & Medicine, Shopping & Money, Food & Drink,
   Entertainment & Leisure, Nature & Environment, Science & Technology, Culture & Society,
   Government & Politics, History & Geography, Sports & Fitness, Arts & Literature,
   Religion & Spirituality, Law & Justice, Philosophy & Ethics.
2. **Paragraph** — Level → content type (Emails, Diaries, Essays, Articles).
3. **IELTS** — Level (with **band targets**: Beginner 5.0–6.0, Intermediate 6.5–7.0,
   Advanced 8.0+; time est. 15–40 min) → **Task 1** (describe charts/graphs/processes,
   formal report) **AND Task 2** (opinion/discussion essay). *I originally shipped Task 2 only.*

**Curated exercise bank + progress** (the big differentiator): IELTS Task 2 alone lists
**539 exercises**, paginated (90 pages). Each exercise card shows: the English prompt title,
a **Vietnamese context/framing paragraph**, an **Attempt: N** counter, a **"New"** badge, and
**"Never / last-attempted"** timestamp. So practice is a tracked curriculum, not one-shot random gen.

**Cross-cutting study features:**
- **Interactive word lookup** — click any word → dictionary definition (api.datpmt.com/api/v1/dictionary).
- **Audio pronunciation** — a sound icon per word/sentence (Google TTS).
- **Vocabulary** bank (saved words, behind login).
- **Rank / Leaderboard** — global points ranking (points per exercise; ~2999 pages of users) = gamification.
- **Speaking / Pronunciation** (Beta) — separate spoken practice.

## Omilearn features worth borrowing (study value)
- **Teach-back / Active Learning** — you explain a concept to the AI; it verifies and awards XP +
  a memory-retention % (Feynman technique).
- **Streak** tracking (🔥 N-day) and **XP**.
- **Non-linear / branching chat** — each question opens its own thread branch.
- Spaced repetition (already have SM-2 flashcards), smart quiz reminders.

## Implementation status in Workflow (this app)

DONE (v1): setup (mode/level/category) → practice → grade → summary → save-to-flashcards,
sentence + paragraph + IELTS-Task2, AI grading with VN error explanations + offline fallback,
non-blocking toast. Backend `nlp/writing.py` + 3 endpoints.

TO ADD for parity (build via agy pipeline):
1. **All 20 sentence categories** (was 10) in seed bank + UI.
2. **IELTS Task 1** (chart/process description) with its own prompt + report grading.
3. **Band descriptors per criterion** shown in IELTS feedback (per level target band).
4. **Word lookup**: click a word in a sentence → popover with definition + example (AI, offline fallback)
   + **audio pronunciation** (Google TTS URL, already used elsewhere).
5. **Progress + points**: persist writing attempts (score, date) → a small stats/points panel;
   optional local leaderboard placeholder.
6. **Teach-back mode** (stretch): explain-to-AI with retention %.

## Pipeline (unchanged)
GENERATE `/api/writing/lessons/generate` → ATTEMPT (client) → GRADE `/api/writing/grade`
(+`/api/writing/ielts/grade`) → SUMMARY → VOCAB (reuse `/api/generate_flashcards`).
New: `/api/writing/word` (dictionary lookup), `/api/writing/attempts` (progress log).

## Engine rules (every AI feature)
`api_key` from localStorage `workflow_api_key` (`''`→backend .env Gemini, `OFFLINE`, `LOCAL`).
All AI via `agent_run(...)` with a deterministic offline fallback — endpoints never 500.
Never hardcode keys. Vietnamese UI. Inline styles only.
