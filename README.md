# claude-academy-api-app

Working code for the Claude Academy course
"Building with the Claude API" (使用 Claude API 建構應用程式), 67 lessons.
Theory notes live outside this repo.

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
| `eval_pipeline.py` | Lesson 11-14 evaluation pipeline (code-generation task) |
| `prompt_evaluator.py` | Lesson 15+ `PromptEvaluator`: dataset generation, concurrent runs, model grading, HTML report |
| `meal_plan_prompts.py` | Lesson 15-19 shared setup and one `build_prompt_vN` per lesson |
| `class_NN_*.py` | One file per course lesson, numbered course-wide (1-67) |

Lessons that build one program over several classes share a plain-named file instead
(`reminder_app.py` for lessons 20-29, for example); each class is one commit on that file,
so `git log --oneline -- <file>` is the lesson-by-lesson history.

## Progress

`git log --oneline` is the progress record: one lesson, one commit (`feat: class NN <topic>`).
