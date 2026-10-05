"""Day 21 第 19 堂：提供範例。

one-shot（一個範例）建立模式，multi-shot（多個範例）涵蓋不同情境。
範例用 XML 包，並且說明它為什麼好，不只貼配對。

官方的最佳實務：
- 用 XML 標籤組織範例
- 明確說明範例展示什麼
- 範例要能解決最常見的失敗
- 解釋為什麼這個輸出是理想的
- 範例跟任務相關

官方的做法是從評估結果挑高分輸出當範例，讓提示工程和評估形成閉環。
這裡沒有可直接取用的高分輸出（評估結果只在 HTML 報告裡），所以範例是手寫的。
這是偏離課程的地方。

這堂只改一件事：v4 前面加上範例。

用法：uv run class_19_examples.py
"""

from meal_plan_prompts import build_prompt_v4, build_prompt_v5, compare, ensure_dataset
from prompt_evaluator import PromptEvaluator

evaluator = PromptEvaluator(max_concurrent_tasks=3)
ensure_dataset(evaluator, num_cases=3)

averages = compare(
    evaluator,
    {
        "v4": build_prompt_v4,
        "v5": build_prompt_v5,
    },
)

delta = averages["v5"] - averages["v4"]
print(f"{averages['v4']:.2f} -> {averages['v5']:.2f}（{delta:+.2f}）")
print("-> 改動量：前面加一組 example（sample_input + ideal_output）。")
print("-> 三筆案例的雜訊很大（同一提示跨次執行可差 1 分以上），小差距不足以下結論。")
