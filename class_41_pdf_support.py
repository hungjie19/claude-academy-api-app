"""第 41 堂：PDF 支援。

程式碼跟圖片幾乎一樣，四個差異：副檔名 .png -> .pdf、變數名 image_bytes -> file_bytes、
type 從 "image" -> "document"、media_type -> "application/pdf"。

這支額外做一個比較：同一份內容，原生 PDF（document 區塊）vs 先抽成純文字再送，
兩種送法的 input token 用量差多少。這裡直接呼叫 client 而不是 chat_helpers.chat()，
因為要讀 message.usage，chat() 只回傳最終文字字串。

測試文件 reef_report.pdf：用 macOS 內建 cupsfilter 從一段虛構的珊瑚白化測試報告
文字轉出來的一頁 PDF，純粹拿來測 PDF 讀取與摘要能力，數據不是真實研究結果。
PLAIN_TEXT 是同一份內容的純文字版本，兩個請求問同一個問題，比較才公平。

用法：uv run class_41_pdf_support.py
"""

import base64

from chat_helpers import client, model

with open("reef_report.pdf", "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

PLAIN_TEXT = """Coral Reef Bleaching: A 2024 Field Summary (Test Document)

This is a fabricated test document for the Claude API course, used to exercise PDF
support and citations. The numbers below are illustrative, not real research data.

Background

Coral bleaching occurs when sustained ocean temperature increases cause corals to
expel the symbiotic algae living in their tissues, draining the coral of its color
and a major energy source. Repeated or prolonged bleaching events raise coral
mortality significantly.

Survey Findings

Across the twelve reef sites surveyed in this exercise, average sea surface
temperature was 1.8 degrees Celsius above the ten-year seasonal baseline. Seven of
the twelve sites recorded bleaching coverage above 40 percent of live coral cover.
The two sites with the highest water flow showed the lowest bleaching coverage,
at 12 percent and 15 percent respectively, suggesting that circulation may offer
some thermal buffering.

Recovery Observations

Sites revisited after ninety days showed partial pigment recovery in roughly a
third of previously bleached colonies, while the remaining colonies either died or
remained bleached. Recovery correlated most strongly with depth: colonies below
eight meters recovered at roughly twice the rate of shallow colonies.

Recommendation

The summary recommends prioritizing monitoring at shallow, low-flow sites, since
this exercise's data shows they combine the highest bleaching incidence with the
lowest recovery rate.
"""

QUESTION = (
    "Summarize this document in two sentences, and name the single site "
    "characteristic most strongly linked to low recovery."
)


def ask_with_pdf():
    return client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {
                    "type": "base64", "media_type": "application/pdf", "data": file_bytes}},
                {"type": "text", "text": QUESTION},
            ],
        }],
    )


def ask_with_plain_text():
    return client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": PLAIN_TEXT},
                {"type": "text", "text": QUESTION},
            ],
        }],
    )


if __name__ == "__main__":
    pdf_message = ask_with_pdf()
    print("--- 原生 PDF（document 區塊）---")
    print(pdf_message.content[0].text)
    print(f"input_tokens={pdf_message.usage.input_tokens}")

    text_message = ask_with_plain_text()
    print("\n--- 先抽成純文字 ---")
    print(text_message.content[0].text)
    print(f"input_tokens={text_message.usage.input_tokens}")
