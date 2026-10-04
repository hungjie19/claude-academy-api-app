"""最小連線測試：確認 API key、SDK、模型字串都通。

用法：uv run smoke_test.py
"""

import os

from dotenv import load_dotenv

from anthropic import Anthropic

load_dotenv()

client = Anthropic()  # 自動讀 ANTHROPIC_API_KEY
model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")

message = client.messages.create(
    model=model,
    max_tokens=1000,  # 安全上限，不是目標長度
    messages=[
        {"role": "user", "content": "What is quantum computing? Answer in one sentence"}
    ],
)

print(message.content[0].text)
print(f"\n[model] {model}")
print(f"[stop_reason] {message.stop_reason}")
print(f"[usage] in={message.usage.input_tokens} out={message.usage.output_tokens}")
