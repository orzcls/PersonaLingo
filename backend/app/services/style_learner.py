"""
用户表达风格分析器
从对话中增量学习用户的英语表达风格特征，用于后续语料生成参考
"""
import re
from typing import Optional

from app.db.crud import get_corpus, update_corpus


class StyleLearner:
    """用户表达风格分析器"""

    # 常见英文连接词列表
    CONNECTORS = [
        "however", "moreover", "besides", "also", "furthermore",
        "in addition", "nevertheless", "meanwhile", "therefore",
        "consequently", "on the other hand", "as a result",
        "for instance", "for example", "in fact", "actually",
        "basically", "so", "then", "anyway", "though", "although"
    ]

    # 常见开头句式
    OPENING_PATTERNS = [
        "well", "actually", "i think", "to be honest", "honestly",
        "in my opinion", "personally", "i believe", "i mean",
        "you know", "i guess", "i would say", "for me",
        "from my perspective", "the thing is", "let me think",
        "that's a good question", "i suppose"
    ]

    async def analyze_message(self, text: str) -> dict:
        """
        分析单条消息的风格特征
        返回：句长、连接词、开头句型、词汇水平、语气
        """
        text_lower = text.lower().strip()
        sentences = self._split_sentences(text)

        # 平均句长（单词数）
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        avg_sentence_length = (
            sum(sentence_lengths) / len(sentence_lengths)
            if sentence_lengths else 0.0
        )

        # 检测常用连接词
        found_connectors = []
        for conn in self.CONNECTORS:
            if conn in text_lower:
                found_connectors.append(conn)

        # 检测开头句型
        found_openings = []
        for pattern in self.OPENING_PATTERNS:
            if text_lower.startswith(pattern) or f". {pattern}" in text_lower or f", {pattern}" in text_lower:
                found_openings.append(pattern)

        # 词汇复杂度估算
        vocabulary_level = self._estimate_vocabulary_level(text)

        # 语气检测
        tone = self._detect_tone(text)

        return {
            "avg_sentence_length": round(avg_sentence_length, 1),
            "common_connectors": found_connectors,
            "opening_patterns": found_openings,
            "vocabulary_level": vocabulary_level,
            "tone": tone,
        }

    async def update_user_style(self, corpus_id: str, new_message: str):
        """
        增量更新用户风格统计
        策略：新消息权重0.1，历史权重0.9（指数移动平均）
        """
        new_analysis = await self.analyze_message(new_message)

        # 从DB读取现有style
        corpus = await get_corpus(corpus_id)
        if not corpus:
            return

        existing_style = corpus.get("user_style") or {}
        if not isinstance(existing_style, dict):
            existing_style = {}

        # 加权合并
        merged = self._merge_styles(existing_style, new_analysis, new_weight=0.1)

        # 增加消息计数
        merged["message_count"] = existing_style.get("message_count", 0) + 1

        # 写回DB
        await update_corpus(corpus_id, {"user_style": merged})

    async def get_style_summary(self, corpus_id: str) -> dict:
        """获取用户风格摘要，用于后续语料生成时参考"""
        corpus = await get_corpus(corpus_id)
        if not corpus:
            return self._empty_style()

        style = corpus.get("user_style")
        if not style or not isinstance(style, dict):
            return self._empty_style()

        return style

    def _merge_styles(self, existing: dict, new: dict, new_weight: float = 0.1) -> dict:
        """加权合并新旧风格统计"""
        old_weight = 1.0 - new_weight

        # 平均句长：加权平均
        old_avg = existing.get("avg_sentence_length", 0.0)
        new_avg = new.get("avg_sentence_length", 0.0)
        merged_avg = old_avg * old_weight + new_avg * new_weight if old_avg else new_avg

        # 连接词：合并并保留频率最高的
        old_connectors = existing.get("common_connectors", [])
        new_connectors = new.get("common_connectors", [])
        merged_connectors = self._merge_list_with_frequency(
            old_connectors, new_connectors, max_items=10
        )

        # 开头句型：合并
        old_openings = existing.get("opening_patterns", [])
        new_openings = new.get("opening_patterns", [])
        merged_openings = self._merge_list_with_frequency(
            old_openings, new_openings, max_items=8
        )

        # 词汇水平：加权
        vocab_levels = {"basic": 1, "intermediate": 2, "advanced": 3}
        old_level_num = vocab_levels.get(existing.get("vocabulary_level", "basic"), 1)
        new_level_num = vocab_levels.get(new.get("vocabulary_level", "basic"), 1)
        merged_level_num = old_level_num * old_weight + new_level_num * new_weight
        if merged_level_num >= 2.5:
            merged_level = "advanced"
        elif merged_level_num >= 1.5:
            merged_level = "intermediate"
        else:
            merged_level = "basic"

        # 语气：如果不一致则标记为mixed
        old_tone = existing.get("tone", "casual")
        new_tone = new.get("tone", "casual")
        if old_tone == new_tone:
            merged_tone = old_tone
        else:
            merged_tone = "mixed"

        return {
            "avg_sentence_length": round(merged_avg, 1),
            "common_connectors": merged_connectors,
            "opening_patterns": merged_openings,
            "vocabulary_level": merged_level,
            "tone": merged_tone,
        }

    def _merge_list_with_frequency(self, old_list: list, new_list: list, max_items: int = 10) -> list:
        """合并两个列表，去重并限制数量"""
        combined = list(old_list) if old_list else []
        for item in (new_list or []):
            if item not in combined:
                combined.append(item)
        return combined[:max_items]

    def _split_sentences(self, text: str) -> list[str]:
        """将文本分割为句子"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _estimate_vocabulary_level(self, text: str) -> str:
        """估算词汇复杂度"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return "basic"

        # 基于平均词长和高级词汇比例
        avg_word_length = sum(len(w) for w in words) / len(words)
        long_words = [w for w in words if len(w) >= 8]
        long_ratio = len(long_words) / len(words) if words else 0

        if avg_word_length >= 6.0 or long_ratio >= 0.15:
            return "advanced"
        elif avg_word_length >= 4.5 or long_ratio >= 0.08:
            return "intermediate"
        else:
            return "basic"

    def _detect_tone(self, text: str) -> str:
        """检测语气正式度"""
        text_lower = text.lower()

        # 正式指标
        formal_markers = [
            "furthermore", "nevertheless", "consequently", "moreover",
            "in addition", "as a result", "it is worth noting",
            "one might argue", "it should be noted"
        ]
        # 非正式指标
        informal_markers = [
            "gonna", "wanna", "kinda", "yeah", "nah", "lol",
            "btw", "tbh", "you know", "like,", "stuff", "things like that"
        ]

        formal_count = sum(1 for m in formal_markers if m in text_lower)
        informal_count = sum(1 for m in informal_markers if m in text_lower)

        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "casual"
        else:
            return "mixed"

    def _empty_style(self) -> dict:
        """返回空的风格数据"""
        return {
            "avg_sentence_length": 0.0,
            "common_connectors": [],
            "opening_patterns": [],
            "vocabulary_level": "basic",
            "tone": "casual",
            "message_count": 0
        }


# 全局单例
_style_learner: Optional[StyleLearner] = None


def get_style_learner() -> StyleLearner:
    global _style_learner
    if _style_learner is None:
        _style_learner = StyleLearner()
    return _style_learner
