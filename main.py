"""CLI 聊天機器人（第 49-56 堂 MCP 專案的主程式）。

第 52 堂起：main.py 接上 mcp_client.py。開始時先問 mcp_server.py 要工具清單，
轉成 Claude 的 tools 參數格式；Claude 要用工具時，透過 MCPClient 真正執行，
Claude 從沒直接碰過 mcp_server.py（48 堂的重點）。

用法：uv run main.py
"""

import asyncio

from chat_helpers import add_user_message, client, model
from mcp_client import MCPClient


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
            add_user_message(messages, user_input)
            await run_conversation(mcp, messages, tools)


if __name__ == "__main__":
    asyncio.run(main())
