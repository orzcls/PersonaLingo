from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.skill_exporter import SkillExporter

router = APIRouter(tags=["Skills"])
exporter = SkillExporter()


@router.get("/{corpus_id}/export/markdown")
async def export_markdown(corpus_id: str):
    """导出 Markdown 格式 Skill 文件"""
    try:
        content = await exporter.export_markdown(corpus_id)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": 'attachment; filename="personalingo_skill.md"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{corpus_id}/export/json")
async def export_json(corpus_id: str):
    """导出 JSON 格式 Skill 文件"""
    try:
        result = await exporter.export_json(corpus_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{corpus_id}/preview")
async def preview_skill(corpus_id: str, format: str = "markdown"):
    """预览 Skill 内容（不下载）"""
    try:
        if format == "json":
            return await exporter.export_json(corpus_id)
        else:
            content = await exporter.export_markdown(corpus_id)
            return Response(content=content, media_type="text/plain; charset=utf-8")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
