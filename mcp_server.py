"""第 50 堂：用 MCP 定義工具 + 第 53 堂：定義資源。

mcp_server.py 從 50 堂開始建立（51-56 堂持續疊上去）。用官方 Python SDK 的
FastMCP：不手寫 JSON schema，靠裝飾器與型別提示自動生成——Day 22 手寫的
description 現在變成 Pydantic 的 Field()。

第 53 堂：資源（resources）跟工具不是同一回事——工具由 Claude 自己判斷要不
要呼叫（模型控制），資源由應用程式決定何時要（App 控制），類似 HTTP 的
GET。兩種資源：直接資源（固定 URI，列出全部）、範本化資源（URI 帶
{doc_id} 參數，查單一個）。

第 55 堂：prompts 是第三種東西——工具是模型控制、資源是應用程式控制，
prompts 是使用者控制：使用者主動選一個預寫好的模板（例如「把這份文件排版
成 Markdown」），模板把參數包成一句完整的指令再送給 Claude。回傳型別是
list[base.Message]，課程是用 base.UserMessage 包一句話。

警告（課程筆記提過要核對）：這支程式只在 mcp<2（裝的是 1.30.0）能跑。
mcp 2.x 把 FastMCP 整個改名成 MCPServer，import 路徑不一樣，pyproject.toml
已經釘住 mcp<2。另外課程筆記寫的 `from mcp.server.fastmcp import base`
在 1.30.0 這個版本行不通，實測後 base 其實在
`mcp.server.fastmcp.prompts` 底下。

用法：mcp dev mcp_server.py（51 堂的 inspector，單獨測這個檔案）
     或由 mcp_client.py 當子程序啟動（52 堂起，經由 uv run main.py）
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
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


@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add
    section titles if appropriate. Be sure to use the tools provided to you to
    read and edit the document. Make no changes to the content, only the
    formatting.
    """
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
