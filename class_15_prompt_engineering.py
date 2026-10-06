"""第 15 堂：提示工程。

官方把「提示工程」定義成一個可量測的迴圈，不是技巧清單：
  設定目標 -> 寫初始提示 -> 評估 -> 套用技巧 -> 重新評估（重複後兩步）
而且**每次只改一項**，才知道哪一招對你的情境有效。

這堂的工作是立基準線：任務換成「為運動員生成一日餐食計畫」，
用一個刻意很弱的提示（「這個人應該吃什麼？」）跑評估，拿一個難看的分數。
官方先打預防針：第一次拿 10 分中的 2.3 分很常見。

第 16-19 堂會拿同一個資料集、同一組評分標準，一次只改提示的一件事。

用法：uv run class_15_prompt_engineering.py
"""

from meal_plan_prompts import (
    EXTRA_CRITERIA,
    DATASET_PATH,
    REPORT_PATH,
    build_prompt_v1,
    ensure_dataset,
    runner,
)
from prompt_evaluator import PromptEvaluator, average_score

# 官方建議從較低的併發開始（例如 3），避免撞 rate limit，配額夠再往上調
evaluator = PromptEvaluator(max_concurrent_tasks=3)

ensure_dataset(evaluator, num_cases=3)

results = evaluator.run_evaluation(
    run_prompt_function=runner(build_prompt_v1),
    dataset_file=DATASET_PATH,
    extra_criteria=EXTRA_CRITERIA,
    report_file=REPORT_PATH,
)

for i, r in enumerate(results, 1):
    inputs = r["test_case"]["prompt_inputs"]
    print(f"{i}. [score={r['score']}] {inputs['goal']} / {inputs['restrictions']}")
    print(f"   缺點：{'; '.join(r['weaknesses'][:2])}")

print(f"\nAverage score (提示 v1 基準線): {average_score(results):.2f} / 10")
print(f"報告：{REPORT_PATH.name}（每個案例的輸出原文與評分理由）")
print("-> 這個數字難看是刻意的。第 16 堂只改開頭那一行，再跑一次比。")
