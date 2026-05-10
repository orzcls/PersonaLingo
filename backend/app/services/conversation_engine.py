"""
NotebookLM 风格对话维护引擎
支持：对话聊天、RAG上下文注入、语料提取、风格学习
"""
import json
from typing import Optional

from app.services.llm_adapter import get_llm
from app.services.corpus_rag import get_corpus_rag
from app.services.token_manager import get_token_manager
from app.services.style_learner import get_style_learner
from app.db.crud import (
    get_corpus, update_corpus,
    create_conversation_message, get_conversation_history
)


class ConversationEngine:
    """NotebookLM 风格对话维护引擎"""

    def __init__(self, corpus_id: str):
        self.corpus_id = corpus_id
        self.llm = get_llm()
        self.rag = get_corpus_rag()
        self.token_manager = get_token_manager()
        self.style_learner = get_style_learner()

    async def chat(self, user_message: str) -> dict:
        """
        处理用户消息，返回AI回复
        流程：
        1. 从DB加载历史对话
        2. RAG检索相关语料注入context
        3. Token检查，超阈值则压缩历史
        4. 调用LLM生成回复
        5. 分析回复是否建议语料更新
        6. 保存对话到DB
        7. 更新风格统计
        返回: {"reply": str, "suggestions": list[dict], "style_update": dict|None}
        """
        # 1. 加载历史对话
        history = await get_conversation_history(self.corpus_id, limit=50)
        messages = self._history_to_messages(history)

        # 追加当前用户消息
        messages.append({"role": "user", "content": user_message})

        # 2. RAG检索相关语料注入context
        rag_context = await self.rag.get_context_for_conversation(
            self.corpus_id, messages, max_context_tokens=2000
        )

        # 3. 构建system prompt
        corpus = await get_corpus(self.corpus_id)
        system_prompt = self._build_system_prompt(corpus, rag_context)

        # 组装完整消息
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        # 4. Token检查，超阈值则压缩历史
        full_messages, was_compacted = await self.token_manager.compact_if_needed(full_messages)

        # 5. 调用LLM生成回复
        raw_reply = await self.llm.chat(messages=full_messages, temperature=0.7)

        # 6. 解析回复，提取建议（内部JSON标记）
        reply, suggestions = self._parse_reply(raw_reply)

        # 7. 保存对话到DB
        await create_conversation_message(self.corpus_id, "user", user_message)
        await create_conversation_message(
            self.corpus_id, "assistant", reply,
            extracted_items=suggestions if suggestions else None
        )

        # 8. 更新风格统计（仅用户消息）
        style_update = None
        try:
            await self.style_learner.update_user_style(self.corpus_id, user_message)
            style_update = await self.style_learner.get_style_summary(self.corpus_id)
        except Exception:
            pass  # 风格更新失败不影响主流程

        return {
            "reply": reply,
            "suggestions": suggestions,
            "style_update": style_update,
            "was_compacted": was_compacted
        }

    async def extract_corpus_items(self, conversation_ids: list[str] = None, last_n: int = None) -> dict:
        """
        从对话中提取可加入语料库的内容
        返回: {"anchors": [...], "bridges": [...], "vocabulary": [...], "patterns": [...]}
        """
        # 获取对话内容
        history = await get_conversation_history(self.corpus_id, limit=100)

        if conversation_ids:
            history = [h for h in history if h.get("id") in conversation_ids]
        elif last_n:
            history = history[-last_n:]

        if not history:
            return {"anchors": [], "bridges": [], "vocabulary": [], "patterns": []}

        # 构建提取prompt
        conversation_text = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in history
        )

        extraction_prompt = self._build_extraction_prompt(conversation_text)

        messages = [
            {"role": "system", "content": extraction_prompt},
            {"role": "user", "content": f"Please analyze this conversation and extract corpus items:\n\n{conversation_text}"}
        ]

        result = await self.llm.chat(messages=messages, temperature=0.3)

        # 解析JSON结果
        extracted = self._parse_extraction_result(result)
        return extracted

    async def merge_extracted(self, items: dict) -> dict:
        """
        将提取的内容融合到语料库
        1. 追加到对应字段
        2. 更新数据库
        3. 重建RAG索引
        """
        corpus = await get_corpus(self.corpus_id)
        if not corpus:
            return {"success": False, "error": "Corpus not found"}

        updates = {}
        merge_stats = {"anchors": 0, "bridges": 0, "vocabulary": 0, "patterns": 0}

        # 合并各类内容
        for field in ["anchors", "bridges", "vocabulary", "patterns"]:
            new_items = items.get(field, [])
            if not new_items:
                continue

            existing = corpus.get(field) or []
            if not isinstance(existing, list):
                existing = []

            existing.extend(new_items)
            updates[field] = existing
            merge_stats[field] = len(new_items)

        if updates:
            await update_corpus(self.corpus_id, updates)
            # 重建RAG索引
            self.rag.invalidate(self.corpus_id)
            await self.rag.index_corpus(self.corpus_id)

        return {
            "success": True,
            "merged": merge_stats,
            "total_items": sum(merge_stats.values())
        }

    def _build_system_prompt(self, corpus: dict, rag_context: str) -> str:
        """构建对话system prompt"""
        if not corpus:
            corpus = {}

        # 统计语料库信息
        anchors = corpus.get("anchors") or []
        bridges = corpus.get("bridges") or []
        vocabulary = corpus.get("vocabulary") or []
        patterns = corpus.get("patterns") or []
        persona = corpus.get("persona") or {}
        band_strategy = corpus.get("band_strategy") or {}

        anchor_count = len(anchors) if isinstance(anchors, list) else 0
        bridge_count = len(bridges) if isinstance(bridges, list) else 0
        vocab_count = len(vocabulary) if isinstance(vocabulary, list) else 0
        pattern_count = len(patterns) if isinstance(patterns, list) else 0

        target_score = ""
        if isinstance(band_strategy, dict):
            target_score = band_strategy.get("target_band", "")
        if not target_score and isinstance(persona, dict):
            target_score = persona.get("target_score", "6.5")

        prompt = f"""You are an IELTS Speaking coach and corpus maintenance assistant for PersonaLingo.

## Your Role
- Help the user practice IELTS speaking and maintain their personal corpus
- Provide feedback on their English expression
- Suggest improvements and new corpus items when appropriate

## Current Corpus Status
- Anchor stories: {anchor_count}
- Bridge sentences: {bridge_count}
- Vocabulary items: {vocab_count}
- Sentence patterns: {pattern_count}
- Target band score: {target_score or '6.5'}

## Behavior Guidelines
1. When the user shares a NEW personal story or experience, suggest adding it as an anchor
2. When the user practices answering a question, analyze if you can extract new bridge sentences or vocabulary
3. When you notice useful expressions the user uses, highlight them
4. Keep your replies natural and encouraging
5. If suggesting corpus updates, embed them in your natural response

## Suggestion Format
When you have suggestions for corpus updates, append them at the END of your reply in this exact format:
<!--SUGGESTIONS
[{{"type": "anchor|bridge|vocabulary|pattern", "content": "...", "reason": "..."}}]
SUGGESTIONS-->

Only include the SUGGESTIONS block when you genuinely have suggestions. Do NOT include it in every reply.

{f'''## Relevant Corpus Context
{rag_context}''' if rag_context else ''}
"""
        return prompt

    def _build_extraction_prompt(self, conversation_text: str) -> str:
        """构建语料提取的prompt"""
        return """You are a corpus extraction specialist for IELTS speaking preparation.

Analyze the conversation and extract useful items that can be added to the user's personal corpus.

Return a JSON object with these categories:
{
    "anchors": [{"label": "short_label", "story": "the story/experience", "keywords": ["kw1", "kw2"]}],
    "bridges": [{"topic_title": "related topic", "bridge_sentence": "the bridge sentence", "category": "category"}],
    "vocabulary": [{"basic_word": "simple word", "upgrade": "advanced alternative", "context": "example usage"}],
    "patterns": [{"name": "pattern name", "formula": "the pattern formula", "example": "usage example", "when_to_use": "situation"}]
}

Rules:
- Only extract items that are genuinely useful for IELTS speaking
- Anchors: personal stories/experiences the user shared
- Bridges: sentences that connect topics to personal stories
- Vocabulary: upgraded words or expressions
- Patterns: reusable sentence structures
- If no items found for a category, use an empty array
- Return ONLY the JSON, no additional text"""

    def _parse_reply(self, raw_reply: str) -> tuple[str, list[dict]]:
        """解析LLM回复，分离正文和建议"""
        suggestions = []

        # 尝试提取 <!--SUGGESTIONS ... SUGGESTIONS--> 块
        import re
        pattern = r'<!--SUGGESTIONS\s*(.*?)\s*SUGGESTIONS-->'
        match = re.search(pattern, raw_reply, re.DOTALL)

        if match:
            # 提取建议JSON
            try:
                suggestions_json = match.group(1).strip()
                suggestions = json.loads(suggestions_json)
            except (json.JSONDecodeError, Exception):
                suggestions = []

            # 移除建议块，保留正文
            reply = raw_reply[:match.start()].strip()
        else:
            reply = raw_reply.strip()

        return reply, suggestions

    def _parse_extraction_result(self, result: str) -> dict:
        """解析LLM提取的语料结果"""
        default = {"anchors": [], "bridges": [], "vocabulary": [], "patterns": []}

        try:
            # 尝试直接解析JSON
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                return {
                    "anchors": parsed.get("anchors", []),
                    "bridges": parsed.get("bridges", []),
                    "vocabulary": parsed.get("vocabulary", []),
                    "patterns": parsed.get("patterns", []),
                }
        except json.JSONDecodeError:
            pass

        # 尝试从代码块中提取JSON
        import re
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if isinstance(parsed, dict):
                    return {
                        "anchors": parsed.get("anchors", []),
                        "bridges": parsed.get("bridges", []),
                        "vocabulary": parsed.get("vocabulary", []),
                        "patterns": parsed.get("patterns", []),
                    }
            except json.JSONDecodeError:
                pass

        return default

    def _history_to_messages(self, history: list[dict]) -> list[dict]:
        """将数据库历史记录转为LLM消息格式"""
        messages = []
        for item in history:
            role = item.get("role", "user")
            content = item.get("content", "")
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": content})
        return messages
