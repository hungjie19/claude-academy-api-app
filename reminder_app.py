"""Day 21 第 22 堂起：設定提醒專案（連續專案，每堂原地修改這支檔案）。

目標：使用者說「下週四提醒我看醫生」，Claude 能回答。
Claude 缺三樣東西：目前時間、日期加減、設定提醒。
每個缺口對應一個工具函式，函式本身就是普通的 Python。

第 22 堂的最佳實務：
- 函式名與參數名要清楚表明用途
- 輸入不合法就 raise，不要默默回傳錯誤值
- 錯誤訊息要寫給 Claude 看：Claude 看得到錯誤，可能會用修正後的參數重試
"""

from datetime import datetime, timedelta

UNITS = {
    "minutes": "minutes",
    "hours": "hours",
    "days": "days",
    "weeks": "weeks",
}


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    """取得目前的日期時間。Claude 不知道確切時間，需要的時候呼叫這個。"""
    if not date_format:
        raise ValueError("date_format 不能是空字串，例如 '%Y-%m-%d %H:%M:%S'")
    return datetime.now().strftime(date_format)


def add_duration_to_datetime(datetime_str, duration, unit):
    """把一段時間加到一個日期時間上，回傳 '%Y-%m-%d %H:%M:%S'。

    Claude 做「展望未來很多天」的日期加法不可靠，所以交給程式算。
    """
    if unit not in UNITS:
        raise ValueError(
            f"unit 必須是 {list(UNITS)} 其中之一，收到 {unit!r}。"
        )
    if not isinstance(duration, (int, float)) or duration < 0:
        raise ValueError(f"duration 必須是非負數字，收到 {duration!r}。")
    try:
        start = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"datetime_str 格式錯誤，需要 'YYYY-MM-DD HH:MM:SS'，收到 {datetime_str!r}。"
        ) from e
    result = start + timedelta(**{UNITS[unit]: duration})
    return result.strftime("%Y-%m-%d %H:%M:%S")


# 第 23 堂：工具結構（schema）。
# Claude 看不到 Python 函式，只看得到這份描述：名稱、用途、參數格式。
# 名稱與參數名要跟上面的函式一致，enum 要跟 UNITS 的 key 一致。
# description 是寫給 Claude 讀的：它決定 Claude 什麼時候該呼叫這個工具。

get_current_datetime_schema = {
    "name": "get_current_datetime",
    "description": (
        "取得目前的日期與時間。當使用者提到「今天」「明天」「下週」等相對時間，"
        "或你需要知道現在幾點時，先呼叫這個工具，不要自己猜。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "Python strftime 格式，例如 '%Y-%m-%d %H:%M:%S'。預設即可。",
            }
        },
        "required": [],
    },
}

add_duration_to_datetime_schema = {
    "name": "add_duration_to_datetime",
    "description": (
        "把一段時間加到某個日期時間上，回傳結果。計算未來或過去的日期時，"
        "必須用這個工具，不要自己做日期加減。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "起始日期時間，格式 'YYYY-MM-DD HH:MM:SS'。",
            },
            "duration": {
                "type": "number",
                "description": "要加的時間長度，非負數。",
            },
            "unit": {
                "type": "string",
                "enum": list(UNITS),
                "description": "時間單位。",
            },
        },
        "required": ["datetime_str", "duration", "unit"],
    },
}

TOOLS = [get_current_datetime_schema, add_duration_to_datetime_schema]


# 第 24 堂：處理訊息區塊。
# 啟用工具就是在 API 呼叫裡加 tools。Claude 決定用工具時，
# 回應的 content 不再是一段文字，而是一串區塊：text 與 tool_use。
from chat_helpers import add_user_message, client, model  # noqa: E402


def send_with_tools(messages):
    """把歷史和工具清單送出去，回傳完整的 response（不只取文字）。"""
    return client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
        tools=TOOLS,
    )


def print_blocks(response):
    """逐一看區塊。tool_use 區塊帶 id（追蹤用）、name、input（參數 dict）。"""
    for block in response.content:
        if block.type == "text":
            print(f"[text] {block.text}")
        elif block.type == "tool_use":
            print(f"[tool_use] name={block.name} id={block.id} input={block.input}")



# 第 25 堂：傳送工具結果。
# 名稱對應到實際函式。Claude 送來的 name 必須在這張表裡找得到。
TOOL_FUNCTIONS = {
    "get_current_datetime": get_current_datetime,
    "add_duration_to_datetime": add_duration_to_datetime,
}


def build_tool_results(response):
    """執行回應裡所有 tool_use，產生對應的 tool_result 區塊。

    每個結果都要帶原本的 tool_use_id，Claude 靠它把結果對回請求。
    函式丟錯時不要讓程式中斷：把錯誤訊息當成 is_error 結果送回，
    Claude 看得到錯誤，可能會改參數重試（第 22 堂的設計）。
    """
    results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        try:
            output = TOOL_FUNCTIONS[block.name](**block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(output),
                "is_error": False,
            })
        except Exception as e:
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(e),
                "is_error": True,
            })
    return results

if __name__ == "__main__":
    messages = []
    add_user_message(messages, "我想知道現在幾點，還有 3 天後是幾號？")

    response = send_with_tools(messages)
    messages.append({"role": "assistant", "content": response.content})
    print_blocks(response)

    # 工具結果放在 user 訊息裡
    messages.append({"role": "user", "content": build_tool_results(response)})

    # 送出工具結果後，後續請求仍要帶 TOOLS（Claude 需要 schema 理解歷史）
    response = send_with_tools(messages)
    messages.append({"role": "assistant", "content": response.content})
    print_blocks(response)

