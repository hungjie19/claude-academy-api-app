"""CLI 聊天機器人（第 49-56 堂 MCP 專案的主程式）。

這堂（49）還沒接 MCP 伺服器／客戶端，先把最簡單的聊天迴圈跑起來，
當作後面每一層（工具、resources、prompts）疊上去前的驗證基準。

用法：uv run main.py
"""

from chat_helpers import add_user_message, add_assistant_message, chat


def main():
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("quit", "exit"):
            break
        add_user_message(messages, user_input)
        response = chat(messages)
        add_assistant_message(messages, response)
        print(f"Claude: {response}")


if __name__ == "__main__":
    main()
