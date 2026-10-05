"""Day 21 第 16 堂：清晰且直接。

**提示的第一行是整個請求中最重要的部分。**

- 清晰：用任何人都能理解的簡單語言，開頭就直接陳述 Claude 的任務
- 直接：用指示句而非問句，以直接的動作動詞開頭（寫、建立、生成）

官方的對照：「我想知道那些人們放在屋頂上、利用太陽的東西」->
「寫三段關於太陽能板如何運作的文字。」

這堂**只改第 15 堂提示的開頭那一行**，其他部分一字不動——
提示工程的紀律是一次只改一項，否則分數動了你也不知道是哪一招的功勞。

官方實測：2.32 -> 3.92

用法：uv run class_16_clear_direct.py
"""

from meal_plan_prompts import build_prompt_v1, build_prompt_v2, compare, ensure_dataset
from prompt_evaluator import PromptEvaluator

evaluator = PromptEvaluator(max_concurrent_tasks=3)
ensure_dataset(evaluator, num_cases=3)

averages = compare(
    evaluator,
    {
        "v1": build_prompt_v1,
        "v2": build_prompt_v2,
    },
)

delta = averages["v2"] - averages["v1"]
print(f"{averages['v1']:.2f} -> {averages['v2']:.2f}（{delta:+.2f}）")
print("-> 改動量：一行問句換成一行指示句。官方同一步是 2.32 -> 3.92。")
