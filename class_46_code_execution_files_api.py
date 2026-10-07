"""第 46 堂：Code execution 工具 + Files API。

兩個功能合起來才有意思：

- Files API：檔案事先用獨立呼叫上傳一次，拿到 file_id，之後用 ID 參照，不必每次都塞 base64。
  適合同一檔案要被多次參照，或檔案較大時。
- Code execution：伺服器端工具，不用自己提供實作，Claude 在隔離的 Docker 容器裡寫並執行
  Python。容器沒有網路，所以 Files API 就成了資料進出容器的唯一管道：
  上傳 CSV → container_upload 區塊把它放進容器 → Claude 跑程式分析、畫圖 →
  產出的檔案一樣用 file_id 下載回來。

跟前面幾堂一樣直接呼叫 client 而不是 chat_helpers.chat()：要讀 server_tool_use 與
code_execution_tool_result 這些區塊的原始結構，chat() 只回傳最終文字會把它們全部丟掉。

reef_sites.csv：延續第 41、42 堂用的虛構珊瑚白化測試資料（12 個站點），這次換成
CSV 格式，讓 Claude 能真的拿去做統計與畫圖，不是讀 PDF 摘要文字。

用法：uv run class_46_code_execution_files_api.py
"""

import os
from pathlib import Path

from chat_helpers import client, model

OUTPUT_DIR = Path("class_46_outputs")


def upload_csv():
    uploaded = client.files.upload(file=Path("reef_sites.csv"))
    print(f"已上傳 file_id={uploaded.id}（{uploaded.size_bytes} bytes）")
    return uploaded


def run_analysis(file_id):
    return client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Run an analysis on this reef site data to determine what site "
                    "characteristic is most strongly linked to low recovery_pct. "
                    "Your final output should include at least one plot summarizing "
                    "your findings."
                )},
                {"type": "container_upload", "file_id": file_id},
            ],
        }],
        tools=[{"type": "code_execution_20250522", "name": "code_execution"}],
    )


def download_outputs(message):
    OUTPUT_DIR.mkdir(exist_ok=True)
    saved = []
    for block in message.content:
        if block.type != "code_execution_tool_result":
            continue
        result = block.content
        if result.type != "code_execution_result":
            print(f"    工具錯誤：{result.error_code}")
            continue
        for output in result.content:
            metadata = client.files.retrieve_metadata(output.file_id)
            # basename 擋路徑跳脫；檔名來自模型執行結果，不完全信任
            safe_name = os.path.basename(metadata.filename)
            path = OUTPUT_DIR / safe_name
            client.files.download(output.file_id).write_to_file(path)
            saved.append(path)
    return saved


if __name__ == "__main__":
    uploaded = upload_csv()
    message = run_analysis(uploaded.id)

    for i, block in enumerate(message.content):
        if block.type == "text":
            print(f"--- 區塊 {i}：text ---\n{block.text}")
        elif block.type == "server_tool_use":
            print(f"--- 區塊 {i}：server_tool_use（{block.name}）---\n{block.input.get('code', block.input)}")
        elif block.type == "code_execution_tool_result":
            result = block.content
            if result.type == "code_execution_result":
                print(f"--- 區塊 {i}：code_execution_tool_result（return_code={result.return_code}）---")
                print(f"stdout: {result.stdout}")
                if result.stderr:
                    print(f"stderr: {result.stderr}")
            else:
                print(f"--- 區塊 {i}：code_execution_tool_result（錯誤：{result.error_code}）---")

    saved_paths = download_outputs(message)
    for path in saved_paths:
        print(f"已下載產出檔案：{path}")

    client.files.delete(uploaded.id)
