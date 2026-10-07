"""第 35 堂：完整的 RAG 流程。

這堂用一個刻意簡化的二維例子走完六步：分塊 → 嵌入 → 存進向量庫 → 查詢嵌入 → 找相似 → 組最終提示。
二維向量只是為了看得見：每個向量畫在單位圓上，角度越小越相似。
真實的嵌入是上千維，但流程和算法完全相同。

這堂不呼叫 API，所以不需要 key。

用法：uv run class_35_rag_flow.py
"""

import math


def normalize(vec):
    """把向量縮放成長度 1，嵌入 API 通常會自動做這一步。"""
    length = math.sqrt(sum(x * x for x in vec))
    return [x / length for x in vec]


def cosine_similarity(a, b):
    """兩向量的餘弦相似度：接近 1 很相似，0 無關，接近 -1 很不同。"""
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def cosine_distance(a, b):
    """餘弦距離 = 1 - 餘弦相似度，越小越相似。向量資料庫常用這個。"""
    return 1 - cosine_similarity(a, b)


# 步驟 1 分塊：兩段文字，各是一塊
chunks = {
    "醫學研究": "今年在我們對 XDR-47 的理解上取得了重大進展，這是一種我們以前從未見過的 bug。",
    "軟體工程": "這個部門投入了大量精力研究我們分散式系統中的各種感染途徑。",
}

# 步驟 2 生成嵌入：假設一個「完美模型」只回兩個數字，第一個是談醫學的程度，第二個是談軟體工程的程度
embeddings = {
    "醫學研究": [0.97, 0.34],
    "軟體工程": [0.30, 0.97],
}

# 步驟 3 存進向量庫：嵌入和原文一起存，查詢回來才拿得到文字
vector_store = []
for name, vec in embeddings.items():
    vector_store.append({"content": chunks[name], "embedding": normalize(vec)})

# 步驟 4 處理查詢：這個查詢嵌入後是 [0.1, 0.89]
query = "我對這家公司很好奇。特別是，軟體工程部門今年做了什麼？"
query_vec = normalize([0.1, 0.89])

# 步驟 5 找相似：算每塊跟查詢的相似度與距離，排序
print("== 步驟 5：找相似 ==")
for name, vec in embeddings.items():
    norm_vec = normalize(vec)
    sim = cosine_similarity(query_vec, norm_vec)
    dist = cosine_distance(query_vec, norm_vec)
    print(f"{name}：相似度 {sim:.3f}，距離 {dist:.3f}")

ranked = sorted(vector_store, key=lambda d: cosine_distance(query_vec, d["embedding"]))
top = ranked[0]

# 步驟 6 組最終提示：問題 + 最相關的塊，用 XML 標籤包起來
prompt = f"""<context>
{top["content"]}
</context>

<question>
{query}
</question>"""

print("\n== 步驟 6：最終提示 ==")
print(prompt)
