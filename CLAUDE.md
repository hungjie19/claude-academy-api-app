# claude-academy-api-app

Code for the Claude Academy course "Building with the Claude API" (67 lessons, split
across Day 20/21/22 of a 30-day study schedule). One lesson at a time.

## Commits

- Commit messages are **English**, conventional-commits format (`feat:`, `fix:`, `chore:`, `docs:`).
- One lesson, one commit: `feat: class NN <topic>`. If a lesson changes `chat_helpers.py`,
  that change belongs in the same commit as the lesson that introduced it — not batched
  with later lessons.
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
- `chat_helpers.py` holds the shared `add_user_message` / `add_assistant_message` /
  `chat` functions. Each lesson that adds a parameter to `chat()` edits that file;
  earlier lesson scripts must keep working, so new parameters get defaults.
- Packages go through `uv add` / `uv run`. Never `pip install`.
- The API key lives only in `.env` — never in code, never in a commit, never in chat.
- Theory notes live in the vault (`~/ai_session_summary/ironman/`). Do not copy them
  here; this repo holds runnable code only.
