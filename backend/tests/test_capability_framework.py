"""Stage 2 CapabilityFramework \u6700\u5c0f\u5355\u6d4b - \u9a8c\u8bc1\u89c4\u5219\u5151\u5e95\u4e0e JSON \u89e3\u6790"""
import unittest
from unittest.mock import patch, AsyncMock

from app.services.capability_framework import CapabilityFramework


class TestCapabilityFrameworkFallback(unittest.TestCase):
    def test_fallback_on_none_profile(self):
        fb = CapabilityFramework()._fallback(None)
        self._assert_non_empty_dimensions(fb)
        self.assertEqual(fb["source"], "rule_fallback")

    def test_fallback_respects_goal_vector(self):
        profile = {
            "goal_vector": {
                "target_score": "7.0",
                "priority_parts": ["P2", "P3"],
                "focus_topics": ["travel", "food"],
                "exam_date": "2026-08-15",
            },
            "weakness_signals": ["lack_connectors", "short_sentences(avg=5.0)"],
        }
        fb = CapabilityFramework()._fallback(profile)
        self._assert_non_empty_dimensions(fb)
        self.assertEqual(
            fb["dimensions"]["goal"][0],
            {"key": "target_score", "value": "7.0"},
        )
        scenario_parts = [s["part"] for s in fb["dimensions"]["scenario"]]
        self.assertIn("P2", scenario_parts)
        self.assertGreaterEqual(len(fb["pain_points"]), 2)

    @staticmethod
    def _assert_non_empty_dimensions(fb):
        for dim in ("ability", "scenario", "goal"):
            assert fb["dimensions"][dim], f"dim {dim} empty"

    def test_safe_json_strip_codefence(self):
        t = """```json
        {"dimensions": {"ability": [{"name": "x"}], "scenario": [], "goal": []}}
        ```"""
        data = CapabilityFramework._safe_json(t)
        self.assertIsInstance(data, dict)
        self.assertIn("dimensions", data)

    def test_safe_json_invalid(self):
        self.assertIsNone(CapabilityFramework._safe_json(""))
        self.assertIsNone(CapabilityFramework._safe_json("no json at all"))


class TestCapabilityFrameworkAsync(unittest.IsolatedAsyncioTestCase):
    async def test_distill_llm_failure_falls_back(self):
        cf = CapabilityFramework()
        with patch.object(cf, "_llm_distill", new=AsyncMock(side_effect=RuntimeError("no key"))):
            result = await cf.distill({"goal_vector": {"target_score": "6.5"}})
        self.assertEqual(result["source"], "rule_fallback")
        self.assertTrue(result["dimensions"]["ability"])

    async def test_distill_non_dict_profile(self):
        result = await CapabilityFramework().distill("not a dict")
        self.assertEqual(result["source"], "rule_fallback")


if __name__ == "__main__":
    unittest.main()
