"""第 6 堂：Temperature。

生成三步：Tokenization -> Prediction（下一個 token 的機率）-> Sampling（依機率挑一個）。
temperature 調的是第三步的機率分佈：接近 0 幾乎總是挑機率最高的，接近 1 則分散。

同一個提示各跑三次，低溫與高溫並排看。
注意課程的提醒：temperature 不保證產生不同輸出，它只改變「不同」的機率。

警告：這堂課的 API 已經過時兩層。
1. SDK：anthropic 1.x 把 temperature 從 messages.create() 的簽名移除了，
   照課程寫會噴 TypeError，要用 extra_body 繞（見 chat_helpers.chat）。
2. 模型：4.6 以後的世代就算送進去也會回 400，只有 Haiku 4.5 這類舊模型還吃。

用法：uv run class_06_temperature.py
"""

from chat_helpers import add_user_message, chat

PROMPT = "Write a one-sentence opening line for a mystery novel."
RUNS = 3


def sample(temperature):
    print(f"\n[temperature={temperature}]")
    for i in range(RUNS):
        messages = []
        add_user_message(messages, PROMPT)
        print(f"  {i + 1}. {chat(messages, temperature=temperature)}")


sample(0.0)  # 事實性回應、程式碼、資料提取
sample(1.0)  # 腦力激盪、創意寫作

print("\n-> 低溫三句應該高度相似甚至一模一樣，高溫三句應該明顯分岔。")
print("-> 但低溫不等於「正確」，只等於「可預測」。")
