"""麦门一人食补给站 · 端到端演示（Demo）

真实环境中，candidates 来自麦当劳 MCP 工具：
  query-meals（在售餐品）+ list-nutrition-foods（营养）+ calculate-price（价格）
  + available-coupons（券）+ create-order（下单，需用户确认）。

本 demo 用 mock 餐品数据演示 ① 双模式 ② 周菜单 ③ 节日 三大模块，
可直接 `python src/demo.py "想犒劳自己"` 运行，无需联网、无需凭证。
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from memory_store import load_profile, this_week_history
from recommend import detect_mode, pick, score_item
from weekly_plan import generate_weekly_plan
from festival import detect_festival, detect_birthday, festival_plan

# ---- Mock 餐品（真实环境由 MCP query-meals 返回）----
MOCK_MEALS = [
    {"name": "巨无霸套餐", "tags": ["classic", "comfort", "fast"]},
    {"name": "麦辣鸡腿堡套餐", "tags": ["spicy", "fast", "comfort"]},
    {"name": "板烧鸡腿堡套餐", "tags": ["classic", "sit_down"]},
    {"name": "吉士汉堡", "tags": ["cheap", "fast", "classic"]},
    {"name": "麦香鱼套餐", "tags": ["classic", "comfort"]},
    {"name": "苹果派", "tags": ["dessert"]},
    {"name": "圆筒冰淇淋", "tags": ["dessert", "cheap"]},
    {"name": "热可可", "tags": ["hot", "comfort", "dessert"]},
    {"name": "薯条(大)", "tags": ["classic", "comfort"]},
]


def main():
    argv = sys.argv[1] if len(sys.argv) > 1 else "赶稿到深夜，随便来点快的"
    profile = load_profile()  # 真实环境：首次会 init_profile 收集忌口
    prefs = profile["preferences"]

    # ① 双模式
    mode = detect_mode(argv)
    picked, _ = pick(MOCK_MEALS, user_text=argv, prefs=prefs, top=1)
    print("[① 状态双模式] 输入：", argv)
    print("    判定：", "极速单" if mode == "quick" else "犒劳单")
    if picked:
        print("    推荐：", picked[0]["name"],
              "（评分", score_item(picked[0], mode, prefs), "）")

    # ② 周菜单
    hist = this_week_history(profile)
    print("\n[② 周中不重样] 本周已点：", hist or "无")
    plan = generate_weekly_plan(
        MOCK_MEALS, week_history=hist, prefs=prefs, seed=42
    )
    print("    " + " · ".join(f"{d['day']}{d['item']}" for d in plan))

    # ③ 节日
    fest = detect_festival() or detect_birthday(date.today(), profile.get("birthday"))
    print("\n[③ 一个人的节日不空桌]")
    if fest:
        fp = festival_plan(MOCK_MEALS, fest, prefs)
        print("    今天：", fp["festival"])
        print("    套餐：", " + ".join(fp["items"]))
        print("    文案：", fp["copy"])
    else:
        print("    今天不是特殊日子，平平淡淡也挺好。")


if __name__ == "__main__":
    main()
