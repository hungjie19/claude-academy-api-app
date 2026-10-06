"""第 34 堂：文字嵌入。

嵌入是把一段文字轉成一串數字（向量），每個數字在 -1 到 +1 之間。
語意相近的文字，向量的夾角小，餘弦相似度高。

Anthropic 不提供嵌入，這堂改用 Voyage AI，需要在 .env 設定 VOYAGE_API_KEY。
模型用免費額度內的 voyage-4（voyage-3-large 不在免費額度內）。

用法：uv run class_34_embeddings.py
"""

import math

import voyageai
from dotenv import load_dotenv

load_dotenv()
client = voyageai.Client()  # 自動讀取環境變數 VOYAGE_API_KEY


def generate_embedding(text, model="voyage-4", input_type="query"):
    """把一段文字或文字列表轉成向量。文件用 input_type="document"，查詢用 "query"。

    傳字串回傳一個向量，傳列表回傳對應的向量列表。免費額度沒綁付款時限制 3 RPM，
    所以多段文字盡量一次送出。
    """
    texts = [text] if isinstance(text, str) else text
    result = client.embed(texts, model=model, input_type=input_type)
    return result.embeddings[0] if isinstance(text, str) else result.embeddings


def cosine_similarity(a, b):
    """兩向量的餘弦相似度：接近 1 很相似，0 無關，接近 -1 很不同。"""
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


if __name__ == "__main__":
    medical = "研究團隊今年對 XDR-47 取得了重大進展，這是一種我們以前從未見過的病毒。"
    software = "工程團隊重構了付款系統，並把建置時間縮短了三成。"
    query = "軟體團隊今年做了什麼？"

    medical_vec, software_vec = generate_embedding([medical, software], input_type="document")
    query_vec = generate_embedding(query)

    print(f"向量維度：{len(query_vec)}")
    print(f"前 5 個數字：{[round(x, 4) for x in query_vec[:5]]}")
    print(f"所有數字都在 -1 到 +1 之間：{all(-1 <= x <= 1 for x in query_vec)}")

    print(f"\n查詢 vs 軟體段：{cosine_similarity(query_vec, software_vec):.3f}")
    print(f"查詢 vs 醫學段：{cosine_similarity(query_vec, medical_vec):.3f}")
