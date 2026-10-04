"""Day 20 第 12 堂：執行評估。

這堂刻意把評分寫死成 10 分（eval_pipeline 裡的 TODO），
目的是讓整條流水線先跑起來，之後再回頭做評分器。
先用假分數接通、再做評分，比一開始就想把評分做對實用得多。

官方提醒：第一次跑整個資料集，就算用 Haiku 也可能要 30 秒左右。

用法：uv run class_12_run_eval.py
"""

import time

from eval_pipeline import load_dataset, run_eval

dataset = load_dataset()
print(f"資料集 {len(dataset)} 筆，開始跑...\n")

start = time.perf_counter()
results = run_eval(dataset)
elapsed = time.perf_counter() - start

for i, r in enumerate(results, 1):
    first_line = r["output"].strip().splitlines()[0]
    print(f"{i}. [score={r['score']}] {r['test_case']['task'][:52]}")
    print(f"   輸出開頭：{first_line[:66]}")

print(f"\n耗時 {elapsed:.1f} 秒，每筆結果固定三個欄位：output / test_case / score")
print("分數全是 10，因為評分還沒做——但流水線已經通了。")
