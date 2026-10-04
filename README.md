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

## Progress

| Day | Sections | Status |
|---|---|---|
| Day 20 | Accessing Claude via the API / Prompt evaluation / Prompt engineering | In progress — lesson 5 of 19 |
| Day 21 | Tool use / RAG / Claude's capabilities | Not started |
| Day 22 | MCP / Anthropic applications / Agents and workflows | Not started |
