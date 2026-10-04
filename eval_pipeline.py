"""評估流水線（Day 20 第 12 堂起）。

職責分三層，每層只做一件事：

    run_prompt(test_case)   把提示範本和測試案例合併，送出去拿輸出
    run_test_case(test_case) 呼叫 run_prompt，然後對結果評分
    run_eval(dataset)        對每一筆呼叫 run_test_case，收集結果

跟 chat_helpers 一樣，後面每一堂都在這個模組上長東西（第 13 堂加模型評分，
第 14 堂加程式碼評分），舊的課程 script 不能壞。
"""

import ast
import json
import re
from pathlib import Path
from statistics import mean

from chat_helpers import add_assistant_message, add_user_message, chat, client, model

DATASET_PATH = Path(__file__).parent / "dataset.json"

# 版本 1：刻意寫得很弱，之後要靠評估分數把它改好
PROMPT_TEMPLATE = """
Please provide a solution to the following task:
{task}
"""


def load_dataset():
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


# 版本 2（第 14 堂）：把格式要求講明白，並用不指定語言的預填逼它只給原始程式碼
PROMPT_TEMPLATE_V2 = """
Please provide a solution to the following task:
{task}

* Respond only with Python, JSON, or a plain Regex
* Do not add any comments or commentary or explanation
"""


def run_prompt(test_case, template=PROMPT_TEMPLATE, prefill=None):
    """把測試案例塞進提示範本，拿 Claude 的輸出。"""
    prompt = template.format(task=test_case["task"])
    messages = []
    add_user_message(messages, prompt)
    if prefill:
        add_assistant_message(messages, prefill)
        return chat(messages, stop_sequences=["```"])
    return chat(messages)


GRADER_PROMPT = """
You are an expert code reviewer. Evaluate this AI-generated solution.

Task: {task}
Solution: {solution}

Provide your evaluation as a structured JSON object with:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your assessment
- "score": A number between 1-10
"""


GRADER_SCHEMA = {
    "type": "object",
    "properties": {
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "reasoning": {"type": "string"},
        "score": {"type": "number"},
    },
    "required": ["strengths", "weaknesses", "reasoning", "score"],
    "additionalProperties": False,
}


def grade_by_model(test_case, output):
    """模型評分器：再呼叫一次 API 來評這次的輸出。

    關鍵在於同時要 strengths / weaknesses / reasoning。
    只問分數的話，模型傾向一律給 6 分左右——拿到一堆沒有鑑別力的中等分。

    課程用預填 ```json ＋ 停止序列來拿 JSON，但這裡會炸：評分理由常常引用
    regex（\\d、\\.），那些反斜線在 JSON 字串裡是非法跳脫，json.loads 直接
    JSONDecodeError。改用第 8 堂的 structured outputs，由 schema 保證合法。
    """
    prompt = GRADER_PROMPT.format(task=test_case["task"], solution=output)
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": GRADER_SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


VALIDATORS = {
    "json": lambda t: json.loads(t),
    "python": lambda t: ast.parse(t),
    "regex": lambda t: re.compile(t),
}


def grade_syntax(output, test_case):
    """程式碼評分器：解析得過給 10、不過給 0。

    「程式碼評分器」指的是「用程式碼寫的評分器」，不是「評程式碼的評分器」。
    這裡剛好在評程式碼，是因為這個專案的受測提示在生成程式碼。
    """
    validator = VALIDATORS.get(test_case.get("format"))
    if validator is None:
        return 0
    try:
        validator(output.strip())
        return 10
    except (json.JSONDecodeError, SyntaxError, re.error, ValueError):
        return 0


def grade_combined(test_case, output):
    """內容品質用模型判、語法對不對用程式判，等權重合分。"""
    grade = grade_by_model(test_case, output)
    syntax = grade_syntax(output, test_case)
    return {
        **grade,
        "model_score": grade["score"],
        "syntax_score": syntax,
        "score": (grade["score"] + syntax) / 2,
    }


def run_test_case(test_case, grader=None, template=PROMPT_TEMPLATE, prefill=None):
    """跑一筆並評分。

    課程直接改寫 run_test_case 的內容，這裡改成傳入 grader，
    讓第 12 堂的 script 重跑時仍然看到硬編碼的 10 分。
    """
    output = run_prompt(test_case, template, prefill)
    if grader is None:
        return {"output": output, "test_case": test_case, "score": 10}
    grade = grader(test_case, output)
    return {"output": output, "test_case": test_case, **grade}


def run_eval(dataset, grader=None, template=PROMPT_TEMPLATE, prefill=None):
    """對整個資料集跑一輪。"""
    return [run_test_case(tc, grader, template, prefill) for tc in dataset]


RESULTS_PATH = Path(__file__).parent / "results.json"


def save_results(results, path=RESULTS_PATH):
    """把整輪結果存檔。

    課程沒做這件事，但不存就看不到 Claude 到底寫了什麼——分數再漂亮，
    你也沒有可以回頭讀的輸出。改提示之後要比較前後差異也需要它。
    """
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def average_score(results):
    """平均分。課程寫在 run_eval 裡，這裡拆出來，才不會改掉它的回傳形狀。"""
    return mean(r["score"] for r in results)
