"""課程的三個核心輔助函式（Day 20 第 4 堂）。

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


def chat(messages, system=None, temperature=None, stop_sequences=None):
    params = {"model": model, "max_tokens": 1000, "messages": messages}
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
    message = client.messages.create(**params)
    return message.content[0].text
