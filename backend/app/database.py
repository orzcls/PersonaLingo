import aiosqlite
import os
from app.config import get_settings

_db_connection = None


async def get_db() -> aiosqlite.Connection:
    """获取数据库连接（单例）"""
    global _db_connection
    if _db_connection is None:
        settings = get_settings()
        # 确保数据目录存在
        os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
        _db_connection = await aiosqlite.connect(settings.DB_PATH)
        _db_connection.row_factory = aiosqlite.Row
        # 启用 WAL 模式提升并发性能
        await _db_connection.execute("PRAGMA journal_mode=WAL")
        await _db_connection.execute("PRAGMA foreign_keys=ON")
    return _db_connection


async def close_db():
    """关闭数据库连接"""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None


async def init_db():
    """初始化数据库（创建表 + 加载内置数据）"""
    db = await get_db()
    from app.db.schemas import create_tables
    await create_tables(db)
    # 数据库迁移（幂等）：topics 表新加列
    await _add_column_if_missing(db, "topics", "linked_p2_id", "TEXT")
    await _add_column_if_missing(db, "topics", "source_url", "TEXT")
    await _add_column_if_missing(db, "topics", "updated_at", "TIMESTAMP")
    # questionnaires 表新加列
    await _add_column_if_missing(db, "questionnaires", "personal_background", "TEXT")
    await _add_column_if_missing(db, "questionnaires", "life_experiences", "TEXT")
    # corpora 表新加列(三段式蒸馏:Stage1/Stage2 产物)
    await _add_column_if_missing(db, "corpora", "learner_profile", "TEXT")
    await _add_column_if_missing(db, "corpora", "capability_framework", "TEXT")
    # 加载内置题库：每次启动都扫描 data/ 下所有 topics_p*.json（含季度后缀）
    # → 新数据幂等导入 / 更新；老数据保留。
    from app.db.crud import get_topic_count
    # 启动时清理早期错标的 corpus_demo 残留（比如曾被错入为 2026-Q2 的 1-4 月题目）
    await _cleanup_stale_corpus_demo()
    await _sync_builtin_topics()
    print(f"[Database] Initialized at {get_settings().DB_PATH}. Topics: {await get_topic_count()}")


async def _add_column_if_missing(db, table: str, column: str, col_type: str):
    """幂等地给表添加列（存在则跳过）"""
    try:
        cursor = await db.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in await cursor.fetchall()]
        if column not in cols:
            await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            await db.commit()
    except Exception as e:
        print(f"[Database] Migration skip {table}.{column}: {e}")


async def _cleanup_stale_corpus_demo():
    """删除早期错标为 2026-Q2 的 corpus_demo 题目残留。

    旧脚本 extract_2026q2_topics.py 曾把 demo 目录的 1-4 月 PDF 错入为
    season=2026-Q2，source=corpus_demo_2026q2；新脚本输出 id为 p?_2026q1_*，
    旧记录不会被 UPSERT 触及。此处一次性删除避免两套共存。"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "DELETE FROM topics WHERE source LIKE ?",
            ("corpus_demo_2026q2%",),
        )
        await db.commit()
        if cursor.rowcount and cursor.rowcount > 0:
            print(f"[Database] Cleanup removed {cursor.rowcount} stale corpus_demo_2026q2 rows")
    except Exception as e:
        print(f"[Database] Cleanup skip: {e}")


async def _sync_builtin_topics():
    """扫描 app/data/topics_p*.json，幂等地 UPSERT 到数据库。

    - 首次启动：表为空，全量 INSERT
    - 后续启动：多个季度 JSON（如 topics_p1.json / topics_p1_2026q2.json）将被透过
      TopicManager.import_topics_from_json 导入，同 title+part 已存在的条目会刷新
      season / source / is_new / updated_at。
    """
    import json
    import glob
    from app.services.topic_manager import get_topic_manager
    from app.db.crud import get_topic_count

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    # 排序：旧文件先导，新季度 JSON 后导，确保新季度的 season/source 能覆盖同名条目
    patterns = [
        os.path.join(data_dir, "topics_p1.json"),
        os.path.join(data_dir, "topics_p2.json"),
        os.path.join(data_dir, "topics_p3.json"),
    ]
    # 再加上所有带季度后缀的 topics_p?_????q?.json
    patterns.extend(sorted(glob.glob(os.path.join(data_dir, "topics_p[1-3]_*.json"))))

    seen: set[str] = set()
    manager = get_topic_manager()
    initial_count = await get_topic_count()
    total_imported = 0
    total_updated = 0

    for path in patterns:
        if not path or path in seen or not os.path.exists(path):
            continue
        seen.add(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                topics = json.load(f)
            if not isinstance(topics, list):
                continue
            result = await manager.import_topics_from_json(topics)
            total_imported += result.get("imported", 0)
            total_updated += result.get("updated", 0)
            print(
                f"[Database] Seeded {os.path.basename(path)}: "
                f"+{result.get('imported', 0)} new, ~{result.get('updated', 0)} updated"
            )
        except Exception as e:
            print(f"[Database] Skip {os.path.basename(path)}: {e}")

    if initial_count == 0 and total_imported == 0 and total_updated == 0:
        print("[Database] WARN: no seed topics found under app/data/")


async def _load_builtin_topics():
    """旧调用入口（兼容）：委托给 _sync_builtin_topics。"""
    await _sync_builtin_topics()
