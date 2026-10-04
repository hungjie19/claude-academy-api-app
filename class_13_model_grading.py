"""Day 20 第 13 堂：基於模型的評分。

三種評分器：程式碼評分器（自訂邏輯）、模型評分器（再呼叫一次 API）、
人工評分器。這堂做模型評分器，因為「任務遵循」這條標準靠程式碼判不出來。

最關鍵的洞見：評分時要同時要 strengths / weaknesses / reasoning。
只問分數，模型會一律回 6 分左右——拿到一堆沒有鑑別力的中等分。

用法：uv run class_13_model_grading.py
"""

from eval_pipeline import (
    average_score,
    grade_by_model,
    load_dataset,
    run_eval,
    save_results,
)

dataset = load_dataset()
print(f"資料集 {len(dataset)} 筆，每筆要跑兩次 API（生成 + 評分）...\n")

results = run_eval(dataset, grader=grade_by_model)

for i, r in enumerate(results, 1):
    print(f"{i}. [score={r['score']}] {r['test_case']['task'][:50]}")
    print(f"   優點：{'; '.join(r['strengths'][:2])}")
    print(f"   缺點：{'; '.join(r['weaknesses'][:2])}")

print(f"\nAverage score: {average_score(results)}")
print(f"完整輸出存到 {save_results(results).name}（含每筆的 output 原文與評分理由）")
print("-> 分數有高有低才代表評分器在工作；全都是 6 分就是沒給 reasoning 的症狀。")
