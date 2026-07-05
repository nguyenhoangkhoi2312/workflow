### Handle Project vs. Standalone Document Contexts
When building or modifying features (UI components, APIs, or Database Models) in this application, you MUST ensure they support both **Project** contexts (`project_id`) and **Standalone Document** contexts (`document_id`).
- **Database**: If a feature (like Roadmaps, Invites, etc.) applies to documents, ensure its model supports an optional `document_id` alongside `project_id`.
- **Frontend**: Check if the current view is a Project or a Standalone Document, and pass the appropriate ID to the backend APIs. Do not assume `project_id` is always present.
- **Backend**: API endpoints should gracefully handle missing `project_id`s by falling back to `document_id` where applicable.

### File Serving & Uploads
When serving user-uploaded documents (e.g., PDFs, Images) by matching IDs in the `uploads/` directory with `glob.glob`, you MUST filter out auxiliary `.txt` files (e.g., `[f for f in files if not f.endswith('.txt')]`). The app automatically generates `.txt` cache files for text extraction, and serving them instead of the original media will cause the Frontend viewer to break or trigger unwanted downloads.
Additionally, when returning `FileResponse` from FastAPI for files intended to be viewed inline (e.g. inside an iframe), you MUST explicitly set `filename=os.path.basename(file_path)` and `content_disposition_type="inline"`. Otherwise, the browser may default to downloading the file as an attachment.

### AI Generation & DB Idempotency
When re-generating 1-to-many AI artifacts (e.g., Roadmaps, Quizzes, Flashcards) for a `project_id` or `document_id`, you MUST explicitly `delete()` the existing parent and child items from the database before inserting the newly generated ones. Failure to do so will cause duplicate items to accumulate on every "Generate" action.

### OmiGuide UI Layout & Tool Placement
When building or adding new learning tools (e.g., Flashcards, Quizzes, Summaries, Mindmaps) to the Right Pane (`DocumentViewer.jsx`), you MUST adhere to the following OmiGuide layout principles:
1. **No Bulky Studio Grid:** Do NOT place learning tools in a large button grid inside a "Studio Tab".
2. **Right-Edge Vertical Toolbar:** For Modal-based tools (e.g., Quizzes, Flashcards, Mindmaps, Smart Notes, Study Docs), place them as small, rounded icon buttons in a vertically stacked toolbar stuck to the absolute right edge of the screen.
3. **Chat-Driven Action Pills:** For text-processing or prompt-based features (e.g., Summarize, Translate, Outline, Interview, Give Example), place them as horizontal "Action Pills" directly above the Chat input box. Clicking them should automatically send a prompt to the AI in the chat thread.
4. **Color & Styling:** Follow the OmiGuide aesthetic: light beige backgrounds (`#FAFAF9`), maroon user messages (`#8A334C`), and pill-shaped inputs with thin tan borders (`#D6C5B3`).
5. **Left Sidebar Restrictions:** DO NOT place learning feature buttons in the left navigation sidebar (`ProjectStudioSidebar.jsx`). The left sidebar is strictly reserved for File Management, Persona selection, and Roadmaps.

### macOS Browser Automation Workaround
When the user requires browser automation but the host environment is macOS, the native `open_browser_url` tool will fail. Do NOT report this as a hard failure. Instead:
1. Instruct the user to open Google Chrome, navigate to `chrome://inspect/#remote-debugging`, and check **"Allow remote debugging for this browser instance"**.
2. Once the user confirms, the browser will expose the Chrome DevTools Protocol at `127.0.0.1:9222`.
3. Invoke the `browser` subagent, explicitly mentioning that a remote Chrome debugger is running at `127.0.0.1:9222`. The subagent is equipped with the `chrome-devtools` MCP server and will automatically connect to it and perform the required browser automation tasks.

### Project Naming & Branding
When building, modifying, or referring to this application, you MUST always use the name **"Workflow"** (or "Workflow AI"). 
Even though you may be instructed to clone features, layouts, or logic from "OmiLearn" or "OmiGuide", you MUST NEVER use the string "OmiLearn" or "Omilearn" anywhere in the application's user-facing UI, logos, or empty states. Always replace references to the external inspiration (OmiLearn) with the actual project name (Workflow).

### Dictionary & Vocabulary Processing Fallbacks
When building or modifying dictionary lookups, synonym generation, or vocabulary additions in the Workflow app:
1. **Prioritize Offline/Free APIs:** Always implement robust fallbacks that do not require cloud AI keys (e.g., Gemini). Utilize `FreeDictionaryAPI` for definitions/phonetics, `NLTK WordNet` for offline synonyms, and `deep-translator` for offline/free translations. 
2. **Lookup First UX:** Vocabulary search bars should default to performing a debounced dictionary lookup to display a "Lookup Card" with full details (IPA, meaning, examples, synonyms) *before* the user decides to add the word to their personal bank.
3. **Static Content Banks:** Vocabulary and Writing banks (`vocab_bank.py` / `writing.py`) must be pure, curated, and fully static data. Do not wire them to generate content dynamically via AI at runtime.

### Long Lists & Viewport Management
When rendering potentially long lists (e.g., Vocabulary Banks, generated Q&A) in the right pane or side panels, you MUST wrap the list in a collapsible Accordion/Drawer (e.g., using `<details>` and `<summary>`) and apply a scrollable container (`max-height` and `overflow-y: auto`). This prevents the list from dominating the viewport and pushing primary action buttons off-screen.

### Spaced Repetition System (SRS) Integrity
When implementing or modifying Spaced Repetition features (e.g., Flashcards, Vocabulary Review), you MUST strictly filter queries to only include items where `due_date <= today`. Do not return items that have already been learned but are not yet due for review.

### Dictionary Grammar Tag Extraction
When parsing definitions from offline sources like `FreeDictionaryAPI`, you MUST explicitly extract and represent detailed grammatical classifications by searching the definition strings for keywords like "plural", "countable", and "uncountable". Ensure that combinations (e.g., "countable / uncountable") are handled and displayed clearly.
