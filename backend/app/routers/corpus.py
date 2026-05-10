"""
语料库路由 - 生成/流式进度/查询/更新
"""
import json
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from app.models.corpus import CorpusGenerate, CorpusResponse, CorpusData
from app.services.corpus_generator import (
    get_corpus_generator, get_generation_progress, find_progress_by_questionnaire
)
from app.db.crud import get_corpus, update_corpus

router = APIRouter(tags=["Corpus"])


@router.post("/generate")
async def generate_corpus(data: CorpusGenerate, background_tasks: BackgroundTasks):
    """
    触发语料库生成（后台异步执行）
    立即返回 questionnaire_id，前端通过 SSE 端点轮询进度
    """
    generator = get_corpus_generator()

    # 后台执行生成任务
    async def _run_generation():
        try:
            await generator.generate_full_corpus(data.questionnaire_id)
        except Exception:
            # 错误已在 generator 内部处理并写入数据库
            pass

    background_tasks.add_task(_run_generation)

    return {
        "status": "success",
        "message": "语料库生成已启动",
        "data": {
            "questionnaire_id": data.questionnaire_id,
            "stream_url": f"/api/corpus/generate/{data.questionnaire_id}/stream"
        }
    }


@router.get("/generate/{questionnaire_id}/stream")
async def stream_generation_progress(questionnaire_id: str):
    """
    SSE 流式推送生成进度
    前端通过 EventSource 连接此端点，实时获取每步完成状态
    """
    async def event_generator():
        """生成 SSE 事件流"""
        steps_order = ["persona", "anchors", "bridges", "vocabulary", "patterns", "practices"]
        completed_steps = set()
        max_wait = 300  # 最长等待300秒
        elapsed = 0
        poll_interval = 1.0

        while elapsed < max_wait:
            # 通过 questionnaire_id 查找对应的生成进度
            corpus_id, progress = find_progress_by_questionnaire(questionnaire_id)

            if progress:
                # 检查每步状态
                steps = progress.get("steps", {})
                for step in steps_order:
                    step_info = steps.get(step, {})
                    step_status = step_info.get("status", "")

                    if step_status == "completed" and step not in completed_steps:
                        completed_steps.add(step)
                        event_data = json.dumps({
                            "step": step,
                            "status": "completed",
                            "progress": len(completed_steps) / len(steps_order),
                            "message": f"Step '{step}' completed"
                        }, ensure_ascii=False)
                        yield f"data: {event_data}\n\n"

                    elif step_status == "generating" and step not in completed_steps:
                        event_data = json.dumps({
                            "step": step,
                            "status": "generating",
                            "progress": (len(completed_steps) + 0.5) / len(steps_order),
                            "message": f"Generating '{step}'..."
                        }, ensure_ascii=False)
                        yield f"data: {event_data}\n\n"

                # 检查整体状态
                overall_status = progress.get("status", "")
                if overall_status == "completed":
                    event_data = json.dumps({
                        "step": "all",
                        "status": "completed",
                        "progress": 1.0,
                        "message": "All steps completed successfully"
                    }, ensure_ascii=False)
                    yield f"data: {event_data}\n\n"
                    return

                elif overall_status == "failed":
                    event_data = json.dumps({
                        "step": "error",
                        "status": "failed",
                        "progress": len(completed_steps) / len(steps_order),
                        "message": progress.get("error", "Generation failed"),
                    }, ensure_ascii=False)
                    yield f"data: {event_data}\n\n"
                    return

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        # 超时
        yield f"data: {json.dumps({'step': 'timeout', 'status': 'failed', 'message': 'Generation timed out'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/{corpus_id}")
async def get_corpus_detail(corpus_id: str):
    """获取语料库完整数据"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    return {
        "status": "success",
        "data": corpus
    }


@router.put("/{corpus_id}")
async def update_corpus_data(corpus_id: str, data: dict):
    """手动更新语料库某部分（如用户编辑锚点故事）"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    # 只允许更新特定字段
    allowed_fields = {"persona", "anchors", "bridges", "vocabulary", "patterns", "practices", "user_style"}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    await update_corpus(corpus_id, update_data)

    # 使 RAG 索引失效，下次查询时重建
    from app.services.corpus_rag import get_corpus_rag
    rag = get_corpus_rag()
    rag.invalidate(corpus_id)

    return {
        "status": "success",
        "message": "Corpus updated",
        "updated_fields": list(update_data.keys())
    }


@router.get("/{corpus_id}/status")
async def get_corpus_status(corpus_id: str):
    """获取生成状态"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    # 同时检查内存中的进度信息
    progress = get_generation_progress(corpus_id)
    steps_status = {}
    if progress and progress.get("steps"):
        for step, info in progress["steps"].items():
            steps_status[step] = info.get("status", "unknown")

    return {
        "status": "success",
        "data": {
            "corpus_id": corpus_id,
            "generation_status": corpus.get("status", "unknown"),
            "steps": steps_status,
            "created_at": corpus.get("created_at", ""),
            "updated_at": corpus.get("updated_at", ""),
        }
    }
