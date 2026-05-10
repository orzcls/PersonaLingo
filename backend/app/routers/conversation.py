"""
对话维护 API 路由
提供聊天、历史查询、语料提取和合并、风格分析等端点
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.conversation_engine import ConversationEngine
from app.services.style_learner import get_style_learner
from app.db.crud import get_corpus, get_conversation_history

router = APIRouter(prefix="/api/conversations", tags=["Conversation"])


# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    content: str


class ExtractRequest(BaseModel):
    conversation_ids: Optional[list[str]] = None
    last_n: Optional[int] = None


class MergeRequest(BaseModel):
    anchors: Optional[list[dict]] = None
    bridges: Optional[list[dict]] = None
    vocabulary: Optional[list[dict]] = None
    patterns: Optional[list[dict]] = None


# ============ Routes ============

@router.post("/{corpus_id}/chat")
async def chat(corpus_id: str, request: ChatRequest):
    """发送消息，返回AI回复+建议"""
    # 验证corpus存在
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    engine = ConversationEngine(corpus_id)
    result = await engine.chat(request.content)

    return {
        "reply": result["reply"],
        "suggestions": result.get("suggestions", []),
        "style_update": result.get("style_update"),
        "was_compacted": result.get("was_compacted", False),
        "corpus_id": corpus_id,
    }


@router.get("/{corpus_id}/history")
async def get_history(corpus_id: str, limit: int = 50):
    """获取对话历史"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    history = await get_conversation_history(corpus_id, limit=limit)
    return {
        "corpus_id": corpus_id,
        "messages": history,
        "count": len(history)
    }


@router.post("/{corpus_id}/extract")
async def extract_from_conversation(corpus_id: str, request: ExtractRequest):
    """从指定对话提取语料"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    engine = ConversationEngine(corpus_id)
    extracted = await engine.extract_corpus_items(
        conversation_ids=request.conversation_ids,
        last_n=request.last_n
    )

    return {
        "corpus_id": corpus_id,
        "extracted": extracted,
        "total_items": sum(len(v) for v in extracted.values())
    }


@router.post("/{corpus_id}/merge")
async def merge_to_corpus(corpus_id: str, request: MergeRequest):
    """确认并融合提取的语料到语料库"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    items = {
        "anchors": request.anchors or [],
        "bridges": request.bridges or [],
        "vocabulary": request.vocabulary or [],
        "patterns": request.patterns or [],
    }

    # 检查是否有内容可合并
    total = sum(len(v) for v in items.values())
    if total == 0:
        raise HTTPException(status_code=400, detail="No items to merge")

    engine = ConversationEngine(corpus_id)
    result = await engine.merge_extracted(items)

    return result


@router.get("/{corpus_id}/style")
async def get_user_style(corpus_id: str):
    """获取用户风格分析结果"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    learner = get_style_learner()
    style = await learner.get_style_summary(corpus_id)

    return {
        "corpus_id": corpus_id,
        "style": style
    }
