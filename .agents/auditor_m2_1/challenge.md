## Challenge Summary

**Overall risk assessment**: LOW-MEDIUM

## Challenges

### [Medium] Concurrency in Database Startup Schema-Patching
- **Assumption challenged**: The API server assumes that executing `patch_database_schema(engine)` on every startup is safe and handles table upgrades.
- **Attack scenario**: In a multi-worker production environment (e.g. Uvicorn with `--workers > 1`), concurrent workers executing `patch_database_schema` at the exact same startup time might try to run `ALTER TABLE` concurrently, causing SQLite locks (`database is locked` error).
- **Blast radius**: The server fails to start or database queries block, throwing 500 errors.
- **Mitigation**: Use a real migration tool (like Alembic) rather than a dynamic startup function.

### [Low-Medium] Dependency Fallback degradation on NLTK/spaCy failure
- **Assumption challenged**: Offline NLP algorithms assume that spaCy's `en_core_web_sm` model and NLTK's `wordnet` corpus are always present in the environment.
- **Attack scenario**: If the local env is not set up correctly (or is corrupted), `spacy.load` fails and `extract_quiz` degrades to `_fallback_quiz` which is a simple regex-based word-blanking mechanism that does not understand grammar.
- **Blast radius**: The quality of quiz and flashcard generation degrades significantly, although the endpoints remain functional (graceful degradation).
- **Mitigation**: Provide pre-downloaded package files bundled with the application distribution.

### [Low] Multi-review spaced repetition on the same day
- **Assumption challenged**: The spaced repetition (SM-2) implementation assumes reviews happen at most once a day per card.
- **Attack scenario**: If a user reviews a card multiple times within the same day, `sm2_update` will increment repetitions and intervals repeatedly on that day.
- **Blast radius**: The card's interval will artificially inflate, pushing the next due date far into the future without actual spaced delay.
- **Mitigation**: Track the last review date and only apply the SM-2 state transition if a new calendar day has started.

## Stress Test Results
- **Uvicorn pipe buffer deadlock** → High concurrent request output fills buffers → Deadlocks the backend process → Resolved by not piping stdout/stderr or using file redirections.
- **Vietnamese glues syllables desegmentation** → Sentences with glued bigrams → Desegmented correctly → PASS.
