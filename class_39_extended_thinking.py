"""第 39 堂：擴展思考（extended thinking）。

開關條件不是「這題很難」，是「提示已經優化過、準確性還不夠」才開。
開了之後 chat() 會把 thinking 區塊印出來，再回傳最終答案文字。

用法：uv run class_39_extended_thinking.py
"""

from chat_helpers import add_user_message, chat

if __name__ == "__main__":
    messages = []
    add_user_message(
        messages,
        "一個房間裡有 3 盞燈。每盞燈各連一個開關，開關在走廊、看不到房間裡的狀態，"
        "只能進房間一次。怎麼用最少次數的開關操作，確認哪個開關對應哪盞燈？",
    )

    answer = chat(messages, thinking=True, thinking_budget=2048, max_tokens=1000)
    print(f"--- 最終答案 ---\n{answer}")
