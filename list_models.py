"""列出這把 API key 實際可用的模型。

用法：uv run list_models.py
"""

from dotenv import load_dotenv

from anthropic import Anthropic

load_dotenv()

client = Anthropic()

for m in client.models.list():  # 會自動翻頁
    ctx = getattr(m, "max_input_tokens", None)
    out = getattr(m, "max_tokens", None)
    print(f"{m.id:<28} {m.display_name:<22} ctx={ctx} out={out}")
