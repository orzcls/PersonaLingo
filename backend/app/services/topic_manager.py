"""题库管理服务"""
import json
import os
from typing import Optional
from app.db import crud


class TopicManager:
    """管理 IELTS 题库（P1/P2/P3）"""

    REQUIRED_FIELDS = ["part", "title", "questions"]
    VALID_PARTS = ["P1", "P2", "P3"]
    
    async def get_topics(self, part: str = None, season: str = None, 
                         category: str = None) -> list[dict]:
        """获取题库列表（支持多条件筛选）"""
        return await crud.get_topics(part=part, season=season, category=category)
    
    async def get_topic_by_id(self, topic_id: str) -> dict | None:
        """按ID获取单个题目"""
        from app.database import get_db
        db = await get_db()
        cursor = await db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        item = dict(row)
        for field in ["questions", "recommended_anchors"]:
            if item.get(field):
                try:
                    item[field] = json.loads(item[field])
                except:
                    pass
        return item
    
    async def add_topic(self, data: dict) -> str:
        """添加单个题目"""
        return await crud.create_topic(data)
    
    async def batch_import(self, topics: list[dict]) -> dict:
        """批量导入题库"""
        imported = 0
        errors = []
        for topic in topics:
            try:
                await crud.create_topic(topic)
                imported += 1
            except Exception as e:
                errors.append({"topic": topic.get("title", "unknown"), "error": str(e)})
        return {"imported": imported, "errors": errors, "total": len(topics)}
    
    async def update_topic(self, topic_id: str, data: dict) -> bool:
        """更新题目"""
        from app.database import get_db
        db = await get_db()
        updates = []
        values = []
        allowed_fields = ["part", "season", "category", "title", "questions", 
                         "is_new", "difficulty", "recommended_anchors", "source"]
        for key, val in data.items():
            if key in allowed_fields:
                if key in ("questions", "recommended_anchors"):
                    updates.append(f"{key} = ?")
                    values.append(json.dumps(val) if isinstance(val, list) else val)
                elif key == "is_new":
                    updates.append(f"{key} = ?")
                    values.append(1 if val else 0)
                else:
                    updates.append(f"{key} = ?")
                    values.append(val)
        if not updates:
            return False
        values.append(topic_id)
        cursor = await db.execute(f"UPDATE topics SET {', '.join(updates)} WHERE id = ?", values)
        await db.commit()
        return cursor.rowcount > 0
    
    async def delete_topic(self, topic_id: str) -> bool:
        """删除题目"""
        return await crud.delete_topic(topic_id)
    
    async def get_categories(self) -> list[str]:
        """获取所有可用的题目类别"""
        from app.database import get_db
        db = await get_db()
        cursor = await db.execute("SELECT DISTINCT category FROM topics WHERE category != '' ORDER BY category")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def get_seasons(self) -> list[str]:
        """获取所有可用的季度"""
        from app.database import get_db
        db = await get_db()
        cursor = await db.execute("SELECT DISTINCT season FROM topics WHERE season != '' ORDER BY season DESC")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def get_stats(self) -> dict:
        """获取题库统计信息"""
        from app.database import get_db
        db = await get_db()
        total = await crud.get_topic_count()
        
        cursor = await db.execute("SELECT part, COUNT(*) as count FROM topics GROUP BY part")
        by_part = {row[0]: row[1] for row in await cursor.fetchall()}
        
        cursor = await db.execute("SELECT COUNT(*) FROM topics WHERE is_new = 1")
        new_count = (await cursor.fetchone())[0]
        
        return {
            "total": total,
            "by_part": by_part,
            "new_topics": new_count,
            "old_topics": total - new_count
        }

    async def import_topics_from_json(self, data: list[dict]) -> dict:
        """从用户上传的JSON导入题库（存在则 UPDATE，不再 skip）"""
        from datetime import datetime
        imported = 0
        updated = 0
        errors = []

        for idx, item in enumerate(data):
            missing = [f for f in self.REQUIRED_FIELDS if f not in item]
            if missing:
                errors.append({"index": idx, "error": f"Missing fields: {missing}"})
                continue

            if item.get("part") not in self.VALID_PARTS:
                errors.append({"index": idx, "error": f"Invalid part: {item.get('part')}. Must be P1/P2/P3"})
                continue

            from app.database import get_db
            db = await get_db()
            title_key = (item["title"] or "").strip().lower()
            cursor = await db.execute(
                "SELECT id FROM topics WHERE LOWER(TRIM(title)) = ? AND part = ?",
                (title_key, item["part"])
            )
            existing = await cursor.fetchone()

            item.setdefault("source", "user_upload")
            item.setdefault("difficulty", "medium")
            item.setdefault("is_new", True)
            item.setdefault("season", "")
            item.setdefault("category", "")
            item.setdefault("recommended_anchors", [])
            item["updated_at"] = datetime.now().isoformat()

            try:
                if existing:
                    # 已存在 -> 刷新 season / source_url / updated_at / is_new
                    update_fields = ["season = ?", "updated_at = ?", "is_new = ?"]
                    values = [item["season"], item["updated_at"], 1 if item["is_new"] else 0]
                    if item.get("source_url"):
                        update_fields.append("source_url = ?")
                        values.append(item["source_url"])
                    if item.get("source"):
                        update_fields.append("source = ?")
                        values.append(item["source"])
                    values.append(existing[0])
                    await db.execute(
                        f"UPDATE topics SET {', '.join(update_fields)} WHERE id = ?",
                        values,
                    )
                    await db.commit()
                    updated += 1
                else:
                    await crud.create_topic(item)
                    imported += 1
            except Exception as e:
                errors.append({"index": idx, "title": item.get("title"), "error": str(e)})

        return {"imported": imported, "updated": updated, "skipped": 0, "errors": errors}

    async def import_topics_from_text(self, text: str, part: str) -> dict:
        """从纯文本导入（用LLM辅助解析结构）"""
        # 尝试简单的文本解析：每行一个题目
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        topics = []
        for line in lines:
            # 去除序号前缀 如 "1. " 或 "1) "
            import re
            cleaned = re.sub(r'^\d+[.)\s]+', '', line)
            if cleaned:
                topics.append({
                    "part": part,
                    "title": cleaned,
                    "questions": [cleaned],
                    "source": "text_import",
                    "is_new": True,
                    "difficulty": "medium"
                })

        if not topics:
            return {"imported": 0, "skipped": 0, "errors": [{"error": "No valid topics found in text"}]}

        return await self.import_topics_from_json(topics)

    async def scrape_latest_topics(self) -> dict:
        """联网搜索最新 IELTS 口语题库（真实搜索 + Jina Reader + RAG + LLM 抽取 + P3 衍生）"""
        from datetime import datetime
        from app.config import get_settings
        from app.services.topic_scraper import scrape_topics_pipeline, get_current_season

        settings = get_settings()

        # 1. 校验 LLM Key
        has_llm = (
            (settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY)
            or (settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY)
        )
        if not has_llm:
            return {
                "topics": [], "source": "",
                "error": "未配置 LLM API Key，请先在设置页面配置 LLM 服务商和 API Key。",
            }

        # 2. 校验搜索 Provider
        provider = (settings.SEARCH_PROVIDER or "").strip().lower()
        if not provider:
            return {
                "topics": [], "source": "",
                "error": "未配置搜索服务，请在 设置 → 网络搜索 选择 provider。",
            }

        season = get_current_season()

        # 3. 跑 P1/P2 抓取流水线
        result = await scrape_topics_pipeline(season=season, parts=("P1", "P2"), max_urls=10)

        p1_topics = result["by_part"].get("P1", [])
        p2_topics = result["by_part"].get("P2", [])
        source_urls = result["source_urls"]

        # 4. 为每道新 P2 衍生 P3（Task 5）
        derived_p3: list[dict] = []
        p3_errors: list[str] = []
        for p2 in p2_topics:
            try:
                children = await self.generate_p3_for_p2(p2, season=season)
                derived_p3.extend(children)
            except Exception as e:
                p3_errors.append(f"P2 '{p2.get('title')}' -> P3 衍生失败: {e}")

        all_topics = p1_topics + p2_topics + derived_p3
        for t in all_topics:
            t.setdefault("season", season)
            t.setdefault("is_new", True)
            t.setdefault("source", t.get("source", "web_scraped"))

        return {
            "topics": all_topics,
            "source": "web_search+rag+llm_extract",
            "current_season": season,
            "last_updated_at": datetime.now().isoformat(),
            "source_urls": source_urls,
            "derived_p3_count": len(derived_p3),
            "pipeline_errors": result.get("errors", []) + p3_errors,
            "error": None,
        }

    # ================= P3 衍生（Task 5）=================

    P3_SYSTEM = (
        "You are an IELTS speaking tutor. Given a Part 2 cue card, generate 3-4 abstract "
        "Part 3 discussion questions that naturally follow up on it. "
        "Return ONLY a JSON array of strings, no markdown fences."
    )

    async def generate_p3_for_p2(self, p2: dict, season: str | None = None) -> list[dict]:
        """给一道 P2 生成 3-4 个关联 P3 讨论题"""
        import re
        from datetime import datetime
        from app.services.llm_adapter import get_llm

        title = p2.get("title") or ""
        questions = p2.get("questions") or []
        if not title:
            return []

        # P2 入库 ID：用 title+part 查出来，没有则先不绑 linked_p2_id
        from app.database import get_db
        db = await get_db()
        cursor = await db.execute(
            "SELECT id FROM topics WHERE LOWER(TRIM(title)) = ? AND part = ?",
            ((title or "").strip().lower(), "P2"),
        )
        row = await cursor.fetchone()
        linked_p2_id = row[0] if row else None

        llm = get_llm()
        prompt = (
            f"Part 2 cue card title: {title}\n"
            f"Cue bullets: {json.dumps(questions, ensure_ascii=False)}\n\n"
            "Generate 3-4 Part 3 follow-up discussion questions. "
            "Return JSON array of strings only."
        )
        try:
            resp = await llm.chat(
                [
                    {"role": "system", "content": self.P3_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            text = resp.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text
                text = text.rsplit("```", 1)[0] if "```" in text else text
                text = text.strip()
                if text.startswith("json"):
                    text = text[4:].strip()
            match = re.search(r"\[[\s\S]*\]", text)
            raw = match.group() if match else text
            qs = json.loads(raw)
            if not isinstance(qs, list):
                return []
            qs = [q for q in qs if isinstance(q, str) and q.strip()]
            if not qs:
                return []
        except Exception:
            return []

        p3 = {
            "part": "P3",
            "title": f"Discussion: {title}",
            "questions": qs[:4],
            "category": p2.get("category", "abstract"),
            "difficulty": "hard",
            "is_new": True,
            "season": season or p2.get("season", ""),
            "source": "derived_from_p2",
            "linked_p2_id": linked_p2_id,
            "source_url": p2.get("source_url", ""),
            "updated_at": datetime.now().isoformat(),
        }
        return [p3]

    async def backfill_p3_for_all_p2(self, missing_only: bool = True, limit: int = 20) -> dict:
        """为库内所有（缺 P3 的）P2 批量补上衍生 P3"""
        from app.database import get_db
        db = await get_db()
        if missing_only:
            # 找出没有 linked_p2 指向自己的 P2
            cursor = await db.execute(
                """SELECT t.id, t.title, t.questions, t.category, t.season, t.source_url
                   FROM topics t
                   WHERE t.part = 'P2'
                     AND NOT EXISTS (SELECT 1 FROM topics p3 WHERE p3.part='P3' AND p3.linked_p2_id = t.id)
                   LIMIT ?""",
                (limit,),
            )
        else:
            cursor = await db.execute(
                "SELECT id, title, questions, category, season, source_url FROM topics WHERE part='P2' LIMIT ?",
                (limit,),
            )
        rows = await cursor.fetchall()
        generated = 0
        for row in rows:
            try:
                questions = json.loads(row[2]) if row[2] else []
            except Exception:
                questions = []
            p2 = {
                "title": row[1], "questions": questions, "category": row[3],
                "season": row[4], "source_url": row[5],
            }
            children = await self.generate_p3_for_p2(p2, season=row[4])
            for c in children:
                c["linked_p2_id"] = row[0]
                try:
                    await crud.create_topic(c)
                    generated += 1
                except Exception:
                    pass
        return {"generated": generated, "scanned": len(rows)}


def get_topic_manager() -> TopicManager:
    return TopicManager()
