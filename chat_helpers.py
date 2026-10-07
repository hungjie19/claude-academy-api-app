"""課程的三個核心輔助函式（第 4 堂）。

後面每一堂都在 chat() 上加參數（system prompt、temperature、streaming...），
所以這組函式放在共用模組，不要每支 script 重抄一次。
"""

import os

from dotenv import load_dotenv

from anthropic import Anthropic

load_dotenv()

client = Anthropic()
model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def chat(messages, system=None, temperature=None, stop_sequences=None, max_tokens=1000,
         thinking=False, thinking_budget=1024):
    # max_tokens 從第 15 堂起要調大：餐食計畫帶熱量、三大營養素、份量與時間，
    # 1000 tokens 會被截斷，而截斷的輸出會讓評估分數測到的是截斷、不是提示。
    params = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    # API 不接受 system=None，只有真的有值時才塞進去
    if system:
        params["system"] = system
    # 課程寫 temperature=1.0 直接當參數傳，但 anthropic SDK 1.x 已經把
    # temperature / top_p / top_k 從 messages.create() 的簽名移除
    # （4.6 以後的世代送了會 400）。舊模型如 Haiku 4.5 仍然接受，
    # 所以用 extra_body 直接塞進 request body 繞過 SDK 的簽名。
    if temperature is not None:
        params["extra_body"] = {"temperature": temperature}
    # 第 39 堂：擴展思考。budget_tokens 最小 1024；max_tokens 必須大於它，
    # 所以這裡把 thinking_budget 加在呼叫端要的輸出 max_tokens 之上，而不是取代它。
    if thinking:
        params["max_tokens"] = thinking_budget + max_tokens
        params["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
    message = client.messages.create(**params)
    # 開了 thinking 後 content[0] 是 thinking 區塊（沒有 .text），最終文字會在它後面；
    # 印出思考過程讓它可見，再回傳文字區塊本身。
    text = None
    for block in message.content:
        if block.type in ("thinking", "redacted_thinking"):
            label = "思考過程" if block.type == "thinking" else "已編輯思考（內容被加密）"
            print(f"--- {label} ---\n{getattr(block, 'thinking', '<redacted>')}\n")
        elif block.type == "text":
            text = block.text
    return text
