"""第 7 堂：回應串流。

要解的是 UX 問題：一次回應可能要 10-30 秒，使用者只能盯著 loading。
串流把同一個請求拆成一連串事件，邊生成邊顯示。

三段：原始事件 -> SDK 的簡化介面 -> 串完再組一份完整訊息。

用法：uv run class_07_streaming.py
"""

from collections import Counter

from chat_helpers import client, model

PROMPT = "Explain what an API is, in three sentences."

print("[A] 原始事件：stream=True 自己解析")
stream = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[{"role": "user", "content": PROMPT}],
    stream=True,
)
counts = Counter(event.type for event in stream)
for name, n in counts.items():
    print(f"  {name:<28} x{n}")
print("-> 文字在 content_block_delta 裡，其他事件是信封不是內容。")

print("\n[B] SDK 簡化介面：text_stream 只給你文字")
with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=[{"role": "user", "content": PROMPT}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # [C] 串完還是要一份完整訊息給應用邏輯用（存 DB、算 token、看 stop_reason）
    final = stream.get_final_message()

print("\n\n[C] get_final_message()：串流與完整訊息兩者兼得")
print(f"  stop_reason = {final.stop_reason}")
print(f"  usage       = in={final.usage.input_tokens} out={final.usage.output_tokens}")
print(f"  文字長度     = {len(final.content[0].text)} 字元")
