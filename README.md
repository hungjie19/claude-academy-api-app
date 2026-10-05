# claude-academy-api-app

Working code for the Claude Academy course
"Building with the Claude API" (使用 Claude API 建構應用程式), 67 lessons.
Theory notes live in the vault: `~/ai_session_summary/ironman/2026_10_03_day2*.md`.

## Requirements

- Python 3.13, managed by `uv`
- `anthropic`, `python-dotenv`

## Setup

```bash
cp .env.example .env   # then paste the real API key into .env (.env is gitignored)
uv sync
uv run smoke_test.py   # verify the key, the SDK and the model id all work
```

## Scripts

| File | What it does |
|---|---|
| `smoke_test.py` | Minimal `messages.create` call; prints text, `stop_reason`, token usage |
| `list_models.py` | Lists the models this API key can actually call |
| `chat_helpers.py` | Shared `add_user_message` / `add_assistant_message` / `chat` |
| `class_NN_*.py` | One file per course lesson, numbered course-wide (1-67) |

Lessons that build one program over several classes share a plain-named file instead
(`reminder_app.py` for lessons 20-29, for example); each class is one commit on that file,
so `git log --oneline -- <file>` is the lesson-by-lesson history.

## Progress

The vault notes split the 67 lessons across six study days (Day 20-25). That grouping lives
in the notes; this table only tracks how far the code has got.

| Day | Lessons | Sections | Status |
|---|---|---|---|
| Day 20 | 1-14 | Accessing Claude via the API / Prompt evaluation | Done through lesson 14 (09, 10 are theory-only) |
| Day 21 | 15-31 | Prompt engineering / Tool use | Not started |
| Day 22 | 32-38 | RAG and agentic search | Not started |
| Day 23 | 39-46 | Claude's capabilities | Not started |
| Day 24 | 47-56 | Model Context Protocol | Not started |
| Day 25 | 57-67 | Anthropic applications / Agents and workflows | Not started |
