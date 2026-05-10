"""SQLite 表定义"""

SCHEMAS = [
    # 问卷记录表
    """
    CREATE TABLE IF NOT EXISTS questionnaires (
        id TEXT PRIMARY KEY,
        mbti_type TEXT NOT NULL,
        mbti_dimensions TEXT,
        interests_tags TEXT,
        interests_descriptions TEXT,
        ielts_target_score TEXT,
        ielts_topic_types TEXT,
        ielts_exam_date TEXT,
        personal_background TEXT,
        life_experiences TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 语料库表
    """
    CREATE TABLE IF NOT EXISTS corpora (
        id TEXT PRIMARY KEY,
        questionnaire_id TEXT REFERENCES questionnaires(id),
        status TEXT DEFAULT 'generating',
        persona TEXT,
        anchors TEXT,
        bridges TEXT,
        vocabulary TEXT,
        patterns TEXT,
        practices TEXT,
        band_strategy TEXT,
        user_style TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 题库表
    """
    CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        part TEXT NOT NULL,
        season TEXT,
        category TEXT,
        title TEXT NOT NULL,
        questions TEXT,
        is_new INTEGER DEFAULT 1,
        difficulty TEXT DEFAULT 'medium',
        recommended_anchors TEXT,
        source TEXT DEFAULT 'builtin',
        linked_p2_id TEXT,
        source_url TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 题源抓取缓存表（用于动态题库更新去重）
    """
    CREATE TABLE IF NOT EXISTS topic_sources (
        url TEXT PRIMARY KEY,
        title TEXT,
        content_hash TEXT,
        season TEXT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 上传资料表
    """
    CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT,
        raw_content TEXT,
        parsed_content TEXT,
        analysis_result TEXT,
        merged_to_corpus TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 对话记录表
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        corpus_id TEXT REFERENCES corpora(id),
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        extracted_items TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 笔记表
    """
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        corpus_id TEXT REFERENCES corpora(id),
        trigger_type TEXT,
        title TEXT,
        summary TEXT,
        changes TEXT,
        tips TEXT,
        mindmap_mermaid TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # 设置表
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """
]


async def create_tables(db):
    """创建所有表"""
    for schema in SCHEMAS:
        await db.execute(schema)
    await db.commit()
    print("[Database] All tables created/verified")
