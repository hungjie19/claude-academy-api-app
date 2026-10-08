"""第 52 堂：實作客戶端 + 第 54 堂：存取資源 + 第 56 堂：存取 prompts。

mcp_client.py 從 52 堂開始建立。
MCPClient 包一層 ClientSession：session 用完要做資源清理，包起來用
async context manager 自動處理，不用每個呼叫端自己記得收尾。

main.py 對這個類別需要四件事：拿工具清單給 Claude、Claude 要用時執行
工具、`@文件名` 被提及時讀資源內容、`/prompt名 參數` 被輸入時取得
prompt 展開後的訊息。

第 54 堂：read_resource() 只取 result.contents[0]——課程筆記說「通常你
只要第一個元素」。MIME 類型是 application/json 就用 json.loads 還原成
物件，否則就是純文字直接回傳。

第 56 堂：list_prompts()/get_prompt() 直接對應 ClientSession 原生方法，
沒有額外轉換——prompt 的參數（例如 format 的 doc_id）由呼叫端決定要傳
什麼，這裡只是單純轉發。

用法：uv run mcp_client.py（自帶測試：連上 mcp_server.py 印出工具清單）
"""

import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    def __init__(self, command: str, args: list[str], env: dict | None = None):
        self._command = command
        self._args = args
        self._env = env
        self._session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("Client session not initialized. Call connect() first.")
        return self._session

    async def connect(self):
        server_params = StdioServerParameters(command=self._command, args=self._args, env=self._env)
        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        self._session = session

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.cleanup()

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, tool_input: dict) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text

        return resource

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name: str, args: dict[str, str]) -> list[types.PromptMessage]:
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages


async def main():
    async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as client:
        result = await client.list_tools()
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
