from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.services.skill_exporter import SkillExporter

router = APIRouter(prefix="/skill", tags=["Skill导出"])
exporter = SkillExporter()


@router.get("/formats")
async def get_formats():
    """获取支持的导出格式列表"""
    return {
        "formats": [
            {
                "id": "markdown",
                "name": "Markdown Skill File",
                "description": "For Trae, Cursor, and similar IDE Agents",
                "extension": ".md",
                "icon": "document-text",
            },
            {
                "id": "json",
                "name": "JSON Schema",
                "description": "For GPTs, Coze, Dify, and similar platforms",
                "extension": ".json",
                "icon": "code-bracket",
            },
            {
                "id": "openapi",
                "name": "OpenAPI Specification",
                "description": "For Agents with API calling capabilities",
                "extension": ".yaml",
                "icon": "globe-alt",
            },
        ]
    }


@router.post("/export")
async def export_skill(data: dict):
    """
    导出 Skill 文件
    请求体: {"format": "markdown"|"json"|"openapi", "corpus_id": "optional-uuid"}
    返回: {"filename": "...", "content": "...", "mime_type": "..."}
    """
    format_type = data.get("format", "markdown")
    corpus_id = data.get("corpus_id")

    # 如果提供了 corpus_id，从 store 获取数据
    corpus_data = None
    if corpus_id:
        from app.storage import corpus_store
        if corpus_id in corpus_store:
            corpus_data = corpus_store[corpus_id]

    try:
        result = exporter.export(format_type, corpus_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
