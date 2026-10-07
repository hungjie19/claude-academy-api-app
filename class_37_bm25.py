"""第 37 堂：BM25 lexical search。

跟第 35、36 堂的向量搜尋不同，BM25 是純統計的關鍵字比對：
不看語意、不需要嵌入模型，只看詞彙重疊程度，所以不呼叫任何 API。
對「代號、錯誤碼、專有名詞」這類精確字串，BM25 常常比語意搜尋準，
因為嵌入模型容易把 "INC-2023-Q4-011" 這種字串打散成接近語意、卻失去精確比對能力的向量。

課程原本用 BM25Index，這裡改成本檔內的替代寫法，功能相同但不是課程原始程式。
中文沒有空白分詞，這裡用簡化版 tokenizer：
英數字（含連字號，例如 INC-2023-Q4-011）當一個 token，
中文字則一字一個 token（unigram），只為了示範 BM25 的計算方式，不是正式的中文斷詞方案。

用法：uv run class_37_bm25.py
"""

import math
import re

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
    """英數字（含連字號）當一個 token，中文字一字一個 token。"""
    return TOKEN_RE.findall(text)


class BM25Index:
    """替代課程的 BM25Index：標準 Okapi BM25 公式，k1=1.5、b=0.75。"""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self._docs = []  # [{"tokens": [...], "metadata": {...}}]

    def add_document(self, text, metadata):
        self._docs.append({"tokens": tokenize(text), "metadata": metadata})

    def _idf(self, term):
        n = len(self._docs)
        df = sum(1 for doc in self._docs if term in doc["tokens"])
        if df == 0:
            return 0.0
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def search(self, query, k=1):
        query_terms = tokenize(query)
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
            scored.append((score, doc["metadata"]))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [(meta, score) for score, meta in scored[:k]]


# 步驟 1 分塊
chunks = chunk_by_section(SAMPLE)

# 步驟 2 存進 BM25 索引：不用嵌入，直接存斷詞後的原文
index = BM25Index()
for chunk in chunks:
    index.add_document(chunk, {"content": chunk})

# 步驟 3 查詢：精確代號，考驗的是關鍵字比對，不是語意理解
query = "INC-2023-Q4-011 這起事件處理得如何？"

# 步驟 4 搜尋：分數越高越相關
results = index.search(query, k=2)
for doc, score in results:
    print(f"分數 {score:.3f}")
    print(doc["content"][:200])
    print("----")
