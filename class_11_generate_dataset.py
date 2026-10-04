"""Day 20 第 11 堂：生成測試資料集。

從這堂開始做一個完整的評估系統。被評估的目標提示要能寫出
AWS 相關的 Python / JSON 設定 / 正規表示式，而且輸出要乾淨、不含說明。

第一步是測試資料集：一個 JSON 陣列，每個物件有一個 task 屬性。
可以手寫，也可以叫 Claude 生成——官方明說這正是該用 Haiku 這種
便宜快的模型、而不是完整版 Claude 的時機。這是成本意識第一次出現在課程裡。

解析用第 8 堂的預填＋停止序列。

用法：uv run class_11_generate_dataset.py
"""

import json
from pathlib import Path

from chat_helpers import add_assistant_message, add_user_message, chat

DATASET_PATH = Path(__file__).parent / "dataset.json"
N_TASKS = 6

prompt = f"""
Generate an evaluation dataset for a prompt evaluation process.
The dataset will be used to evaluate prompts that generate Python, JSON,
or Regex specifically for AWS-related tasks.

Generate an array of JSON objects, each representing a task that requires
Python, JSON, or a Regex to complete.

Example output:
[
  {{"task": "Write a Python function that calculates the factorial of a number"}},
  {{"task": "Write a JSON object representing an S3 bucket policy"}}
]

* Focus on tasks that can be solved by writing a single Python function,
  a single JSON object, or a single regular expression.
* Focus on tasks that do not require writing much code.

Please generate {N_TASKS} objects.
"""

messages = []
add_user_message(messages, prompt)
add_assistant_message(messages, "```json")
text = chat(messages, stop_sequences=["```"])

try:
    dataset = json.loads(text.strip())
except json.JSONDecodeError as e:
    print("JSON 解析失敗（多半是被 max_tokens 截斷），原始輸出：")
    print(text)
    raise SystemExit(1) from e

DATASET_PATH.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

print(f"生成 {len(dataset)} 筆，存到 {DATASET_PATH.name}：\n")
for i, item in enumerate(dataset, 1):
    print(f"  {i}. {item['task']}")
