"""第 42 堂：Citations。

啟用只要在 document 區塊加 "citations": {"enabled": True}。重點不是怎麼開（一行事），
是回應結構變了：答案文字被切成好幾段，每一段各自帶自己的 citations 清單（可能是空的），
不是回應最後附一包清單。這支直接印出切段結果，讓這件事看得見。

直接呼叫 client 而不是 chat_helpers.chat()：chat() 只回傳 content[0].text，
會把切段跟 citations 資訊全部丟掉。

複用第 41 堂的 reef_report.pdf（虛構的珊瑚白化測試報告）。

用法：uv run class_42_citations.py
"""

import base64

from chat_helpers import client, model

with open("reef_report.pdf", "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model=model,
    max_tokens=500,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": file_bytes},
                "title": "reef_report.pdf",
                "citations": {"enabled": True},
            },
            {"type": "text", "text": "What percentage of sites had bleaching coverage above 40 percent, "
                                      "and what characteristic was most linked to low recovery?"},
        ],
    }],
)

if __name__ == "__main__":
    for i, block in enumerate(message.content):
        print(f"--- 區塊 {i}：{block.text!r}")
        if not block.citations:
            print("    (無引用)")
            continue
        for c in block.citations:
            pages = f"p.{c.start_page_number}-{c.end_page_number}"
            print(f"    引用自 {c.document_title} {pages}: {c.cited_text!r}")
