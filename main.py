"""CLI 聊天機器人（第 49-56 堂 MCP 專案的主程式）。

第 52 堂起：main.py 接上 mcp_client.py。開始時先問 mcp_server.py 要工具清單，
轉成 Claude 的 tools 參數格式；Claude 要用工具時，透過 MCPClient 真正執行，
Claude 從沒直接碰過 mcp_server.py（48 堂的重點）。

第 54 堂：輸入裡的 `@文件名` 被偵測到就直接讀資源、把內容塞進送給 Claude
的訊息——不必透過工具呼叫，Claude 開局就拿到內容。課程原版有自動完成
選單 UI，這支 CLI 只做偵測與注入這個機制本身，UI 不是教學重點就先省略。

第 56 堂：輸入 `/prompt名 參數` 時，不送去給 Claude，而是直接向伺服器
要這個 prompt 展開後的訊息，取代使用者輸入——這是三種 MCP 元件裡唯一
「使用者主動選」的一種，跟 `@mention`（App 決定注入）、工具呼叫
（Claude 自己決定）都不同。目前只有 `format` 這個 prompt、只有一個
`doc_id` 參數，所以簡化成「`/` 後第一個詞是 prompt 名，剩下整段當
`doc_id`」，沒有做通用的多參數解析。

用法：uv run main.py
"""

import asyncio
import re

from chat_helpers import add_user_message, client, model
from mcp_client import MCPClient

MENTION_RE = re.compile(r"@(\S+)")
PROMPT_RE = re.compile(r"^/(\S+)\s+(.+)$")


async def inject_mentions(mcp: MCPClient, text: str) -> str:
    doc_ids = MENTION_RE.findall(text)
    if not doc_ids:
        return text

    blocks = []
    for doc_id in doc_ids:
        content = await mcp.read_resource(f"docs://documents/{doc_id}")
        blocks.append(f'<document id="{doc_id}">\n{content}\n</document>')

    return text + "\n\n" + "\n\n".join(blocks)


async def expand_prompt(mcp: MCPClient, text: str) -> str | None:
    match = PROMPT_RE.match(text)
    if not match:
        return None

    prompt_name, doc_id = match.groups()
    messages = await mcp.get_prompt(prompt_name, {"doc_id": doc_id})
    return messages[0].content.text


def tool_schema(tool):
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    }


def print_text_blocks(response):
    for block in response.content:
        if block.type == "text":
            print(f"Claude: {block.text}")


async def build_tool_results(mcp: MCPClient, response):
    results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        result = await mcp.call_tool(block.name, block.input)
        text = "\n".join(c.text for c in result.content if c.type == "text")
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": text,
            "is_error": result.isError,
        })
    return results


async def run_conversation(mcp: MCPClient, messages, tools):
    while True:
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=messages,
            tools=tools,
        )
        messages.append({"role": "assistant", "content": response.content})
        print_text_blocks(response)

        if response.stop_reason != "tool_use":
            return

        results = await build_tool_results(mcp, response)
        messages.append({"role": "user", "content": results})


async def main():
    async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as mcp:
        tools = [tool_schema(t) for t in await mcp.list_tools()]
        messages = []
        while True:
            user_input = input("You: ")
            if user_input.lower() in ("quit", "exit"):
                break
            expanded = await expand_prompt(mcp, user_input)
            if expanded is None:
                expanded = await inject_mentions(mcp, user_input)
            add_user_message(messages, expanded)
            await run_conversation(mcp, messages, tools)


if __name__ == "__main__":
    asyncio.run(main())
