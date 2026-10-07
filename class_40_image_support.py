"""第 40 堂：圖片支援。

這堂真正的重點不是「怎麼傳圖片」（跟文字一樣呼叫 chat()，只是多一個 image 區塊），
是「圖片要用跟文字一樣的提示工程」。兩次請求刻意獨立送出，直接比較：
簡單提問 vs. 官方的「數彈珠方法論」（要求分步驟數、再用不同方法驗算一次）。

測試圖 marbles.png：使用者提供的彈珠照片，762x368，遠低於課程列的
5MB／8000px（單張）／2000px（多張）硬限制。

用法：uv run class_40_image_support.py
"""

import base64

from chat_helpers import add_user_message, chat

with open("marbles.png", "rb") as f:
    image_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

image_block = {
    "type": "image",
    "source": {"type": "base64", "media_type": "image/png", "data": image_bytes},
}

NAIVE_PROMPT = "這張圖片中有多少顆彈珠？"

METHODOLOGY_PROMPT = """Analyze this image of marbles and determine the exact count using this methodology:
1. Begin by identifying each unique marble one at a time. Assign each a number as you identify it.
2. Verify your result by counting with a different method. Start from the bottom-left corner and work row by row, from left to right.

What is the exact, verified number of marbles in this image?"""


if __name__ == "__main__":
    # 兩個彼此獨立的請求，都帶齊參數、不依賴對方的結果，方便直接比較結果。
    naive_messages = []
    add_user_message(naive_messages, [image_block, {"type": "text", "text": NAIVE_PROMPT}])
    print("--- 簡單提問 ---")
    print(chat(naive_messages))

    methodology_messages = []
    add_user_message(methodology_messages, [image_block, {"type": "text", "text": METHODOLOGY_PROMPT}])
    print("\n--- 方法論提問（分步驟＋驗算）---")
    print(chat(methodology_messages))
