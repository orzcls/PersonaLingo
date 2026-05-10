"""数据访问层 - 各表的异步 CRUD 操作"""
import json
import uuid
from datetime import datetime
from app.database import get_db


# ============ Questionnaire CRUD ============

async def create_questionnaire(data: dict) -> str:
    db = await get_db()
    qid = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO questionnaires (id, mbti_type, mbti_dimensions, interests_tags, 
           interests_descriptions, ielts_target_score, ielts_topic_types, ielts_exam_date,
           personal_background, life_experiences)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (qid, data["mbti_type"], json.dumps(data.get("mbti_dimensions", {})),
         json.dumps(data.get("interests_tags", [])), json.dumps(data.get("interests_descriptions", [])),
         data.get("ielts_target_score", "6.5"), json.dumps(data.get("ielts_topic_types", [])),
         data.get("ielts_exam_date", ""),
         json.dumps(data.get("personal_background")) if data.get("personal_background") else None,
         json.dumps(data.get("life_experiences")) if data.get("life_experiences") else None)
    )
    await db.commit()
    return qid

async def get_questionnaire(qid: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM questionnaires WHERE id = ?", (qid,))
    row = await cursor.fetchone()
    if row is None:
        return None
    result = _row_to_dict(row)
    # 解析 JSON 字段
    for field in ["personal_background", "life_experiences"]:
        if result.get(field):
            try:
                result[field] = json.loads(result[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return result


# ============ Corpus CRUD ============

async def create_corpus(questionnaire_id: str) -> str:
    db = await get_db()
    corpus_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO corpora (id, questionnaire_id, status) VALUES (?, ?, 'generating')""",
        (corpus_id, questionnaire_id)
    )
    await db.commit()
    return corpus_id

async def get_corpus(corpus_id: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM corpora WHERE id = ?", (corpus_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    result = _row_to_dict(row)
    # 解析JSON字段
    for field in ["persona", "anchors", "bridges", "vocabulary", "patterns", "practices", "band_strategy", "user_style", "learner_profile", "capability_framework"]:
        if result.get(field):
            try:
                result[field] = json.loads(result[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return result

async def update_corpus(corpus_id: str, data: dict):
    db = await get_db()
    updates = []
    values = []
    for key, val in data.items():
        if key in ("persona", "anchors", "bridges", "vocabulary", "patterns", "practices", "band_strategy", "user_style", "learner_profile", "capability_framework"):
            updates.append(f"{key} = ?")
            values.append(json.dumps(val) if isinstance(val, (dict, list)) else val)
        elif key in ("status",):
            updates.append(f"{key} = ?")
            values.append(val)
    updates.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(corpus_id)
    await db.execute(f"UPDATE corpora SET {', '.join(updates)} WHERE id = ?", values)
    await db.commit()


# ============ Topics CRUD ============

async def create_topic(data: dict) -> str:
    db = await get_db()
    topic_id = data.get("id", str(uuid.uuid4()))
    now_iso = datetime.now().isoformat()
    await db.execute(
        """INSERT OR REPLACE INTO topics (id, part, season, category, title, questions, 
           is_new, difficulty, recommended_anchors, source, linked_p2_id, source_url, updated_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (topic_id, data["part"], data.get("season", ""), data.get("category", ""),
         data["title"], json.dumps(data.get("questions", [])),
         1 if data.get("is_new", True) else 0, data.get("difficulty", "medium"),
         json.dumps(data.get("recommended_anchors", [])), data.get("source", "builtin"),
         data.get("linked_p2_id"), data.get("source_url"),
         data.get("updated_at", now_iso))
    )
    await db.commit()
    return topic_id

async def get_topics(part: str = None, season: str = None, category: str = None) -> list:
    db = await get_db()
    query = "SELECT * FROM topics WHERE 1=1"
    params = []
    if part:
        query += " AND part = ?"
        params.append(part)
    if season:
        query += " AND season = ?"
        params.append(season)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY part, category, title"
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    results = []
    for row in rows:
        item = _row_to_dict(row)
        for field in ["questions", "recommended_anchors"]:
            if item.get(field):
                try:
                    item[field] = json.loads(item[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        results.append(item)
    return results

async def delete_topic(topic_id: str) -> bool:
    db = await get_db()
    cursor = await db.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    await db.commit()
    return cursor.rowcount > 0

async def get_topic_count() -> int:
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) FROM topics")
    row = await cursor.fetchone()
    return row[0]


# ============ Materials CRUD ============

async def create_material(data: dict) -> str:
    db = await get_db()
    mid = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO materials (id, filename, file_type, raw_content, parsed_content, analysis_result)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (mid, data["filename"], data.get("file_type", ""), data.get("raw_content", ""),
         json.dumps(data.get("parsed_content")) if data.get("parsed_content") else None,
         json.dumps(data.get("analysis_result")) if data.get("analysis_result") else None)
    )
    await db.commit()
    return mid

async def get_materials() -> list:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM materials ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


# ============ Conversations CRUD ============

async def create_conversation_message(corpus_id: str, role: str, content: str, extracted_items: list = None) -> str:
    db = await get_db()
    msg_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO conversations (id, corpus_id, role, content, extracted_items)
           VALUES (?, ?, ?, ?, ?)""",
        (msg_id, corpus_id, role, content, json.dumps(extracted_items) if extracted_items else None)
    )
    await db.commit()
    return msg_id

async def get_conversation_history(corpus_id: str, limit: int = 50) -> list:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM conversations WHERE corpus_id = ? ORDER BY created_at ASC LIMIT ?",
        (corpus_id, limit)
    )
    rows = await cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


# ============ Notes CRUD ============

async def create_note(data: dict) -> str:
    db = await get_db()
    note_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO notes (id, corpus_id, trigger_type, title, summary, changes, tips, mindmap_mermaid)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (note_id, data.get("corpus_id"), data.get("trigger_type", "manual"),
         data.get("title", ""), data.get("summary", ""),
         json.dumps(data.get("changes", [])), json.dumps(data.get("tips", [])),
         data.get("mindmap_mermaid", ""))
    )
    await db.commit()
    return note_id

async def get_notes(corpus_id: str = None) -> list:
    db = await get_db()
    if corpus_id:
        cursor = await db.execute("SELECT * FROM notes WHERE corpus_id = ? ORDER BY created_at DESC", (corpus_id,))
    else:
        cursor = await db.execute("SELECT * FROM notes ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    return [_row_to_dict(row) for row in rows]

async def get_note(note_id: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


# ============ Settings CRUD ============

async def get_setting(key: str) -> str | None:
    db = await get_db()
    cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    return row[0] if row else None

async def set_setting(key: str, value: str):
    db = await get_db()
    await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    await db.commit()


# ============ Helper ============

def _row_to_dict(row) -> dict:
    """将 aiosqlite Row 转为 dict"""
    if row is None:
        return None
    return dict(row)
