"""第 8 堂：結構化資料。

場景：做一個產生 AWS EventBridge 規則的 App，使用者要能直接複製整段 JSON。
但 Claude 預設很愛幫忙——把 JSON 包進 markdown 程式碼區塊，前後再加說明。

課程解法：助手訊息預填（prefill）＋ 停止序列（stop sequences）。
通則是「先認出 Claude 自然會用什麼包裝你的內容，再把那個包裝拿來當預填與停止序列」。

警告：prefill 在 4.6 以後的世代會回 400，只有 Haiku 4.5 這類舊模型還能跑。
現行做法是 structured outputs（[C] 段），不需要跟模型的格式習慣鬥智。

用法：uv run class_08_structured_data.py
"""

import json

from chat_helpers import add_assistant_message, add_user_message, chat, client, model

PROMPT = "Generate a very short event bridge rule as json"

print("[A] 直接要 JSON：Claude 會幫你包裝")
messages = []
add_user_message(messages, PROMPT)
raw = chat(messages)
print(raw)
try:
    json.loads(raw)
    print("-> 竟然可以直接 parse（少見）")
except json.JSONDecodeError as e:
    print(f"-> json.loads() 失敗：{e.msg}。使用者得自己手動選取。")

print("\n[B] 課程解法：預填 ```json ＋ 停止序列 ```")
messages = []
add_user_message(messages, PROMPT)
add_assistant_message(messages, "```json")  # 讓 Claude 以為已經開始寫程式碼區塊
text = chat(messages, stop_sequences=["```"])  # 它想收尾時立刻切斷
print(text.strip())
print(f"-> json.loads() 成功，keys = {list(json.loads(text.strip()))}")

print("\n[C] 現行做法：structured outputs（prefill 的替代品）")
response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[{"role": "user", "content": PROMPT}],
    output_config={
        "format": {
            "type": "json_schema",
            # 每一層 object 都要明確寫 additionalProperties: False，
            # 漏掉巢狀那層會回 400。
            "schema": {
                "type": "object",
                "properties": {
                    "Name": {"type": "string"},
                    "EventPattern": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "array", "items": {"type": "string"}},
                            "detail-type": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["source", "detail-type"],
                        "additionalProperties": False,
                    },
                },
                "required": ["Name", "EventPattern"],
                "additionalProperties": False,
            },
        }
    },
)
out = next(b.text for b in response.content if b.type == "text")
print(out.strip())
print(f"-> schema 保證回傳合法 JSON，keys = {list(json.loads(out))}")
print("-> B 是用 Claude 的格式習慣綁住它，C 是直接規定輸出形狀。")
