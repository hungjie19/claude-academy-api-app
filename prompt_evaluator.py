"""課程 `PromptEvaluator` 的自刻版（第 15 堂起）。

課程 notebook 直接 import 一個現成的 `PromptEvaluator`，但那支程式碼不在這個
repo 裡，所以照官方介紹的介面自己寫一份：`generate_dataset` 生測試資料、
`run_evaluation` 跑評估，加上併發與一份 HTML 報告。

為什麼不直接長在 eval_pipeline 上：資料形狀變了。那邊一筆是
{"task": ..., "format": ...}，受測提示只有一個洞；這邊一筆是
{"task": ..., "solution_criteria": [...], "prompt_inputs": {...}}，
提示有多個具名輸入，評分標準還要由呼叫端用 extra_criteria 補。
硬塞進同一個模組會讓第 11-14 堂的 script 跟著一起改，所以另開一支。

併發官方建議從 3 起跳，避免撞 rate limit，配額夠再往上調。
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from html import escape
from statistics import mean

from chat_helpers import add_assistant_message, add_user_message, chat, client

# CLAUDE.md 的規則：評分模型不能比被評的模型弱，否則評估沒有意義。
# 生成用 .env 的 ANTHROPIC_MODEL（Haiku），評分固定用 Sonnet。
GRADER_MODEL = os.getenv("ANTHROPIC_GRADER_MODEL", "claude-sonnet-5-5")

GENERATE_PROMPT = """
Generate an evaluation dataset for the prompt described below.

<task_description>
{task_description}
</task_description>

The prompt under test receives these named inputs:
{spec_lines}

Generate an array of {num_cases} JSON objects. Each object must have:
- "task": one sentence describing what the prompt must produce for this case
- "solution_criteria": an array of 2-4 short, objective criteria a grader can check
- "prompt_inputs": an object with exactly these keys: {keys}

* Make the cases meaningfully different from each other.
* Keep every input value realistic and internally consistent.

Example output:
[
  {{
    "task": "...",
    "solution_criteria": ["...", "..."],
    "prompt_inputs": {{{example_inputs}}}
  }}
]
"""

GRADER_PROMPT = """
You are grading the output of a prompt that is under evaluation.

<task>
{task}
</task>

<prompt_inputs>
{prompt_inputs}
</prompt_inputs>

<solution_criteria>
{solution_criteria}
</solution_criteria>
{extra_criteria_block}
<output>
{output}
</output>

Judge how well the output satisfies the criteria for these exact inputs.
Be strict: a missing required element is a real deduction, not a rounding error.
"""

# 跟 eval_pipeline 同一個教訓：只問分數的話模型一律回 6 分左右，
# 要同時要 strengths / weaknesses / reasoning 才有鑑別力。
GRADER_SCHEMA = {
    "type": "object",
    "properties": {
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "reasoning": {"type": "string"},
        # 上下界一定要宣告：只寫 number 的話評分模型偶爾會用百分制回答
        # （實際撞到過 68 和 0.4），平均分直接被污染。
        "score": {"type": "number", "minimum": 1, "maximum": 10},
    },
    "required": ["strengths", "weaknesses", "reasoning", "score"],
    "additionalProperties": False,
}


class PromptEvaluator:
    def __init__(self, max_concurrent_tasks=3):
        self.max_concurrent_tasks = max_concurrent_tasks

    def generate_dataset(
        self, task_description, prompt_inputs_spec, output_file, num_cases=3
    ):
        """生測試資料集。開發階段 2-3 筆就好，迭代才快；最終驗證再加量。"""
        prompt = GENERATE_PROMPT.format(
            task_description=task_description.strip(),
            spec_lines="\n".join(
                f'- "{k}": {v}' for k, v in prompt_inputs_spec.items()
            ),
            num_cases=num_cases,
            keys=", ".join(f'"{k}"' for k in prompt_inputs_spec),
            example_inputs=", ".join(f'"{k}": "..."' for k in prompt_inputs_spec),
        )
        messages = []
        add_user_message(messages, prompt)
        add_assistant_message(messages, "```json")
        text = chat(messages, stop_sequences=["```"], max_tokens=2000)
        dataset = json.loads(text.strip())
        output_file.write_text(
            json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return dataset

    def run_evaluation(
        self, run_prompt_function, dataset_file, extra_criteria=None, report_file=None
    ):
        """對整個資料集跑受測提示並評分，回傳每筆的結果。

        extra_criteria 是這一堂的重點之一：有些要求（熱量總量、三大營養素、
        份量與時間）不在資料集的 solution_criteria 裡，但你確實在意，
        就從呼叫端告訴評分模型。
        """
        dataset = json.loads(dataset_file.read_text(encoding="utf-8"))
        with ThreadPoolExecutor(max_workers=self.max_concurrent_tasks) as pool:
            results = list(
                pool.map(
                    lambda case: self._run_case(
                        case, run_prompt_function, extra_criteria
                    ),
                    dataset,
                )
            )
        if report_file is not None:
            self._write_report(results, report_file)
        return results

    def _run_case(self, case, run_prompt_function, extra_criteria):
        output = run_prompt_function(case["prompt_inputs"])
        grade = self._grade(case, output, extra_criteria)
        return {"test_case": case, "output": output, **grade}

    def _grade(self, case, output, extra_criteria):
        extra = ""
        if extra_criteria:
            extra = f"\n<extra_criteria>\n{extra_criteria.strip()}\n</extra_criteria>\n"
        prompt = GRADER_PROMPT.format(
            task=case["task"],
            prompt_inputs=json.dumps(case["prompt_inputs"], ensure_ascii=False, indent=2),
            solution_criteria="\n".join(f"- {c}" for c in case["solution_criteria"]),
            extra_criteria_block=extra,
            output=output,
        )
        # 用第 8 堂的 structured outputs，不用預填 ```json：評分理由常引用
        # 反斜線，JSON 字串裡是非法跳脫，json.loads 會直接炸。
        response = client.messages.create(
            model=GRADER_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            output_config={"format": {"type": "json_schema", "schema": GRADER_SCHEMA}},
        )
        text = next(b.text for b in response.content if b.type == "text")
        # structured outputs 保證「合法 JSON」，但保證不了「寫完了」：被 max_tokens
        # 切斷的 JSON 一樣是壞的。第 16 堂就踩到——提示改好之後輸出變長，
        # 評分理由跟著變長，1000 tokens 不夠，json.loads 丟 Unterminated string。
        # 截斷要當成錯誤講清楚，不要讓它假扮成解析失敗。
        if response.stop_reason == "max_tokens":
            raise RuntimeError(
                "評分模型的回應被 max_tokens 截斷，調高 _grade 的 max_tokens"
            )
        return json.loads(text)

    def _write_report(self, results, report_file):
        """官方的 evaluator 會吐一份 HTML 報告，這裡做一份最小可用的。

        分數看趨勢，報告看原因——改提示之後哪個案例變好、評分模型抓到什麼缺點，
        只有讀得到輸出原文才判斷得出來。
        """
        rows = []
        for i, r in enumerate(results, 1):
            rows.append(
                f"""
<section>
  <h2>#{i} &mdash; {r["score"]}/10</h2>
  <p class="task">{escape(r["test_case"]["task"])}</p>
  <pre class="inputs">{escape(json.dumps(r["test_case"]["prompt_inputs"], ensure_ascii=False, indent=2))}</pre>
  <h3>Output</h3>
  <pre class="output">{escape(r["output"])}</pre>
  <h3>Grader</h3>
  <p><b>Strengths</b></p><ul>{"".join(f"<li>{escape(s)}</li>" for s in r["strengths"])}</ul>
  <p><b>Weaknesses</b></p><ul>{"".join(f"<li>{escape(w)}</li>" for w in r["weaknesses"])}</ul>
  <p class="reasoning">{escape(r["reasoning"])}</p>
</section>"""
            )
        html = f"""<!doctype html>
<meta charset="utf-8">
<title>Prompt evaluation report</title>
<style>
  body {{ font: 15px/1.6 -apple-system, sans-serif; max-width: 52rem; margin: 2rem auto; padding: 0 1rem; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: .3rem; }}
  section {{ border: 1px solid #ddd; border-radius: 6px; padding: 1rem; margin: 1.5rem 0; }}
  pre {{ background: #f6f6f6; padding: .8rem; border-radius: 4px; white-space: pre-wrap; }}
  .task {{ font-weight: 600; }}
  .inputs {{ font-size: 13px; }}
  .reasoning {{ color: #444; font-style: italic; }}
</style>
<h1>Average score: {average_score(results):.2f} / 10</h1>
{"".join(rows)}
"""
        report_file.write_text(html, encoding="utf-8")
        return report_file


def average_score(results):
    return mean(r["score"] for r in results)
