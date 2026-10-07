"""第 36 堂：實作 RAG 流程。

五步走完：分塊 → 生成嵌入 → 存進向量庫（向量與原文一起存）→ 查詢嵌入 → 搜尋。
35 堂的假向量在這堂換成真的 Voyage 嵌入，其餘流程不變。

課程原本用 VectorIndex 與 report.md，這裡改成本檔內的替代寫法：
  - VectorIndex：用餘弦相似度暴力搜尋，功能與課程版本相同，但不是課程原始程式。
  - report.md：改用本檔內的 SAMPLE，內容仿照課程的財務報告結構。

需要 VOYAGE_API_KEY。這堂只送 2 次請求（文件一次 batch、查詢一次），不會超過免費額度的 3 RPM。

用法：uv run class_36_rag_pipeline.py
"""

import math
import re

import voyageai
from dotenv import load_dotenv

load_dotenv()
client = voyageai.Client()  # 自動讀取環境變數 VOYAGE_API_KEY

SAMPLE = """
## 公司概況
Acme 是一家做工業感測器的公司，總部在台北，員工約兩千人。

## 財務分析
今年營收成長 12%，主要來自北美市場。毛利率維持在四成左右，費用控制得宜。

## 網路安全
Q4 發生過一起資安事件，編號 INC-2023-Q4-011。事件回應團隊在二十四小時內隔離受影響的系統，並完成根因分析。

## 軟體工程
工程團隊今年重構了付款服務，修了 42 個 bug，並把建置時間縮短了三成。每次合併都需要程式碼審查。

## 法律事務
公司今年新增了兩份供應商合約，並更新了資料保護條款以符合新法規。
""".strip()


def chunk_by_section(document_text):
    """照 Markdown 的 "## " 標題切。"""
    return [part.strip() for part in re.split(r"\n## ", document_text) if part.strip()]


def generate_embedding(text, model="voyage-4", input_type="query"):
    """把一段文字或文字列表轉成向量。文件用 input_type="document"，查詢用 "query"。"""
    texts = [text] if isinstance(text, str) else text
    result = client.embed(texts, model=model, input_type=input_type)
    return result.embeddings[0] if isinstance(text, str) else result.embeddings


def cosine_distance(a, b):
    """餘弦距離 = 1 - 餘弦相似度，越小越相似。"""
    dot = sum(x * y for x, y in zip(a, b))
    sim = dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
    return 1 - sim


class VectorIndex:
    """替代課程的 VectorIndex：向量與原文存在同一筆紀錄，搜尋時暴力比對。"""

    def __init__(self):
        self._items = []

    def add_vector(self, embedding, metadata):
        self._items.append({"embedding": embedding, "metadata": metadata})

    def search(self, query_embedding, k=1):
        scored = [(cosine_distance(query_embedding, item["embedding"]), item["metadata"])
                  for item in self._items]
        scored.sort(key=lambda pair: pair[0])
        return [(meta, dist) for dist, meta in scored[:k]]


# 步驟 1 分塊
chunks = chunk_by_section(SAMPLE)

# 步驟 2 生成嵌入：文件一次 batch 送出
embeddings = generate_embedding(chunks, input_type="document")

# 步驟 3 存進向量庫：嵌入和原文一起存，查詢回來才拿得到文字
store = VectorIndex()
for embedding, chunk in zip(embeddings, chunks):
    store.add_vector(embedding, {"content": chunk})

# 步驟 4 查詢也要嵌入，而且要用同一個模型
user_embedding = generate_embedding("軟體工程部門今年做了什麼？")

# 步驟 5 搜尋：距離越小越相關
results = store.search(user_embedding, k=2)
for doc, distance in results:
    print(f"距離 {distance:.3f}")
    print(doc["content"][:200])
    print("----")
