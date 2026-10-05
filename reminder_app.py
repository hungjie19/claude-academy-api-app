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
