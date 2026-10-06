"""第 18 堂：使用 XML 標籤建立結構。

問題：提示裡塞大量內容或多種內容時，Claude 可能分不出哪段是指示、哪段是要處理的資料。
解法：用描述性的 XML 標籤把資料包起來，例如 <athlete_information>。
標籤名稱要具體，不必是正式 XML：<athlete_information> 比 <data> 清楚。

官方很誠實：簡單提示可能看不出顯著改善，標籤的價值在內容多、混雜時才顯現。
這堂的提示很短，所以預期 v3 -> v4 的差距小，甚至在雜訊之內。
這正是要用評估來檢查的事，不要憑感覺說標籤有效。

只改一件事：v3 的輸入欄位外面包上 <athlete_information>。

用法：uv run class_18_xml_tags.py
"""

from meal_plan_prompts import build_prompt_v3, build_prompt_v4, compare, ensure_dataset
from prompt_evaluator import PromptEvaluator

evaluator = PromptEvaluator(max_concurrent_tasks=3)
ensure_dataset(evaluator, num_cases=3)

averages = compare(
    evaluator,
    {
        "v3": build_prompt_v3,
        "v4": build_prompt_v4,
    },
)

delta = averages["v4"] - averages["v3"]
print(f"{averages['v3']:.2f} -> {averages['v4']:.2f}（{delta:+.2f}）")
print("-> 改動量：輸入欄位包進 <athlete_information>。")
print("-> 三筆案例的雜訊約 ±0.8，差距小於這個範圍就不能說標籤有效或無效。")
