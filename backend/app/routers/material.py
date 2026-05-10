"""资料上传与解析 API 路由"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.services.material_parser import get_material_parser
from app.db import crud

router = APIRouter()


class MergeRequest(BaseModel):
    """素材融合请求体"""
    corpus_id: Optional[str] = None
    selected_items: Optional[dict] = None


@router.post("/upload")
async def upload_material(file: UploadFile = File(...)):
    """上传资料文件"""
    parser = get_material_parser()
    
    # 检查文件类型
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in parser.SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(parser.SUPPORTED_TYPES)}"
        )
    
    # 读取文件内容
    content_bytes = await file.read()
    
    # 解析文件
    try:
        parsed = parser.parse_file(file.filename, content_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File parsing failed: {str(e)}")
    
    # 保存到数据库
    material_id = await crud.create_material({
        "filename": file.filename,
        "file_type": ext,
        "raw_content": parsed["raw_text"][:50000],  # 限制存储大小
        "parsed_content": parsed
    })
    
    return {
        "status": "success",
        "data": {
            "id": material_id,
            "filename": file.filename,
            "file_type": ext,
            "word_count": parsed["word_count"],
            "sections_count": len(parsed["sections"])
        },
        "message": "File uploaded and parsed successfully"
    }


@router.get("")
async def list_materials():
    """获取已上传资料列表"""
    materials = await crud.get_materials()
    # 不返回raw_content（太大），只返回元数据
    result = []
    for m in materials:
        result.append({
            "id": m["id"],
            "filename": m["filename"],
            "file_type": m["file_type"],
            "created_at": m["created_at"],
            "has_analysis": m.get("analysis_result") is not None,
            "merged_to_corpus": m.get("merged_to_corpus")
        })
    return {"status": "success", "data": result}


@router.post("/{material_id}/analyze")
async def analyze_material(material_id: str, target_band: str = "7.0"):
    """使用 LLM 分析资料内容，提取可用于语料库的元素"""
    from app.database import get_db
    import json
    
    db = await get_db()
    cursor = await db.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material = dict(row)
    
    # 构建parsed_content
    parsed_content = {"raw_text": material.get("raw_content", "")}
    if material.get("parsed_content"):
        try:
            parsed_content = json.loads(material["parsed_content"])
        except (json.JSONDecodeError, TypeError):
            pass
    
    # LLM 分析
    parser = get_material_parser()
    analysis = await parser.analyze_for_corpus(parsed_content, target_band)
    
    # 保存分析结果
    await db.execute(
        "UPDATE materials SET analysis_result = ? WHERE id = ?",
        (json.dumps(analysis), material_id)
    )
    await db.commit()
    
    return {
        "status": "success",
        "data": analysis,
        "message": "Analysis complete. Review and select items to merge into corpus."
    }


@router.post("/{material_id}/merge")
async def merge_to_corpus(material_id: str, body: MergeRequest):
    """将分析结果融合到指定语料库

    前端通过 JSON body 传入 corpus_id 和 selected_items（可选）。
    向前兼容：未提供 corpus_id 时返回 400。
    """
    from app.database import get_db
    import json

    corpus_id = body.corpus_id
    selected_items = body.selected_items
    if not corpus_id:
        raise HTTPException(status_code=400, detail="corpus_id is required in request body")

    db = await get_db()
    cursor = await db.execute("SELECT analysis_result FROM materials WHERE id = ?", (material_id,))
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Material not found")
    
    if not row[0]:
        raise HTTPException(status_code=400, detail="Material has not been analyzed yet. Call /analyze first.")
    
    analysis_result = json.loads(row[0])
    
    parser = get_material_parser()
    result = await parser.merge_to_corpus(corpus_id, analysis_result, selected_items)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 标记已融合
    await db.execute(
        "UPDATE materials SET merged_to_corpus = ? WHERE id = ?",
        (corpus_id, material_id)
    )
    await db.commit()
    
    return {"status": "success", "data": result}
