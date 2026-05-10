"""Stage 1 LearnerResearcher \u6700\u5c0f\u5355\u6d4b - \u9a8c\u8bc1\u964d\u7ea7\u8def\u5f84\u4e0e\u89c4\u5219\u8f93\u51fa\u5b8c\u6574\u6027"""
import unittest
from unittest.mock import patch

from app.services.learner_researcher import (
    LearnerResearcher,
    _avg_sentence_length,
    _derive_weakness_signals,
)


class TestLearnerResearcherRules(unittest.TestCase):
    def test_avg_sentence_length_basic(self):
        self.assertEqual(_avg_sentence_length(""), 0.0)
        # "I like it" (3 words) + "You too" (2 words) → avg 2.5
        self.assertEqual(_avg_sentence_length("I like it. You too."), 2.5)

    def test_weakness_signals_short_sentences(self):
        samples = [{"text": "I like it. Yes. No."}]
        signals = _derive_weakness_signals(samples)
        self.assertTrue(any(s.startswith("short_sentences") for s in signals))
        self.assertIn("lack_connectors", signals)

    def test_weakness_signals_empty(self):
        self.assertEqual(_derive_weakness_signals([]), [])


class TestLearnerResearcherAsync(unittest.IsolatedAsyncioTestCase):

    async def test_missing_questionnaire_returns_empty_profile(self):
        """questionnaire \u4e0d\u5b58\u5728 \u2192 \u964d\u7ea7\u7a7a\u6863\u6848\u4f46\u5b57\u6bb5\u9f50\u5168"""
        researcher = LearnerResearcher()
        with patch(
            "app.services.learner_researcher.get_questionnaire",
            return_value=None,
        ):
            profile = await researcher.research("nonexistent-id")

        self.assertIsInstance(profile, dict)
        for key in (
            "background", "language_samples", "weakness_signals",
            "goal_vector", "topic_signals", "source_stats", "generated_at",
        ):
            self.assertIn(key, profile, f"missing key: {key}")
        self.assertEqual(profile["language_samples"], [])
        self.assertEqual(profile["goal_vector"]["target_score"], "6.5")

    async def test_full_profile_with_materials_and_topics(self):
        """\u5168\u6750\u6599\u8def\u5f84: \u5c06\u6750\u6599\u8f6c\u5316\u4e3a language_samples"""
        researcher = LearnerResearcher()

        fake_q = {
            "mbti_type": "INTJ",
            "mbti_dimensions": {},
            "interests_tags": ["photography", "travel"],
            "interests_descriptions": [],
            "ielts_target_score": "7.0",
            "ielts_topic_types": ["P1", "P2"],
            "ielts_exam_date": "",
            "personal_background": {},
            "life_experiences": {},
        }
        fake_materials = [
            {"id": "m1", "filename": "demo.txt", "raw_content": "This is a simple text. Yes."}
        ]
        fake_topics = [
            {"id": "t1", "part": "P1", "title": "Hometown photography", "category": "Places"},
            {"id": "t2", "part": "P2", "title": "Food", "category": "Life"},
        ]

        with patch("app.services.learner_researcher.get_questionnaire", return_value=fake_q), \
             patch("app.services.learner_researcher.get_materials", return_value=fake_materials), \
             patch("app.services.learner_researcher.get_conversation_history", return_value=[]), \
             patch("app.services.learner_researcher.get_topics", return_value=fake_topics):
            profile = await researcher.research("qid", corpus_id="cid")

        self.assertEqual(profile["source_stats"]["materials"], 1)
        self.assertEqual(profile["goal_vector"]["target_score"], "7.0")
        # \u5174\u8da3 photography \u5339\u914d \u2192 \u81f3\u5c11\u547d\u4e2d Hometown photography
        match_titles = [m["title"] for m in profile["topic_signals"]["matches"]]
        self.assertTrue(any("photography" in t.lower() for t in match_titles))


if __name__ == "__main__":
    unittest.main()
