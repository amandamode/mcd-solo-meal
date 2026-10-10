"""双模式 / 周菜单 / 节日 三个创意模块的单元测试。"""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from recommend import detect_mode, filter_by_prefs, pick, score_item
from weekly_plan import generate_weekly_plan
from festival import detect_festival, detect_birthday, festival_plan

MEALS = [
    {"name": "巨无霸套餐", "tags": ["classic", "comfort", "fast"]},
    {"name": "麦辣鸡腿堡套餐", "tags": ["spicy", "fast", "comfort"]},
    {"name": "板烧鸡腿堡套餐", "tags": ["classic", "sit_down"]},
    {"name": "吉士汉堡", "tags": ["cheap", "fast", "classic"]},
    {"name": "麦香鱼套餐", "tags": ["classic", "comfort"]},
    {"name": "苹果派", "tags": ["dessert"]},
    {"name": "圆筒冰淇淋", "tags": ["dessert", "cheap"]},
    {"name": "热可可", "tags": ["hot", "comfort", "dessert"]},
]


class TestRecommend(unittest.TestCase):
    def test_detect_mode_quick(self):
        self.assertEqual(detect_mode("赶稿到深夜随便来点快的"), "quick")
        self.assertEqual(detect_mode("累瘫了没空"), "quick")

    def test_detect_mode_treat(self):
        self.assertEqual(detect_mode("想犒劳自己"), "treat")
        self.assertEqual(detect_mode("周末慢慢吃"), "treat")

    def test_detect_mode_default_treat(self):
        # 平局默认犒劳
        self.assertEqual(detect_mode("今天吃啥"), "treat")

    def test_filter_by_prefs_dislikes(self):
        prefs = {"dislikes": ["spicy"], "spice": None, "temp": None,
                 "favorites": []}
        out = filter_by_prefs(MEALS, prefs)
        names = [c["name"] for c in out]
        self.assertNotIn("麦辣鸡腿堡套餐", names)

    def test_filter_by_prefs_mild(self):
        prefs = {"dislikes": [], "spice": "mild", "temp": None, "favorites": []}
        out = filter_by_prefs(MEALS, prefs)
        for c in out:
            self.assertNotIn("spicy", c["tags"])

    def test_score_favors_quick_classic(self):
        prefs = {"dislikes": [], "spice": None, "temp": None, "favorites": []}
        classic = next(c for c in MEALS if c["name"] == "巨无霸套餐")
        weird = next(c for c in MEALS if c["name"] == "麦香鱼套餐")
        self.assertGreater(score_item(classic, "quick", prefs),
                           score_item(weird, "quick", prefs))

    def test_pick_returns_top(self):
        prefs = {"dislikes": [], "spice": None, "temp": None, "favorites": []}
        items, mode = pick(MEALS, user_text="想犒劳自己", prefs=prefs, top=1)
        self.assertEqual(len(items), 1)
        self.assertEqual(mode, "treat")


class TestWeeklyPlan(unittest.TestCase):
    def test_plan_length_and_no_dup(self):
        plan = generate_weekly_plan(MEALS, week_history=[], prefs={}, seed=1)
        self.assertEqual(len(plan), 7)
        names = [d["item"] for d in plan]
        self.assertEqual(len(set(names)), len(names))

    def test_plan_avoids_week_history(self):
        plan = generate_weekly_plan(
            MEALS, week_history=["巨无霸套餐"], prefs={}, seed=7
        )
        names = [d["item"] for d in plan]
        self.assertNotIn("巨无霸套餐", names)

    def test_plan_reproducible_with_seed(self):
        a = generate_weekly_plan(MEALS, week_history=[], prefs={}, seed=42)
        b = generate_weekly_plan(MEALS, week_history=[], prefs={}, seed=42)
        self.assertEqual([d["item"] for d in a], [d["item"] for d in b])


class TestFestival(unittest.TestCase):
    def test_detect_known_festival(self):
        fest = detect_festival(date(2026, 2, 14))
        self.assertIsNotNone(fest)
        self.assertEqual(fest["name"], "情人节")

    def test_detect_no_festival(self):
        self.assertIsNone(detect_festival(date(2026, 3, 3)))

    def test_detect_birthday(self):
        b = detect_birthday(date(2026, 5, 20), birthday="05-20")
        self.assertIsNotNone(b)
        self.assertEqual(b["name"], "生日")

    def test_festival_plan_has_dessert_when_available(self):
        fest = detect_festival(date(2026, 2, 14))
        fp = festival_plan(MEALS, fest)
        self.assertIn("苹果派", fp["items"])


if __name__ == "__main__":
    unittest.main()
