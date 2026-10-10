"""模块① 状态双模式：极速单 / 犒劳单。

真实环境里 `candidates` 来自麦当劳 MCP：
  query-meals（在售餐品）+ list-nutrition-foods（营养）+ calculate-price（价格）。
本模块只负责"读状态 → 决定节奏 → 加权选品"，与数据来源解耦，便于单测。
"""
from memory_store import load_profile

QUICK_KEYWORDS = [
    "赶稿", "累", "没空", "忙", "加班", "困", "对付", "随便",
    "快", "赶时间", "收工", "饿扁", "想睡", "困了",
]
TREAT_KEYWORDS = [
    "犒劳", "奖励", "周末", "小成就", "对自己好", "庆祝",
    "放松", "慢慢", "躺平", "值得", "今天要点好的", "享受",
]


def detect_mode(user_text):
    """返回 'quick' 或 'treat'。平局默认犒劳（一个人住，认真点）。"""
    t = user_text or ""
    q = sum(1 for k in QUICK_KEYWORDS if k in t)
    r = sum(1 for k in TREAT_KEYWORDS if k in t)
    if q > r:
        return "quick"
    if r > q:
        return "treat"
    return "treat"


def filter_by_prefs(candidates, prefs):
    """按忌口与口味偏好过滤候选。"""
    dislikes = set(prefs.get("dislikes", []))
    out = [c for c in candidates if not (set(c.get("tags", [])) & dislikes)]
    spice = prefs.get("spice")
    if spice == "mild":
        out = [c for c in out if "spicy" not in c.get("tags", [])]
    elif spice == "spicy":
        spicy_only = [c for c in out if "spicy" in c.get("tags", [])]
        out = spicy_only or out
    temp = prefs.get("temp")
    if temp == "hot":
        out = [c for c in out if "cold" not in c.get("tags", [])] or out
    elif temp == "cold":
        out = [c for c in out if "hot" not in c.get("tags", [])] or out
    return out


def score_item(item, mode, prefs):
    """双模式加权打分：极速单压快/省/经典，犒劳单压满足感/可坐食/小确幸。"""
    tags = set(item.get("tags", []))
    score = 0
    if mode == "quick":
        if "fast" in tags:
            score += 3
        if "classic" in tags:
            score += 2
        if "cheap" in tags:
            score += 2
    else:  # treat
        if "comfort" in tags:
            score += 3
        if "dessert" in tags:
            score += 2
        if "sit_down" in tags:
            score += 2
        if "premium" in tags:
            score += 1
    if item["name"] in prefs.get("favorites", []):
        score += 2
    return score


def pick(candidates, user_text=None, prefs=None, mode=None, top=1):
    """完整选品：读状态 → 过滤 → 加权 → 取 top。"""
    prefs = prefs or load_profile()["preferences"]
    mode = mode or detect_mode(user_text)
    cands = filter_by_prefs(candidates, prefs)
    ranked = sorted(
        cands, key=lambda c: score_item(c, mode, prefs), reverse=True
    )
    return ranked[:top], mode
