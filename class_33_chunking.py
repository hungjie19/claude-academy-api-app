"""第 33 堂：文字分塊策略。

RAG 的第一步是把文件切成塊。官方的失敗案例：文件有醫學與軟體工程兩章，
使用者問「工程師修了多少 bug」，卻拿到醫學章節，因為那邊也出現了 "bug" 這個詞。
切法決定了搜尋會拿到什麼，所以分塊不是小事。

四種做法：
  1. 基於大小：等長切，要加 overlap，否則句子斷在中間、上下文會斷掉
  2. 基於結構：照 Markdown 標題切，前提是文件真的有結構
  3. 基於語意：要 NLP，最準也最貴，這堂不做
  4. 基於句子：實用折衷，這堂做

官方的建議：不確定文件結構時，帶重疊的基於大小分塊通常是首選。

用法：uv run class_33_chunking.py
"""

import re

SAMPLE = """
## Medical research
Researchers reported a new bug in the drug trial protocol. The bug delayed enrollment by six weeks.
Patients were monitored for side effects. No serious adverse events were recorded.

## Software engineering
Engineers fixed 42 bugs in the payment service this quarter. Most were race conditions.
The team also reduced build time by thirty percent. Code review was required for every merge.
""".strip()


def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    """等長切，相鄰兩塊重疊 chunk_overlap 個字元，避免上下文在切點斷掉。"""
    chunks = []
    start_idx = 0
    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)
    return chunks


def chunk_by_section(document_text):
    """照 Markdown 的 "## " 標題切。文件沒有這種結構時，這個函式等於什麼都沒做。"""
    return [part.strip() for part in re.split(r"\n## ", document_text) if part.strip()]


def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    """每塊最多幾句，相鄰兩塊重疊幾句。"""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks = []
    start_idx = 0
    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        chunks.append(" ".join(sentences[start_idx:end_idx]))
        if end_idx == len(sentences):
            break
        start_idx += max_sentences_per_chunk - overlap_sentences
    return chunks


if __name__ == "__main__":
    print("== 基於大小（150 字元，重疊 20）==")
    for i, c in enumerate(chunk_by_char(SAMPLE), 1):
        print(f"[{i}] {c!r}")

    print("\n== 基於結構（照 ## 標題）==")
    for i, c in enumerate(chunk_by_section(SAMPLE), 1):
        print(f"[{i}] {c[:60]!r}...")

    print("\n== 基於句子（每塊 2 句，重疊 1 句）==")
    for i, c in enumerate(chunk_by_sentence(SAMPLE, max_sentences_per_chunk=2, overlap_sentences=1), 1):
        print(f"[{i}] {c!r}")
