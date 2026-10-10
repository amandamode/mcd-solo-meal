"""记忆层：本地沉淀用户偏好 / 忌口 / 常点 / 本周已点。

这是「麦门一人食补给站」"记得你"搭子感的核心。
真实环境中由 WorkBuddy 运行时读写；本模块为纯标准库实现，可直接单测。
"""
import json
import os
from datetime import date, datetime

DEFAULT_PATH = os.path.expanduser(
    "~/.workbuddy/skills/mcd-solo-meal/user_profile.json"
)


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def default_profile():
    return {
        "name": None,
        "preferences": {
            "dislikes": [],          # 忌口 / 不爱吃（与餐品 tags 对应）
            "favorites": [],         # 常点 / 爱吃
            "spice": None,           # "spicy" / "mild"
            "temp": None,            # "hot" / "cold"
            "budget_per_meal": None, # 单餐预算（元），None 表示不限
        },
        "history": [],               # [{date, items:[name], mode}]
        "birthday": None,            # "MM-DD"
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def load_profile(path=DEFAULT_PATH):
    if not os.path.exists(path):
        return default_profile()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile, path=DEFAULT_PATH):
    profile["updated_at"] = now_iso()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    return profile


def init_profile(path=DEFAULT_PATH, dislikes=None, favorites=None,
                 spice=None, temp=None, budget=None, birthday=None):
    """首次对话收集并落盘偏好。"""
    p = default_profile()
    p["preferences"].update({
        "dislikes": dislikes or [],
        "favorites": favorites or [],
        "spice": spice,
        "temp": temp,
        "budget_per_meal": budget,
    })
    p["birthday"] = birthday
    return save_profile(p, path)


def update_preferences(profile, path=DEFAULT_PATH, **kwargs):
    profile["preferences"].update(
        {k: v for k, v in kwargs.items() if v is not None}
    )
    return save_profile(profile, path)


def record_order(profile, items, mode, date_str=None, path=DEFAULT_PATH):
    """记录一次下单，用于本周去重与"记得你"。"""
    date_str = date_str or date.today().isoformat()
    profile.setdefault("history", []).append({
        "date": date_str,
        "items": list(items),
        "mode": mode,
    })
    if len(profile["history"]) > 60:
        profile["history"] = profile["history"][-60:]
    return save_profile(profile, path)


def this_week_history(profile, today=None):
    """返回本周已点过的餐品名集合（用于周菜单去重）。"""
    today = today or date.today()
    iso = today.isocalendar()[:2]  # (year, week)
    items = []
    for h in profile.get("history", []):
        try:
            d = date.fromisoformat(h["date"])
        except ValueError:
            continue
        if d.isocalendar()[:2] == iso:
            items.extend(h.get("items", []))
    return items
