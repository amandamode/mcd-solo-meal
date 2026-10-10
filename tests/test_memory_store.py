"""记忆层单元测试。"""
import json
import os
import tempfile
import unittest

from memory_store import (
    default_profile,
    init_profile,
    load_profile,
    record_order,
    this_week_history,
    update_preferences,
)


class TestMemoryStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "user_profile.json")

    def test_default_profile_shape(self):
        p = default_profile()
        self.assertIsNone(p["preferences"]["spice"])
        self.assertEqual(p["history"], [])
        self.assertIn("created_at", p)

    def test_init_and_load_roundtrip(self):
        init_profile(self.path, dislikes=["辣"], favorites=["巨无霸套餐"],
                     spice="mild", budget=35)
        p = load_profile(self.path)
        self.assertEqual(p["preferences"]["dislikes"], ["辣"])
        self.assertEqual(p["preferences"]["spice"], "mild")
        self.assertEqual(p["preferences"]["budget_per_meal"], 35)

    def test_update_preferences_ignores_none(self):
        init_profile(self.path, spice="mild")
        p = load_profile(self.path)
        update_preferences(p, path=self.path, spice=None, temp="hot")
        p2 = load_profile(self.path)
        # spice 不应被 None 覆盖
        self.assertEqual(p2["preferences"]["spice"], "mild")
        self.assertEqual(p2["preferences"]["temp"], "hot")

    def test_record_and_week_history(self):
        init_profile(self.path)
        p = load_profile(self.path)
        record_order(p, ["巨无霸套餐"], "quick", date_str="2026-10-10",
                     path=self.path)
        record_order(p, ["麦香鱼套餐"], "treat", date_str="2026-10-11",
                     path=self.path)
        p = load_profile(self.path)
        self.assertEqual(len(p["history"]), 2)
        # 2026-10-10(周六) 与 2026-10-11(周日) 同属 ISO 第 41 周
        wk = this_week_history(p, today=__import__("datetime").date(2026, 10, 11))
        self.assertIn("巨无霸套餐", wk)
        self.assertIn("麦香鱼套餐", wk)

    def test_history_capped(self):
        init_profile(self.path)
        p = load_profile(self.path)
        for i in range(70):
            record_order(p, [f"item{i}"], "quick", path=self.path)
        p = load_profile(self.path)
        self.assertLessEqual(len(p["history"]), 60)


if __name__ == "__main__":
    unittest.main()
