"""第 52 堂：實作客戶端。

mcp_client.py 從這堂開始建立（54、56 堂持續疊上去）。
MCPClient 包一層 ClientSession：session 用完要做資源清理，包起來用
async context manager 自動處理，不用每個呼叫端自己記得收尾。

main.py 對這個類別只需要兩件事：拿工具清單給 Claude、Claude 要用時執行工具。

用法：uv run mcp_client.py（自帶測試：連上 mcp_server.py 印出工具清單）
"""

import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


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


async def main():
    async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as client:
        result = await client.list_tools()
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
