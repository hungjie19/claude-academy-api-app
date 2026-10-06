"""第 4 堂：多輪對話。

課程的關鍵句：Claude 不會儲存任何對話歷史，每個請求都完全獨立。
這支 script 把「沒帶歷史」和「有帶歷史」各跑一次，差別自己看。

用法：uv run class_04_multiturn.py
"""

from chat_helpers import add_assistant_message, add_user_message, chat

FIRST = "Write a one-sentence description of the ocean."
FOLLOW_UP = "Write another one."

print("[A] 沒帶歷史：每個請求各自獨立")

messages = []
add_user_message(messages, FIRST)
print(f"user      > {FIRST}")
print(f"assistant > {chat(messages)}")

# 重開一個空清單 —— 模擬「忘記把歷史帶上」
messages = []
add_user_message(messages, FOLLOW_UP)
print(f"user      > {FOLLOW_UP}")
print(f"assistant > {chat(messages)}")
print("-> Claude 不知道 another one 指什麼，於是自己挑了一個方向發揮（可能是一整篇小說）。")

print("\n[B] 帶歷史：把 assistant 回應 append 回清單再送")

messages = []
add_user_message(messages, FIRST)
print(f"user      > {FIRST}")
answer = chat(messages)
print(f"assistant > {answer}")

add_assistant_message(messages, answer)  # 關鍵：把回應寫回歷史
add_user_message(messages, FOLLOW_UP)
print(f"user      > {FOLLOW_UP}")
print(f"assistant > {chat(messages)}")

print(f"-> messages 最後有 {len(messages)} 則：{[m['role'] for m in messages]}")
print("對話狀態是你的責任，不是 API 的責任。")
