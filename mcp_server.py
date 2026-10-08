"""第 50 堂：用 MCP 定義工具。

mcp_server.py 從這堂開始建立（51-56 堂持續疊上去）。用官方 Python SDK 的
FastMCP：不手寫 JSON schema，靠裝飾器與型別提示自動生成——Day 22 手寫的
description 現在變成 Pydantic 的 Field()。

警告（課程筆記提過要核對）：這支程式只在 mcp<2（裝的是 1.30.0）能跑。
mcp 2.x 把 FastMCP 整個改名成 MCPServer，import 路徑不一樣，pyproject.toml
已經釘住 mcp<2。

用法：mcp dev mcp_server.py（51 堂的 inspector，單獨測這個檔案）
     或由 mcp_client.py 當子程序啟動（52 堂起，經由 uv run main.py）
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditure",
    "outlook.pdf": "This document presents the projected future performance of the",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment",
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(doc_id: str = Field(description="Id of the document to read")):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string.",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(description="The new text to insert in place of the old text."),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)


if __name__ == "__main__":
    mcp.run(transport="stdio")
