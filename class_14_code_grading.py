"""第 14 堂：基於程式碼的評分。

三條標準終於湊齊：
  1. 格式（只回傳程式碼）  -> 程式碼評分器
  2. 有效語法              -> 程式碼評分器
  3. 任務遵循              -> 模型評分器（第 13 堂）

程式碼評分器＝用程式碼寫的評分器，不是評程式碼的評分器。
這裡剛好在評程式碼，是因為受測的提示在生成程式碼。

評分器要知道該用哪個驗證器，所以測試案例多一個 format 欄位，
資料集要重新生成。

這支 script 跑兩輪，對照提示 v1 與 v2：
  v1 = 原本那句 "Please provide a solution to the following task"
  v2 = 加上「只回傳程式碼、不要任何說明」＋ ```code 預填

官方對分數的態度：分數不是本質上的好或壞，
重點是你能不能靠改提示把它提上去。

用法：uv run class_14_code_grading.py
"""

import json

from chat_helpers import add_assistant_message, add_user_message, chat
from eval_pipeline import (
    DATASET_PATH,
    PROMPT_TEMPLATE,
    PROMPT_TEMPLATE_V2,
    average_score,
    grade_combined,
    load_dataset,
    run_eval,
    save_results,
)

N_TASKS = 6

GENERATE_PROMPT = f"""
Generate an evaluation dataset for a prompt evaluation process.
The dataset will be used to evaluate prompts that generate Python, JSON,
or Regex specifically for AWS-related tasks.

Generate an array of JSON objects, each representing a task that requires
Python, JSON, or a Regex to complete.

Example output:
[
  {{
    "task": "Write a Python function that calculates the factorial of a number",
    "format": "python"
  }},
  {{
    "task": "Write a JSON object representing an S3 bucket policy",
    "format": "json"
  }}
]

* "format" must be exactly one of: "python", "json", "regex"
* Focus on tasks that can be solved by writing a single Python function,
  a single JSON object, or a single regular expression.
* Focus on tasks that do not require writing much code.

Please generate {N_TASKS} objects.
"""


def regenerate_dataset():
    """重新生成資料集，這次每筆帶 format 欄位。"""
    messages = []
    add_user_message(messages, GENERATE_PROMPT)
    add_assistant_message(messages, "```json")
    dataset = json.loads(chat(messages, stop_sequences=["```"]).strip())
    DATASET_PATH.write_text(
        json.dumps(dataset, indent=2) + "\n", encoding="utf-8"
    )
    return dataset


dataset = load_dataset()
if "format" not in dataset[0]:
    print("資料集沒有 format 欄位，重新生成...")
    dataset = regenerate_dataset()
print(f"資料集 {len(dataset)} 筆：{[d['format'] for d in dataset]}\n")


def report(label, results):
    print(f"[{label}]")
    for i, r in enumerate(results, 1):
        fmt = r["test_case"]["format"]
        print(
            f"  {i}. {fmt:<6} 模型 {r['model_score']:>4} / "
            f"語法 {r['syntax_score']:>2} -> {r['score']}"
        )
    avg = average_score(results)
    print(f"  Average score: {avg:.2f}\n")
    return avg


results_v1 = run_eval(dataset, grader=grade_combined, template=PROMPT_TEMPLATE)
avg_v1 = report("提示 v1：原本那句", results_v1)

results_v2 = run_eval(
    dataset,
    grader=grade_combined,
    template=PROMPT_TEMPLATE_V2,
    prefill="```code",
)
avg_v2 = report("提示 v2：明講只回傳程式碼 + ```code 預填", results_v2)

save_results({"v1": results_v1, "v2": results_v2})
print(f"{avg_v1:.2f} -> {avg_v2:.2f}（{avg_v2 - avg_v1:+.2f}）")
print("-> 語法分是二元的，不會像模型分那樣全部擠在 6~7 之間。")
print("-> 分數不是本質上的好或壞，重點是能不能靠改提示把它提上去。")
