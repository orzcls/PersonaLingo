"""题库管理 API 路由"""
import json
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional
from app.models.topic import TopicCreate, TopicFilter
from app.services.topic_manager import get_topic_manager

router = APIRouter()


@router.get("")
async def list_topics(
    part: Optional[str] = Query(None, description="P1/P2/P3"),
    season: Optional[str] = Query(None, description="e.g. 2025-Q2"),
    category: Optional[str] = Query(None, description="e.g. hobby_leisure, object, abstract")
):
    """获取题库列表（支持筛选）"""
    manager = get_topic_manager()
    topics = await manager.get_topics(part=part, season=season, category=category)
    return {"status": "success", "data": topics, "count": len(topics)}


@router.get("/stats")
async def get_stats():
    """获取题库统计信息"""
    manager = get_topic_manager()
    stats = await manager.get_stats()
    return {"status": "success", "data": stats}


@router.get("/categories")
async def get_categories():
    """获取所有题目类别"""
    manager = get_topic_manager()
    categories = await manager.get_categories()
    return {"status": "success", "data": categories}


@router.get("/seasons")
async def get_seasons():
    """获取所有可用季度"""
    manager = get_topic_manager()
    seasons = await manager.get_seasons()
    return {"status": "success", "data": seasons}


@router.get("/meta")
async def get_topics_meta():
    """返回当前考试季 / 最后更新时间 / stale 状态，供前端展示徽标用。"""
    from app.database import get_db
    from app.services.topic_scraper import get_current_season
    from app.config import get_settings

    db = await get_db()
    current_season = get_current_season()

    cursor = await db.execute("SELECT MAX(season) FROM topics WHERE season != ''")
    row = await cursor.fetchone()
    latest_db_season = row[0] if row and row[0] else ""

    cursor = await db.execute("SELECT MAX(updated_at) FROM topics")
    row = await cursor.fetchone()
    last_updated_at = row[0] if row and row[0] else None

    cursor = await db.execute("SELECT part, COUNT(*) FROM topics GROUP BY part")
    by_part = {r[0]: r[1] for r in await cursor.fetchall()}

    stale = bool(latest_db_season) and latest_db_season != current_season

    settings = get_settings()
    return {
        "status": "success",
        "data": {
            "current_season": current_season,
            "latest_db_season": latest_db_season,
            "last_updated_at": last_updated_at,
            "stale": stale,
            "by_part": by_part,
            "search_provider_configured": bool((settings.SEARCH_PROVIDER or "").strip()),
            "llm_configured": bool(
                settings.OPENAI_API_KEY if settings.LLM_PROVIDER == "openai" else settings.ANTHROPIC_API_KEY
            ),
        },
    }


@router.get("/{topic_id}")
async def get_topic(topic_id: str):
    """获取单个题目详情"""
    manager = get_topic_manager()
    topic = await manager.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"status": "success", "data": topic}


@router.post("")
async def create_topic(data: TopicCreate):
    """添加新题目"""
    manager = get_topic_manager()
    topic_id = await manager.add_topic(data.model_dump())
    return {"status": "success", "data": {"id": topic_id}, "message": "Topic created"}


@router.post("/import")
async def batch_import(topics: list[TopicCreate]):
    """批量导入题库（JSON body）"""
    manager = get_topic_manager()
    result = await manager.batch_import([t.model_dump() for t in topics])
    return {"status": "success", "data": result}


@router.post("/import/file")
async def import_topics_file(file: UploadFile = File(...)):
    """上传题库文件（支持 JSON/PDF/DOCX/TXT）"""
    import re as re_mod
    manager = get_topic_manager()
    
    # 读取文件内容
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".json"):
        # JSON 文件：直接解析
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("gbk")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="无法解码文件，请使用 UTF-8 编码")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"JSON 解析错误: {str(e)}")
        
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="JSON 文件应为题目数组")
        
        result = await manager.import_topics_from_json(data)

    elif filename.endswith(".pdf") or filename.endswith(".docx") or filename.endswith(".doc"):
        # PDF/DOCX 文件：解析文本后使用 LLM 提取题目
        from app.services.material_parser import MaterialParser
        from app.services.llm_adapter import get_llm
        from app.config import get_settings

        settings = get_settings()
        # 检查 API Key
        has_key = False
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            has_key = True
        elif settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            has_key = True
        if not has_key:
            raise HTTPException(status_code=400, detail="上传 PDF/DOCX 需要 LLM 服务来提取题目，请先在设置中配置 API Key。")

        parser = MaterialParser()
        parsed = parser.parse_file(file.filename or filename, content)
        raw_text = parsed.get("raw_text", "")

        if not raw_text or raw_text.startswith("["):
            raise HTTPException(status_code=400, detail=f"无法解析文件内容: {raw_text[:200]}")

        # 用 LLM 从文本中提取题目结构
        llm = get_llm()
        extract_prompt = f"""From the following IELTS speaking material, extract all speaking topics/questions as structured data.

Text content:
{raw_text[:8000]}

Return ONLY a JSON array (no markdown, no explanation) with format:
[{{"part": "P1"/"P2"/"P3", "title": "Topic Title", "questions": ["question1", "question2"], "category": "hobby_leisure"/"people"/"place"/"event"/"object"/"abstract"/"technology"/"education"/"society"/"health"/"environment"/"media", "difficulty": "easy"/"medium"/"hard"}}]

Extract as many topics as you can find. If a topic clearly belongs to P1 (short answer), P2 (long turn/cue card), or P3 (discussion), classify accordingly."""

        try:
            response = await llm.chat([
                {"role": "system", "content": "You extract IELTS speaking topics from training materials into structured JSON format. Return ONLY valid JSON array."},
                {"role": "user", "content": extract_prompt}
            ], temperature=0.3)

            # 清理并解析 JSON
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1] if "\n" in response else response
                response = response.rsplit("```", 1)[0] if "```" in response else response
                response = response.strip()
                if response.startswith("json"):
                    response = response[4:].strip()

            json_match = re_mod.search(r'\[[\s\S]*\]', response)
            if json_match:
                topics = json.loads(json_match.group())
            else:
                topics = json.loads(response)

            # 标记来源
            for topic in topics:
                topic.setdefault("source", "file_upload")
                topic.setdefault("is_new", True)

            result = await manager.import_topics_from_json(topics)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="LLM 返回的内容无法解析为有效 JSON，请尝试重新上传")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析文件失败: {str(e)}")

    elif filename.endswith(".txt") or filename.endswith(".md"):
        # 文本文件：按行解析
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("gbk")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="无法解码文件，请使用 UTF-8 编码")
        part = "P1"
        lower_text = text.lower()
        if "part 3" in lower_text or "p3" in lower_text:
            part = "P3"
        elif "part 2" in lower_text or "p2" in lower_text:
            part = "P2"
        result = await manager.import_topics_from_text(text, part)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式。支持: .json, .pdf, .docx, .doc, .txt")

    return {"status": "success", "data": result}


@router.post("/scrape")
async def scrape_topics():
    """获取最新题库（真实搜索+RAG+LLM抽取+P3衍生）"""
    manager = get_topic_manager()
    result = await manager.scrape_latest_topics()

    if result.get("error") and not result.get("topics"):
        raise HTTPException(status_code=400, detail=result["error"])

    imported = 0
    updated = 0
    errors = []
    if result["topics"]:
        import_result = await manager.import_topics_from_json(result["topics"])
        imported = import_result.get("imported", 0)
        updated = import_result.get("updated", 0)
        errors = import_result.get("errors", [])

    # 统计每个 part 的新增数
    by_part = {"P1": 0, "P2": 0, "P3": 0}
    for t in result.get("topics", []):
        p = t.get("part")
        if p in by_part:
            by_part[p] += 1

    return {
        "status": "success",
        "data": {
            "source": result.get("source", "unknown"),
            "current_season": result.get("current_season"),
            "last_updated_at": result.get("last_updated_at"),
            "topics_found": len(result.get("topics", [])),
            "by_part": by_part,
            "derived_p3": result.get("derived_p3_count", 0),
            "imported": imported,
            "updated": updated,
            "errors": errors,
            "pipeline_errors": result.get("pipeline_errors", []),
            "source_urls": result.get("source_urls", [])[:5],
        }
    }


@router.post("/backfill-p3")
async def backfill_p3(limit: int = 20):
    """为现有 P2 批量补上衍生的 P3。"""
    manager = get_topic_manager()
    result = await manager.backfill_p3_for_all_p2(missing_only=True, limit=limit)
    return {"status": "success", "data": result}


@router.put("/{topic_id}")
async def update_topic(topic_id: str, data: dict):
    """更新题目"""
    manager = get_topic_manager()
    success = await manager.update_topic(topic_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found or no changes")
    return {"status": "success", "message": "Topic updated"}


@router.delete("/{topic_id}")
async def delete_topic(topic_id: str):
    """删除题目"""
    manager = get_topic_manager()
    success = await manager.delete_topic(topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"status": "success", "message": "Topic deleted"}
