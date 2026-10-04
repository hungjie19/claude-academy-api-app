"""評估流水線（Day 20 第 12 堂起）。

職責分三層，每層只做一件事：

    run_prompt(test_case)   把提示範本和測試案例合併，送出去拿輸出
    run_test_case(test_case) 呼叫 run_prompt，然後對結果評分
    run_eval(dataset)        對每一筆呼叫 run_test_case，收集結果

跟 chat_helpers 一樣，後面每一堂都在這個模組上長東西（第 13 堂加模型評分，
第 14 堂加程式碼評分），舊的課程 script 不能壞。
"""

import json
from pathlib import Path

from chat_helpers import add_user_message, chat

DATASET_PATH = Path(__file__).parent / "dataset.json"

# 版本 1：刻意寫得很弱，之後要靠評估分數把它改好
PROMPT_TEMPLATE = """
Please provide a solution to the following task:
{task}
"""


def load_dataset():
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def run_prompt(test_case):
    """把測試案例塞進提示範本，拿 Claude 的輸出。"""
    prompt = PROMPT_TEMPLATE.format(task=test_case["task"])
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)


def run_test_case(test_case):
    """跑一筆並評分。"""
    output = run_prompt(test_case)
    score = 10  # TODO - Grading（第 13、14 堂才補上真正的評分）
    return {"output": output, "test_case": test_case, "score": score}


def run_eval(dataset):
    """對整個資料集跑一輪。"""
    return [run_test_case(test_case) for test_case in dataset]
