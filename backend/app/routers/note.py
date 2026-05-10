"""笔记与思维导图 API 路由"""
from fastapi import APIRouter, HTTPException

from app.db.crud import get_notes, get_note, get_corpus
from app.services.note_generator import get_note_generator
from app.models.note import NoteResponse

router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("/{corpus_id}")
async def list_notes(corpus_id: str):
    """获取语料库的所有笔记列表（按时间倒序）"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    notes = await get_notes(corpus_id)
    results = []
    for n in notes:
        # 解析 JSON 字段
        import json
        changes = n.get("changes", "[]")
        tips = n.get("tips", "[]")
        if isinstance(changes, str):
            try:
                changes = json.loads(changes)
            except (json.JSONDecodeError, TypeError):
                changes = []
        if isinstance(tips, str):
            try:
                tips = json.loads(tips)
            except (json.JSONDecodeError, TypeError):
                tips = []

        results.append({
            "id": n["id"],
            "corpus_id": n.get("corpus_id"),
            "trigger_type": n.get("trigger_type", "manual"),
            "title": n.get("title", ""),
            "summary": n.get("summary", ""),
            "changes": changes,
            "tips": tips,
            "mindmap_mermaid": n.get("mindmap_mermaid", ""),
            "created_at": n.get("created_at", "")
        })
    return {"notes": results, "total": len(results)}


@router.get("/{corpus_id}/latest-mindmap")
async def get_latest_mindmap(corpus_id: str):
    """获取最新的思维导图Mermaid代码"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    notes = await get_notes(corpus_id)
    if not notes:
        # 没有笔记时，直接根据语料库生成思维导图（不保存）
        generator = get_note_generator()
        mindmap = await generator.generate_mindmap(corpus)
        return {"mindmap_mermaid": mindmap, "note_id": None}

    # 返回最新一条笔记的思维导图
    latest = notes[0]
    return {
        "mindmap_mermaid": latest.get("mindmap_mermaid", ""),
        "note_id": latest.get("id")
    }


@router.get("/{corpus_id}/{note_id}")
async def get_note_detail(corpus_id: str, note_id: str):
    """获取单条笔记详情（含思维导图代码）"""
    note = await get_note(note_id)
    if not note or note.get("corpus_id") != corpus_id:
        raise HTTPException(status_code=404, detail="Note not found")

    import json
    changes = note.get("changes", "[]")
    tips = note.get("tips", "[]")
    if isinstance(changes, str):
        try:
            changes = json.loads(changes)
        except (json.JSONDecodeError, TypeError):
            changes = []
    if isinstance(tips, str):
        try:
            tips = json.loads(tips)
        except (json.JSONDecodeError, TypeError):
            tips = []

    return {
        "id": note["id"],
        "corpus_id": note.get("corpus_id"),
        "trigger_type": note.get("trigger_type", "manual"),
        "title": note.get("title", ""),
        "summary": note.get("summary", ""),
        "changes": changes,
        "tips": tips,
        "mindmap_mermaid": note.get("mindmap_mermaid", ""),
        "created_at": note.get("created_at", "")
    }


@router.post("/{corpus_id}/generate")
async def generate_note_manually(corpus_id: str):
    """手动触发笔记生成"""
    corpus = await get_corpus(corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    # 兼容两种状态值：新蒸馏管线写入 "completed"，旧路径写入 "ready"
    status = corpus.get("status")
    if status not in ("completed", "ready"):
        raise HTTPException(status_code=400, detail="Corpus is not ready yet")

    generator = get_note_generator()
    result = await generator.generate_note(corpus_id, "manual")

    if not result:
        raise HTTPException(status_code=500, detail="Note generation failed")

    return {"note": result}
