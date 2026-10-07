"""第 38 堂：多索引 RAG 管線（hybrid search）。

把 36 堂的向量搜尋（VectorIndex）跟 37 堂的 BM25（BM25Index）接成一條管線：
兩個索引實作同一組介面（add_document / search），用 Retriever 當協調者，
把查詢分別丟給兩個索引、收回各自的排名，再用倒數排名融合
（reciprocal rank fusion，RRF）合併成一份結果：

    RRF_score(d) = Σ 1 / (k_rrf + rank_i(d))

k_rrf 用業界常用的 60（官方示範為了好懂用 1）。RRF 比的是「排名」不是原始分數，
因為 cosine distance 跟 BM25 score 的量級完全不同，直接加總沒有意義。

課程原本的 VectorIndex、BM25Index、Retriever 都沒在本機找到，這裡沿用
36、37 堂的替代寫法，並補上 Retriever：
  - VectorIndex 這堂改成跟 BM25Index 一樣的介面：add_document(document)、
    search(query_text, k)，查詢文字在索引內部轉成向量，呼叫端看不到向量，
    這樣兩個索引才能被 Retriever 用同一套方式對待。
  - 多加了 index_documents(documents) 批次方法：如果照協定逐筆呼叫
    add_document()，5 個文件就是 5 次 Voyage API 呼叫，加上查詢那 1 次，
    一分鐘內會超過免費額度的 3 RPM。這個方法只是把文件一次性 batch 嵌入，
    介面精神不變，純粹是配合真實世界的 rate limit。

需要 VOYAGE_API_KEY。這堂送 2 次請求（文件一次 batch、查詢一次）。

用法：uv run class_38_multi_index_pipeline.py
"""

import math
import re

import voyageai
from dotenv import load_dotenv

load_dotenv()
client = voyageai.Client()

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

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*|[一-鿿]")


def chunk_by_section(document_text):
    """照 Markdown 的 "## " 標題切。"""
    return [part.strip() for part in re.split(r"\n## ", document_text) if part.strip()]


def tokenize(text):
    """英數字（含連字號）當一個 token，中文字一字一個 token。跟第 37 堂相同。"""
    return TOKEN_RE.findall(text)


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
    """向量搜尋索引：add_document/search 都吃原文字串，向量化在內部做。"""

    def __init__(self):
        self._items = []  # [{"embedding": [...], "document": {...}}]

    def add_document(self, document):
        embedding = generate_embedding(document["content"], input_type="document")
        self._items.append({"embedding": embedding, "document": document})

    def index_documents(self, documents):
        """批次版 add_document：所有文件一次嵌入，避免逐筆呼叫撞到 RPM 上限。"""
        embeddings = generate_embedding(
            [doc["content"] for doc in documents], input_type="document"
        )
        for embedding, document in zip(embeddings, documents):
            self._items.append({"embedding": embedding, "document": document})

    def search(self, query_text, k=1):
        query_embedding = generate_embedding(query_text, input_type="query")
        scored = [
            (cosine_distance(query_embedding, item["embedding"]), item["document"])
            for item in self._items
        ]
        scored.sort(key=lambda pair: pair[0])  # 距離越小越相關
        return [(doc, dist) for dist, doc in scored[:k]]

    def __len__(self):
        return len(self._items)


class BM25Index:
    """BM25 詞彙搜尋索引，公式跟第 37 堂相同，介面改成吃 document dict。"""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self._docs = []  # [{"tokens": [...], "document": {...}}]

    def add_document(self, document):
        self._docs.append({"tokens": tokenize(document["content"]), "document": document})

    def index_documents(self, documents):
        for document in documents:
            self.add_document(document)

    def _idf(self, term):
        n = len(self._docs)
        df = sum(1 for doc in self._docs if term in doc["tokens"])
        if df == 0:
            return 0.0
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def search(self, query_text, k=1):
        query_terms = tokenize(query_text)
        avgdl = sum(len(doc["tokens"]) for doc in self._docs) / len(self._docs)

        scored = []
        for doc in self._docs:
            tokens = doc["tokens"]
            doc_len = len(tokens)
            score = 0.0
            for term in query_terms:
                tf = tokens.count(term)
                if tf == 0:
                    continue
                idf = self._idf(term)
                score += idf * (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * (doc_len / avgdl))
                )
            scored.append((score, doc["document"]))

        scored.sort(key=lambda pair: pair[0], reverse=True)  # 分數越高越相關
        return [(doc, score) for score, doc in scored[:k]]

    def __len__(self):
        return len(self._docs)


class Retriever:
    """協調者：把查詢丟給所有索引，用 RRF 合併各自的排名。"""

    def __init__(self, *indexes):
        if len(indexes) == 0:
            raise ValueError("At least one index must be provided")
        self._indexes = list(indexes)

    def index_documents(self, documents):
        """建索引用批次方法，避免逐筆呼叫撞到向量索引的 API rate limit。"""
        for index in self._indexes:
            index.index_documents(documents)

    def add_document(self, document):
        """協定要求的逐筆介面：真的要單筆加文件時用這個（每個索引各呼叫一次）。"""
        for index in self._indexes:
            index.add_document(document)

    def search(self, query_text, k=1, k_rrf=60):
        rrf_scores = {}
        doc_lookup = {}
        for index in self._indexes:
            # 每個索引都回傳「全部文件」的排名，RRF 才能公平比較兩邊
            results = index.search(query_text, k=len(index))
            for rank, (doc, _score) in enumerate(results, start=1):
                key = doc["content"]
                rrf_scores[key] = rrf_scores.get(key, 0.0) + 1 / (k_rrf + rank)
                doc_lookup[key] = doc

        ranked = sorted(rrf_scores.items(), key=lambda pair: pair[1], reverse=True)
        return [(doc_lookup[key], score) for key, score in ranked[:k]]


# 步驟 1 分塊
chunks = chunk_by_section(SAMPLE)
documents = [{"content": chunk} for chunk in chunks]

# 步驟 2 建索引：向量索引 + BM25 索引各自吃同一批文件
retriever = Retriever(VectorIndex(), BM25Index())
retriever.index_documents(documents)

# 步驟 3 查詢：精確代號，考驗向量搜尋的弱點、BM25 的強項
query = "INC-2023-Q4-011 這起事件處理得如何？"

# 步驟 4 混合搜尋：RRF 分數越高越相關
results = retriever.search(query, k=3)
for doc, score in results:
    print(f"RRF {score:.3f}")
    print(doc["content"][:200])
    print("----")
