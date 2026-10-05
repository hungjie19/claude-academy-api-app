# claude-academy-api-app

Code for the Claude Academy course "Building with the Claude API" (67 lessons, split
across Day 20-25 of a 30-day study schedule). One lesson at a time.

## Commits

- Commit messages are **English**, conventional-commits format (`feat:`, `fix:`, `chore:`, `docs:`).
- One lesson, one commit: `feat: class NN <topic>`. This holds whether the lesson adds a new
  file or only edits a file an earlier lesson created — the commit *is* that lesson's record.
- Because the commit is the record, never keep a per-lesson snapshot copy of a file that a
  later lesson rewrites. No `class_23_*.py` sitting next to `class_24_*.py` with 90% the
  same code. To get a lesson's version back, use git:

  ```bash
  git log --oneline -- reminder_app.py       # the lessons that touched this file
  git checkout <commit> -- reminder_app.py   # restore that lesson's version
  ```

- If a lesson changes `chat_helpers.py`, that change belongs in the same commit as the
  lesson that introduced it — not batched with later lessons.
- Lessons with no code (quizzes, pure theory) get no commit, which is why the lesson numbers
  have gaps (09, 10). Their content lives in the vault notes.
- The vault (`~/ai_session_summary`) is a separate repo. Never mix its commits with this
  repo's, even when one lesson updates both.
- Never commit unless explicitly asked. "OK" or "looks good" is not a commit instruction.
- `.env` must never be committed. Check `git status` before every commit.

## Docs

- Markdown files in this repo (`README.md`, `CLAUDE.md`) are written in English.
- Code comments and docstrings stay in Traditional Chinese — this is study material,
  and the explanations are the point.

## Models

- Course material says `claude-sonnet-4-5`. That model is **not available** on this
  API key (verified with `list_models.py`), so copying it verbatim fails.
- Default is `claude-haiku-4-5-20251001`, set via `ANTHROPIC_MODEL` in `.env`.
  Cheapest current model at $1/$5 per MTok; plenty for the course exercises.
- When the prompt-evaluation lessons need a grader model, use `claude-sonnet-5-5`.
  A grader weaker than the model it grades makes the evaluation meaningless.
- Never hardcode a model id taken from course material. Query the API (`list_models.py`).

## Conventions

- Lesson files are `class_NN_topic.py`, where `NN` is the **course-wide** lesson number
  (1-67), not the per-day one. Day grouping lives in the vault notes, not here.
- Two kinds of lesson file:
  - **Standalone exercise** — `class_NN_topic.py`, runnable on its own. The default.
  - **Incremental project** — when consecutive lessons build one growing program, it gets a
    plain filename with no `class_NN` prefix (e.g. `reminder_app.py`), and each lesson edits
    it in place and commits as `feat: class NN <topic>`. Keep it one file until that
    genuinely hurts; a split into modules happens inside that lesson's own commit.
- Evaluation scores measured while working through a lesson belong in the vault note, not
  here. `results.json` is gitignored on purpose: the repo holds the runnable prompt, the
  note holds the number it produced.
- `chat_helpers.py` holds the shared `add_user_message` / `add_assistant_message` /
  `chat` functions. Each lesson that adds a parameter to `chat()` edits that file;
  earlier lesson scripts must keep working, so new parameters get defaults.
- Packages go through `uv add` / `uv run`. Never `pip install`.
- The API key lives only in `.env` — never in code, never in a commit, never in chat.
- Theory notes live in the vault (`~/ai_session_summary/ironman/`). Do not copy them
  here; this repo holds runnable code only.
