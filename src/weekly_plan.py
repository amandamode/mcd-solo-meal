"""模块② 周中不重样·一人食周菜单。

基于记忆层本周已点 + 在售餐品，生成周一至周日不重样的 7 份方案。
真实环境里 `sold_items` 来自 query-meals，营养/预算平衡可再接入
list-nutrition-foods 与 calculate-price（此处保留钩子，不阻塞）。
"""
import random

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def generate_weekly_plan(sold_items, week_history=None, prefs=None,
                         days=7, seed=None, constraints=None):
    """返回 [{day, item, tags}] 列表，尽量不重样。

    - week_history: 本周已点餐品名集合，优先避开
    - seed: 固定随机种子，便于可复现/测试
    - constraints: 预留（如每日预算上限、营养上限），当前仅透传不参与
    """
    if seed is not None:
        random.seed(seed)
    week_history = set(week_history or [])
    prefs = prefs or {}

    # 优先从未点过的里挑，不够再放宽
    fresh = [c for c in sold_items if c["name"] not in week_history]
    pool = fresh if len(fresh) >= days else sold_items[:]

    chosen, seen = [], set()
    shuffled = pool[:]
    random.shuffle(shuffled)
    for c in shuffled:
        if c["name"] not in seen:
            chosen.append(c)
            seen.add(c["name"])
        if len(chosen) >= days:
            break

    # 若仍不足 days（餐品太少），循环补足
    idx = 0
    while len(chosen) < days and sold_items:
        c = sold_items[idx % len(sold_items)]
        chosen.append(c)
        idx += 1

    plan = []
    for i, c in enumerate(chosen[:days]):
        plan.append({
            "day": WEEKDAYS[i],
            "item": c["name"],
            "tags": c.get("tags", []),
        })
    return plan
