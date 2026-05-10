"""
Stage 1 — LearnerResearcher (深度调研层)

对齐 huashu-nuwa 的"深度调研"段:
从多源(questionnaire / materials / conversation history / topics)聚合学生信号,
产出结构化 LearnerProfile,供 Stage 2 提炼能力框架使用。

设计原则:
- 默认只消费本地 DB,不外联网络(与 .env:DISTILL_RESEARCH_WEB_SEARCH 对齐)
- 任何数据源缺失都走降级路径,保证下游可继续
- LLM 仅用于信号摘要(optional);无 key 时走规则路径
"""
import json
import logging
import re
from datetime import datetime
from typing import Optional

from app.config import get_settings
from app.db.crud import (
    get_questionnaire,
    get_materials,
    get_conversation_history,
    get_topics,
)

logger = logging.getLogger(__name__)


# ============================================================
# 规则工具(无需 LLM)
# ============================================================

_CONNECTOR_WORDS = {
    "however", "moreover", "therefore", "meanwhile", "furthermore",
    "besides", "nevertheless", "instead", "actually", "basically",
    "for example", "for instance", "on the other hand", "as a result",
}


def _avg_sentence_length(text: str) -> float:
    """平均句长(按空格切词,按 . ! ? 切句)"""
    if not text:
        return 0.0
    sents = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sents:
        return 0.0
    total_words = sum(len(s.split()) for s in sents)
    return round(total_words / len(sents), 2)


def _count_connectors(text: str) -> int:
    if not text:
        return 0
    low = text.lower()
    return sum(1 for w in _CONNECTOR_WORDS if w in low)


def _derive_weakness_signals(samples: list[dict]) -> list[str]:
    """从语言样本中提取弱点信号(纯规则,零成本)"""
    if not samples:
        return []
    joined = "\n".join(s.get("text", "") for s in samples if s.get("text"))
    signals: list[str] = []
    avg = _avg_sentence_length(joined)
    if avg and avg < 8:
        signals.append(f"short_sentences(avg={avg})")
    connectors = _count_connectors(joined)
    if connectors <= 1:
        signals.append("lack_connectors")
    # 词汇丰富度粗估
    tokens = [t for t in re.split(r"\W+", joined.lower()) if t]
    if tokens:
        unique_ratio = len(set(tokens)) / max(len(tokens), 1)
        if unique_ratio < 0.35:
            signals.append(f"low_lexical_diversity({round(unique_ratio, 2)})")
    return signals


# ============================================================
# LearnerResearcher
# ============================================================


class LearnerResearcher:
    """Stage 1 深度调研器

    参考 huashu-nuwa 的"深度调研"段:聚合本地多源数据,产出 LearnerProfile。
    """

    # 纳入调研的材料/对话上限,防止 prompt 膨胀
    MAX_MATERIALS = 10
    MAX_CONVERSATIONS = 30

    def __init__(self, enable_web: Optional[bool] = None):
        settings = get_settings()
        self.enable_web = (
            enable_web
            if enable_web is not None
            else settings.DISTILL_RESEARCH_WEB_SEARCH
        )

    async def research(
        self,
        questionnaire_id: str,
        corpus_id: Optional[str] = None,
    ) -> dict:
        """
        多源聚合 → LearnerProfile

        Returns:
            dict 结构参考 docs/蒸馏链路三段式改造/DESIGN §2.1
        """
        # --- 1. 必备:问卷 ---
        questionnaire = await get_questionnaire(questionnaire_id)
        if not questionnaire:
            logger.warning(
                f"LearnerResearcher: questionnaire not found ({questionnaire_id}), "
                f"returning empty profile"
            )
            return self._empty_profile()

        background = self._extract_background(questionnaire)
        goal_vector = self._extract_goal(questionnaire)

        # --- 2. 可选:上传材料作为语言样本源 ---
        language_samples: list[dict] = []
        try:
            materials = await get_materials() or []
            for m in materials[: self.MAX_MATERIALS]:
                text = m.get("raw_content") or ""
                if text:
                    language_samples.append(
                        {
                            "source": "material",
                            "source_id": m.get("id"),
                            "filename": m.get("filename"),
                            "text": text[:2000],  # 截断避免单条过大
                        }
                    )
        except Exception as e:
            logger.warning(f"LearnerResearcher: read materials failed: {e}")

        # --- 3. 可选:历史对话作为语言样本源 ---
        if corpus_id:
            try:
                msgs = await get_conversation_history(corpus_id, limit=self.MAX_CONVERSATIONS) or []
                user_msgs = [m for m in msgs if m.get("role") == "user"]
                for m in user_msgs:
                    text = m.get("content") or ""
                    if text:
                        language_samples.append(
                            {
                                "source": "chat",
                                "source_id": m.get("id"),
                                "text": text[:1000],
                            }
                        )
            except Exception as e:
                logger.warning(f"LearnerResearcher: read conversations failed: {e}")

        # --- 4. 题库信号:兴趣关联的热门 part/topic ---
        topic_stats = await self._scan_topic_signals(background.get("interests", []))

        # --- 5. 弱点推断 ---
        weakness_signals = _derive_weakness_signals(language_samples)

        profile = {
            "background": background,
            "language_samples": language_samples,
            "weakness_signals": weakness_signals,
            "goal_vector": goal_vector,
            "topic_signals": topic_stats,
            "source_stats": {
                "materials": sum(1 for s in language_samples if s["source"] == "material"),
                "chats": sum(1 for s in language_samples if s["source"] == "chat"),
                "topics": topic_stats.get("total", 0),
            },
            "web_enabled": self.enable_web,
            "generated_at": datetime.now().isoformat(),
        }
        return profile

    # -------------------------- helpers -----------------------

    def _extract_background(self, q: dict) -> dict:
        """解析问卷 → 背景子档案(与 corpus_generator.generate_persona 字段保持一致)"""
        def _loads(v, default):
            if v is None:
                return default
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    return default
            return v

        return {
            "mbti_type": q.get("mbti_type") or "",
            "mbti_dimensions": _loads(q.get("mbti_dimensions"), {}),
            "interests": _loads(q.get("interests_tags"), []),
            "interests_descriptions": _loads(q.get("interests_descriptions"), []),
            "personal_background": _loads(q.get("personal_background"), {}),
            "life_experiences": _loads(q.get("life_experiences"), {}),
        }

    def _extract_goal(self, q: dict) -> dict:
        """解析问卷 → 目标向量"""
        def _loads(v, default):
            if v is None:
                return default
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    return default
            return v

        topic_types = _loads(q.get("ielts_topic_types"), [])
        # 将 P1/P2/P3 偏好作为 priority_parts
        priority_parts = [t for t in topic_types if t in ("P1", "P2", "P3")]
        return {
            "target_score": q.get("ielts_target_score") or "6.5",
            "priority_parts": priority_parts or ["P1", "P2"],
            "exam_date": q.get("ielts_exam_date") or "",
            "focus_topics": _loads(q.get("interests_tags"), [])[:8],
        }

    async def _scan_topic_signals(self, interests: list[str]) -> dict:
        """根据兴趣从题库中挑选候选场景(仅计数,不拉文本)"""
        try:
            all_topics = await get_topics() or []
        except Exception as e:
            logger.warning(f"LearnerResearcher: read topics failed: {e}")
            return {"total": 0, "matches": []}

        if not interests:
            return {"total": len(all_topics), "matches": []}

        low_interests = [i.lower() for i in interests if isinstance(i, str)]
        matches: list[dict] = []
        for t in all_topics:
            title = (t.get("title") or "").lower()
            category = (t.get("category") or "").lower()
            if any(i in title or i in category for i in low_interests):
                matches.append(
                    {
                        "id": t.get("id"),
                        "part": t.get("part"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                    }
                )
            if len(matches) >= 20:
                break
        return {"total": len(all_topics), "matches": matches}

    def _empty_profile(self) -> dict:
        """降级空档案,保证下游字段形态稳定"""
        return {
            "background": {},
            "language_samples": [],
            "weakness_signals": [],
            "goal_vector": {
                "target_score": "6.5",
                "priority_parts": ["P1", "P2"],
                "exam_date": "",
                "focus_topics": [],
            },
            "topic_signals": {"total": 0, "matches": []},
            "source_stats": {"materials": 0, "chats": 0, "topics": 0},
            "web_enabled": self.enable_web,
            "generated_at": datetime.now().isoformat(),
        }


# 模块级工厂(与项目其它 service 的 get_*() 模式一致)
_researcher_instance: Optional[LearnerResearcher] = None


def get_learner_researcher() -> LearnerResearcher:
    global _researcher_instance
    if _researcher_instance is None:
        _researcher_instance = LearnerResearcher()
    return _researcher_instance
