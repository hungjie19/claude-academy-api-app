"""Day 21 第 17 堂：具體明確。

兩種指引，專業應用裡常常一起用：

1. **輸出品質指引**——列出輸出該有的特質：回應長度、結構與格式、
   需包含的特定屬性或元素、語氣或風格要求。**幾乎每個提示都該有**，
   它是拿到一致結果的安全網。
2. **流程步驟**——給 Claude 該 follow 的具體步驟，適合你希望它有系統地思考、
   或在下結論前考量多個角度。**留給複雜問題**（排解問題、決策、批判性思考）。

這堂用第一種：在 v2 後面接六條 Guidelines。本質上是把「我沒說但我預期」的
東西講出來——效果比任何花招都大。

官方實測：3.92 -> 7.86，形容「輸出品質提升了一倍以上」。

用法：uv run class_17_be_specific.py
"""

from meal_plan_prompts import build_prompt_v2, build_prompt_v3, compare, ensure_dataset
from prompt_evaluator import PromptEvaluator

evaluator = PromptEvaluator(max_concurrent_tasks=3)
ensure_dataset(evaluator, num_cases=3)

averages = compare(
    evaluator,
    {
        "v2": build_prompt_v2,
        "v3": build_prompt_v3,
    },
)

delta = averages["v3"] - averages["v2"]
print(f"{averages['v2']:.2f} -> {averages['v3']:.2f}（{delta:+.2f}）")
print("-> 改動量：六條輸出品質指引。官方同一步是 3.92 -> 7.86。")
print("-> 這六條有四條是直接呼應 extra_criteria——評估標準講得出來的要求，")
print("   就該寫進提示；評估不是只用來打分，它也是提示的規格書。")
