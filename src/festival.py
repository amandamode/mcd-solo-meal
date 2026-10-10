"""模块③ 一个人的节日不空桌。

检测当前/临近节日（中西方常见节日 + 用户生日），给一份"像样"的
节日套餐 + 一句不煽情、不卖惨的陪伴文案。情感真，是 176 个参赛里
几乎无人占的空白。
"""
from datetime import date

# 公历近似（农历节日用近似公历占位；如需精确可接入农历库，不影响主流程）
FESTIVALS = {
    "02-14": ("情人节", "一个人的情人节，也可以是一份小小的甜。桌子小，心意不空。"),
    "12-31": ("跨年", "这一年不管好坏，最后一顿饭先给自己安排上。"),
    "01-01": ("元旦", "新的一年，从好好吃一顿开始，不赶别人的节奏。"),
    "01-29": ("除夕", "一个人过的年，也得有年味。这桌不大，但坐的是你自己。"),
    "08-15": ("中秋", "月亮是大家的，月饼可以是一个人的。记得抬头看看。"),
}


def detect_festival(today=None):
    today = today or date.today()
    key = today.strftime("%m-%d")
    if key in FESTIVALS:
        name, copy = FESTIVALS[key]
        return {"key": key, "name": name, "copy": copy}
    return None


def detect_birthday(today=None, birthday=None):
    if not birthday:
        return None
    today = today or date.today()
    if today.strftime("%m-%d") == birthday:
        return {
            "key": birthday,
            "name": "生日",
            "copy": "今年这顿，是给自己过的。许愿的时候，别忘了谢谢还撑着的自己。",
        }
    return None


def festival_plan(sold_items, festival, prefs=None):
    """组合一份"像样"的节日套餐：主餐优先 comfort，附一份仪式感甜品。"""
    prefs = prefs or {}
    comfort = [c for c in sold_items if "comfort" in c.get("tags", [])]
    main_pool = comfort or sold_items
    main = main_pool[0]
    dessert = next(
        (c for c in sold_items if "dessert" in c.get("tags", [])), None
    )
    items = [main["name"]]
    if dessert:
        items.append(dessert["name"])
    return {
        "festival": festival["name"],
        "items": items,
        "copy": festival["copy"],
    }
