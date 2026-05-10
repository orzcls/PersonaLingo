"""T5 SkillExporter.export_runnable_skill \u6700\u5c0f\u5355\u6d4b - \u9a8c\u8bc1 4 \u4efd\u4ea7\u7269\u9f50\u5168"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock

from app.services.skill_exporter import SkillExporter


FAKE_CORPUS = {
    "id": "test-corpus-001",
    "questionnaire_id": "q-001",
    "status": "completed",
    "persona": {"mbti_type": "INTJ", "communication_style": "concise"},
    "anchors": [{"id": "a1", "label": "Photography", "keywords": ["camera"]}],
    "bridges": [{"topic_title": "Hometown", "anchor_id": "a1", "bridge_sentence": "..."}],
    "vocabulary": [{"basic_word": "good", "upgrade": "exceptional"}],
    "patterns": [{"name": "contrast", "formula": "A but B"}],
    "band_strategy": {"target_score": "6.5"},
    "user_style": {"avg_sentence_length": 10.5, "frequent_connectors": ["however"]},
    "learner_profile": {
        "background": {"mbti_type": "INTJ"},
        "goal_vector": {"target_score": "6.5"},
    },
    "capability_framework": {
        "dimensions": {"ability": [{"name": "lexical_range"}], "scenario": [], "goal": []},
        "source": "rule_fallback",
    },
}

FAKE_Q = {"mbti_type": "INTJ", "interests_tags": ["photography"], "ielts_target_score": "6.5"}


class TestSkillExporterRunnable(unittest.IsolatedAsyncioTestCase):
    async def test_export_runnable_skill_produces_four_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            out_root = Path(td)
            exporter = SkillExporter()
            with patch("app.services.skill_exporter.get_corpus",
                       new=AsyncMock(return_value=FAKE_CORPUS)), \
                 patch("app.services.skill_exporter.get_questionnaire",
                       new=AsyncMock(return_value=FAKE_Q)):
                target = await exporter.export_runnable_skill(
                    "test-corpus-001", out_root=out_root
                )

            # \u9a8c\u8bc1 4 \u4efd\u4ea7\u7269
            self.assertTrue(target.is_dir())
            self.assertTrue((target / "Skill.md").is_file())
            self.assertTrue((target / "corpus.json").is_file())
            self.assertTrue((target / "runtime_protocol.md").is_file())
            self.assertTrue((target / "prompts" / "README.md").is_file())

            # corpus.json \u53ef\u53cd\u5e8f\u5217\u5316
            payload = json.loads((target / "corpus.json").read_text(encoding="utf-8"))
            self.assertIn("anchors", payload)
            self.assertIn("learner_profile", payload)
            self.assertIn("capability_framework", payload)
            self.assertEqual(payload["skill_manifest"]["pipeline"], "three_stage_distill")
            self.assertEqual(
                payload["skill_manifest"]["stages"][:2],
                ["research", "framework"],
            )

            # Skill.md \u5305\u542b 7 \u6b65\u6807\u8bc6
            md_text = (target / "Skill.md").read_text(encoding="utf-8")
            self.assertIn("7 \u6b65", md_text)
            self.assertIn("Research", md_text)
            self.assertIn("Framework", md_text)

    async def test_export_runnable_skill_raises_on_missing_corpus(self):
        exporter = SkillExporter()
        with patch("app.services.skill_exporter.get_corpus",
                   new=AsyncMock(return_value=None)):
            with self.assertRaises(ValueError):
                await exporter.export_runnable_skill("no-such-id")


if __name__ == "__main__":
    unittest.main()
