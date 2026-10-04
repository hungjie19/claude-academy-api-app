"""Day 20 第 5 堂：系統提示。

同一個學生問題問兩次，差別只在有沒有 system prompt。
系統提示定的是「角色與行為邊界」，不是「更長的使用者訊息」。

用法：uv run class_05_system_prompt.py
"""

from chat_helpers import add_user_message, chat

QUESTION = "How do I solve for x in 5x + 2 = 3?"

SYSTEM_PROMPT = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""

print("[A] 沒有 system prompt")
messages = []
add_user_message(messages, QUESTION)
print(f"student > {QUESTION}")
print(f"claude  > {chat(messages)}")

print("\n[B] 有 system prompt（數學家教）")
messages = []
add_user_message(messages, QUESTION)
print(f"student > {QUESTION}")
print(f"claude  > {chat(messages, system=SYSTEM_PROMPT)}")
print("-> B 應該是反問式引導，不是直接給 x = 1/5。")
