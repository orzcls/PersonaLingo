"""P2 distill router 单测 — 覆盖 /runnable/preview 和 /runnable/download 的关键契约

用 FastAPI TestClient + mock get_corpus / SkillExporter.export_runnable_skill
    → 避免依赖真实 DB 和真实语料
"""
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import distill


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(distill.router, prefix="/api/distill")
    return app


def _write_fake_skill_dir(root: Path) -> Path:
    """在 root 下造一个最小化 runnable skill 目录"""
    target = root / "fake_corpus"
    target.mkdir(parents=True, exist_ok=True)
    (target / "Skill.md").write_text(
        "# PersonaLingo Skill - INTJ\n\n"
        "## Overview\n测试语料 skill\n\n"
        "```python\nprint('hello')\n```\n\n"
        "## 详情\n普通段落\n",
        encoding="utf-8",
    )
    (target / "corpus.json").write_text('{"id": "fake"}', encoding="utf-8")
    (target / "runtime_protocol.md").write_text("protocol", encoding="utf-8")
    prompts = target / "prompts"
    prompts.mkdir(exist_ok=True)
    (prompts / "README.md").write_text("readme", encoding="utf-8")
    return target


class TestDistillRouterP2(unittest.IsolatedAsyncioTestCase):
    """P2 新增/改造端点契约测试"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_root = Path(self._tmp.name)
        self.fake_skill_dir = _write_fake_skill_dir(self.tmp_root)
        self.app = _make_app()

    def tearDown(self):
        self._tmp.cleanup()

    def _start_default_patches(self):
        """在单个测试内启动 patch 并登记到 addCleanup，避免泄露到其他测试"""
        patches = [
            patch(
                "app.routers.distill.get_corpus",
                new=AsyncMock(return_value={"id": "fake_corpus"}),
            ),
            patch.object(
                distill.SkillExporter,
                "export_runnable_skill",
                new=AsyncMock(return_value=self.fake_skill_dir),
            ),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    # ---------- P2-3: preview ----------
    def test_preview_markdown_returns_text_markdown(self):
        self._start_default_patches()
        with TestClient(self.app) as client:
            r = client.get(
                "/api/distill/skill/fake_corpus/runnable/preview",
                params={"format": "markdown"},
            )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers["content-type"].startswith("text/markdown"))
        self.assertIn("# PersonaLingo Skill", r.text)

    def test_preview_html_renders_h1_and_code(self):
        self._start_default_patches()
        with TestClient(self.app) as client:
            r = client.get(
                "/api/distill/skill/fake_corpus/runnable/preview",
                params={"format": "html"},
            )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers["content-type"].startswith("text/html"))
        self.assertIn("<!doctype html>", r.text)
        self.assertIn("<h1>PersonaLingo Skill - INTJ</h1>", r.text)
        self.assertIn("<h2>Overview</h2>", r.text)
        self.assertIn("<pre><code>", r.text)
        self.assertIn("print(&#x27;hello&#x27;)", r.text)  # html escape

    def test_preview_default_format_is_markdown(self):
        self._start_default_patches()
        with TestClient(self.app) as client:
            r = client.get("/api/distill/skill/fake_corpus/runnable/preview")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers["content-type"].startswith("text/markdown"))

    def test_preview_invalid_format_rejected(self):
        self._start_default_patches()
        with TestClient(self.app) as client:
            r = client.get(
                "/api/distill/skill/fake_corpus/runnable/preview",
                params={"format": "pdf"},
            )
        self.assertEqual(r.status_code, 422)

    def test_preview_corpus_not_found(self):
        p = patch(
            "app.routers.distill.get_corpus",
            new=AsyncMock(return_value=None),
        )
        p.start()
        self.addCleanup(p.stop)
        with TestClient(self.app) as client:
            r = client.get("/api/distill/skill/nope/runnable/preview")
        self.assertEqual(r.status_code, 404)

    # ---------- P2-7: download via FileResponse ----------
    def test_download_returns_valid_zip(self):
        self._start_default_patches()
        with TestClient(self.app) as client:
            r = client.get("/api/distill/skill/fake_corpus/runnable/download")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["content-type"], "application/zip")
        self.assertIn(
            "personalingo_skill_fake_corpus.zip",
            r.headers.get("content-disposition", ""),
        )
        # 内容应为合法 zip 且包含 4 份产物
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            f.write(r.content)
            zip_path = f.name
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
        self.assertIn("Skill.md", names)
        self.assertIn("corpus.json", names)
        self.assertIn("runtime_protocol.md", names)
        self.assertTrue(any("prompts" in n for n in names))

    def test_download_corpus_not_found(self):
        p = patch(
            "app.routers.distill.get_corpus",
            new=AsyncMock(return_value=None),
        )
        p.start()
        self.addCleanup(p.stop)
        with TestClient(self.app) as client:
            r = client.get("/api/distill/skill/nope/runnable/download")
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
