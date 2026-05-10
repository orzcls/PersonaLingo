"""
\u4e09\u6bb5\u5f0f\u84b8\u998f\u8def\u7531 - \u5bf9\u9f50 huashu-nuwa "\u6df1\u5ea6\u8c03\u7814 \u2192 \u6846\u67b6\u63d0\u70bc \u2192 \u53ef\u8fd0\u884cSkill" \u7684\u5916\u9732\u5c42

\u7aef\u70b9:
- POST /api/distill/diagnose              \u6a21\u7cca\u9700\u6c42\u5165\u53e3: \u7528\u6237\u81ea\u7531\u6587\u672c \u2192 \u8bca\u65ad\u95ee\u5377 + \u63a8\u8350\u5206\u6570
- POST /api/distill/run                   \u89e6\u53d1 7 \u6b65\u84b8\u998f\u94fe\u8def (\u5411\u540e\u517c\u5bb9 /api/corpus/generate)
- GET  /api/distill/skill/{id}/runnable   \u5bfc\u51fa\u81ea\u5305\u542b\u53ef\u8fd0\u884c Skill \u5305
- GET  /api/distill/skill/{id}/runnable/download   \u6253\u5305\u4e3a zip \u4e0b\u8f7d

\u7edf\u4e00\u8fd4\u56de\u4f53: { "data": {...}, "error": null }
"""
import io
import json
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel

from app.services.corpus_generator import get_corpus_generator
from app.services.skill_exporter import SkillExporter
from app.services.llm_adapter import get_llm
from app.db.crud import get_corpus

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Distill"])


# ============================================================
# \u54cd\u5e94\u5305\u88c5
# ============================================================


def _ok(data):
    return {"data": data, "error": None}


def _err(message: str, code: int = 400):
    raise HTTPException(status_code=code, detail={"data": None, "error": message})


# ============================================================
# 1) \u8bca\u65ad\u5165\u53e3 (\u6a21\u7cca\u9700\u6c42)
# ============================================================


class DiagnoseRequest(BaseModel):
    text: str


_DIAGNOSE_SYSTEM = (
    "You are an IELTS speaking coach helping a student clarify fuzzy goals. "
    "Given their free-form self-description, return a diagnostic questionnaire "
    "and a suggested target band score. Output STRICT JSON only."
)

_DIAGNOSE_USER_TEMPLATE = """Student self-description:
\"\"\"{text}\"\"\"

Return JSON with schema:
{{
  "questions": [
    {{"id": "q1", "text": "...", "type": "single|multi", "options": ["...", "..."]}}
  ],
  "suggested_score": "6.0|6.5|7.0|7.5",
  "rationale": "short reason"
}}
Keep 3-5 questions covering: exam timeline, target score, weakest sub-skill.
"""


_FALLBACK_DIAGNOSE = {
    "questions": [
        {
            "id": "q1",
            "text": "\u4f60\u5e0c\u671b\u591a\u4e45\u5185\u53c2\u52a0\u96c5\u601d?",
            "type": "single",
            "options": ["30\u5929\u5185", "3\u4e2a\u6708\u5185", "\u534a\u5e74\u5185", "\u4ec5\u63d0\u5347\u4e0d\u8003\u8bd5"],
        },
        {
            "id": "q2",
            "text": "\u4f60\u5e0c\u671b\u7684\u76ee\u6807\u5206\u6570?",
            "type": "single",
            "options": ["6.0", "6.5", "7.0", "7.5+"],
        },
        {
            "id": "q3",
            "text": "\u4f60\u89c9\u5f97\u6700\u8584\u5f31\u7684\u73af\u8282?(\u53ef\u591a\u9009)",
            "type": "multi",
            "options": ["\u8bcd\u6c47", "\u6d41\u5229\u5ea6", "\u53d1\u97f3", "\u903b\u8f91\u7ed3\u6784"],
        },
    ],
    "suggested_score": "6.5",
    "rationale": "\u9ed8\u8ba4\u6a21\u677f(LLM \u4e0d\u53ef\u7528\u65f6\u964d\u7ea7\u8fd4\u56de)",
}


@router.post("/diagnose")
async def diagnose(req: DiagnoseRequest):
    """\u6a21\u7cca\u9700\u6c42\u5165\u53e3: \u81ea\u7531\u6587\u672c \u2192 \u8bca\u65ad\u95ee\u5377"""
    text = (req.text or "").strip()
    if not text:
        _err("text \u4e0d\u80fd\u4e3a\u7a7a", 422)

    try:
        llm = get_llm()
        raw = await llm.chat(
            messages=[
                {"role": "system", "content": _DIAGNOSE_SYSTEM},
                {"role": "user", "content": _DIAGNOSE_USER_TEMPLATE.format(text=text[:2000])},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        data = _safe_json(raw) or _FALLBACK_DIAGNOSE
        # \u6700\u5c0f\u6821\u9a8c
        if not isinstance(data.get("questions"), list) or not data["questions"]:
            data = _FALLBACK_DIAGNOSE
        return _ok(data)
    except Exception as e:
        logger.warning(f"/distill/diagnose LLM failed, fallback: {e}")
        return _ok(_FALLBACK_DIAGNOSE)


def _safe_json(text: str) -> Optional[dict]:
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        lines = [ln for ln in t.splitlines() if not ln.strip().startswith("```")]
        t = "\n".join(lines).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(t[start : end + 1])
    except json.JSONDecodeError:
        return None


# ============================================================
# 2) \u89e6\u53d1\u84b8\u998f (\u660e\u786e\u76ee\u6807 / \u8bca\u65ad\u540e\u5165\u53e3)
# ============================================================


@router.post("/run")
async def run_distill(
    background_tasks: BackgroundTasks,
    questionnaire_id: str = Query(..., description="\u95ee\u5377 ID"),
    include_research: bool = Query(True, description="\u662f\u5426\u542f\u7528 Stage 1+2 \u6df1\u5ea6\u8c03\u7814+\u6846\u67b6\u63d0\u70bc"),
):
    """\u542f\u52a8\u540e\u53f0 7 \u6b65\u84b8\u998f\u4efb\u52a1,\u7acb\u5373\u8fd4\u56de\u6d41\u5f0f\u8fdb\u5ea6\u7aef\u70b9"""
    generator = get_corpus_generator()

    async def _run():
        try:
            await generator.generate_full_corpus(
                questionnaire_id, include_research=include_research
            )
        except Exception as e:
            logger.error(f"/distill/run generation failed: {e}", exc_info=True)

    background_tasks.add_task(_run)

    return _ok(
        {
            "questionnaire_id": questionnaire_id,
            "include_research": include_research,
            "stages": [
                "research", "framework",
                "persona", "anchors", "bridges", "vocabulary", "patterns",
            ],
            "stream_url": f"/api/corpus/generate/{questionnaire_id}/stream",
        }
    )


# ============================================================
# 3) \u5bfc\u51fa\u53ef\u8fd0\u884c Skill \u5305
# ============================================================


@router.get("/skill/{corpus_id}/runnable")
async def export_runnable(corpus_id: str):
    """\u5bfc\u51fa\u76ee\u5f55 + \u6587\u4ef6\u6e05\u5355"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        _err(f"\u8bed\u6599\u5e93\u4e0d\u5b58\u5728: {corpus_id}", 404)

    exporter = SkillExporter()
    try:
        out_dir: Path = await exporter.export_runnable_skill(corpus_id)
    except Exception as e:
        logger.error(f"export_runnable_skill failed: {e}", exc_info=True)
        _err(f"\u5bfc\u51fa\u5931\u8d25: {e}", 500)

    files = sorted(
        str(p.relative_to(out_dir)).replace("\\", "/")
        for p in out_dir.rglob("*")
        if p.is_file()
    )
    return _ok(
        {
            "corpus_id": corpus_id,
            "path": str(out_dir),
            "files": files,
        }
    )


@router.get("/skill/{corpus_id}/runnable/download")
async def download_runnable(corpus_id: str, background_tasks: BackgroundTasks):
    """打包为 zip 返回下载 (P2-7: 大语料改走临时文件 + FileResponse)

    响应完成后由 BackgroundTasks 清理临时 zip，避免磁盘泄漏。
    """
    corpus = await get_corpus(corpus_id)
    if not corpus:
        _err(f"语料库不存在: {corpus_id}", 404)

    exporter = SkillExporter()
    out_dir: Path = await exporter.export_runnable_skill(corpus_id)

    # P2-7: 大文件场景走临时文件 + FileResponse，避免内存压力
    tmp = tempfile.NamedTemporaryFile(prefix=f"skill_{corpus_id}_", suffix=".zip", delete=False)
    tmp_path = Path(tmp.name)
    tmp.close()
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in out_dir.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=str(p.relative_to(out_dir)))

    def _cleanup(path: Path):
        try:
            path.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning(f"cleanup tmp zip failed: {exc}")

    background_tasks.add_task(_cleanup, tmp_path)

    return FileResponse(
        path=str(tmp_path),
        media_type="application/zip",
        filename=f"personalingo_skill_{corpus_id}.zip",
        background=background_tasks,
    )


# ============================================================
# 4) 在线预览 Skill.md (P2-3)
# ============================================================


@router.get("/skill/{corpus_id}/runnable/preview", response_class=PlainTextResponse)
async def preview_runnable(corpus_id: str, format: str = Query("markdown", pattern="^(markdown|html)$")):
    """返回 Skill.md 原文或极简 HTML 渲染，供前端/Agent 直接预览，免去下载解压"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        _err(f"语料库不存在: {corpus_id}", 404)

    exporter = SkillExporter()
    out_dir: Path = await exporter.export_runnable_skill(corpus_id)
    skill_md = out_dir / "Skill.md"
    if not skill_md.exists():
        _err("Skill.md 不存在", 500)

    md_text = skill_md.read_text(encoding="utf-8")
    if format == "markdown":
        return PlainTextResponse(md_text, media_type="text/markdown; charset=utf-8")

    # format == html: 极简渲染（不引入额外依赖）
    html = _render_minimal_html(md_text, title=f"PersonaLingo Skill · {corpus_id}")
    return PlainTextResponse(html, media_type="text/html; charset=utf-8")


def _render_minimal_html(md: str, title: str) -> str:
    """极简 Markdown → HTML 渲染：保留结构不引入外部依赖

    仅处理最常见元素：# 标题、```代码块、行内 `code`、段落。
    深度渲染应在前端用 marked/markdown-it 处理，后端只给个底线预览。
    """
    import html as _html
    lines = md.splitlines()
    out = [
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">",
        f"<title>{_html.escape(title)}</title>",
        "<style>body{font-family:-apple-system,Segoe UI,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;color:#24292f;line-height:1.6}"
        "pre{background:#f6f8fa;padding:.8rem;border-radius:6px;overflow:auto}"
        "code{background:#f6f8fa;padding:.1em .3em;border-radius:4px;font-size:.9em}"
        "pre code{background:transparent;padding:0}"
        "h1,h2,h3{border-bottom:1px solid #eaecef;padding-bottom:.3rem}</style></head><body>",
    ]
    in_code = False
    for raw in lines:
        if raw.startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(_html.escape(raw))
            continue
        stripped = raw.strip()
        if stripped.startswith("### "):
            out.append(f"<h3>{_html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            out.append(f"<h2>{_html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            out.append(f"<h1>{_html.escape(stripped[2:])}</h1>")
        elif not stripped:
            out.append("<br/>")
        else:
            out.append(f"<p>{_html.escape(stripped)}</p>")
    if in_code:
        out.append("</code></pre>")
    out.append("</body></html>")
    return "\n".join(out)
