"""
笔记与思维导图自动生成器
语料库生成/更新、对话维护会话结束时自动生成学习笔记（含摘要+变更+建议），
并生成 Mermaid 格式思维导图代码。
"""
import json
import logging
from datetime import datetime

from app.services.llm_adapter import get_llm
from app.services.corpus_rag import get_corpus_rag
from app.db.crud import get_corpus, get_notes, create_note

logger = logging.getLogger(__name__)


class NoteGenerator:
    """笔记与思维导图生成器"""

    def __init__(self):
        self.llm = get_llm()

    async def generate_note(self, corpus_id: str, trigger_type: str,
                            changes_context: dict = None) -> dict:
        """
        生成笔记

        Args:
            corpus_id: 语料库ID
            trigger_type: 触发类型 "corpus_generation" | "corpus_update" | "conversation" | "manual"
            changes_context: 变更上下文

        Returns:
            笔记字典 {id, title, summary, changes, tips, mindmap_mermaid, ...}
        """
        # 1. 获取当前语料库数据
        corpus = await get_corpus(corpus_id)
        if not corpus:
            logger.warning(f"Corpus {corpus_id} not found, skip note generation")
            return None

        # 2. 构建prompt，生成笔记内容
        note_content = await self._generate_note_content(corpus, trigger_type, changes_context)

        # 3. 生成Mermaid思维导图
        mindmap = await self.generate_mindmap(corpus)

        # 4. 组装笔记数据
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        trigger_labels = {
            "corpus_generation": "语料库生成笔记",
            "corpus_update": "语料库更新笔记",
            "conversation": "对话维护笔记",
            "manual": "手动生成笔记"
        }
        title = f"{now} {trigger_labels.get(trigger_type, '笔记')}"

        note_data = {
            "corpus_id": corpus_id,
            "trigger_type": trigger_type,
            "title": title,
            "summary": note_content.get("summary", ""),
            "changes": note_content.get("changes", []),
            "tips": note_content.get("tips", []),
            "mindmap_mermaid": mindmap
        }

        # 5. 保存到数据库
        note_id = await create_note(note_data)

        # 6. 重建RAG索引（笔记也会被索引）
        rag = get_corpus_rag()
        rag.invalidate(corpus_id)

        note_data["id"] = note_id
        return note_data

    async def _generate_note_content(self, corpus: dict, trigger_type: str,
                                     changes_context: dict = None) -> dict:
        """通过LLM生成笔记的summary、changes、tips"""
        # 构建语料库摘要信息
        anchors = corpus.get("anchors") or []
        bridges = corpus.get("bridges") or []
        vocabulary = corpus.get("vocabulary") or []
        patterns = corpus.get("patterns") or []
        persona = corpus.get("persona") or {}
        band_strategy = corpus.get("band_strategy") or {}

        corpus_summary = (
            f"人格类型: {persona.get('mbti', 'N/A')}\n"
            f"目标分数段: {band_strategy.get('label', 'N/A')}\n"
            f"锚点数量: {len(anchors)}\n"
            f"桥接数量: {len(bridges)}\n"
            f"词汇升级数量: {len(vocabulary)}\n"
            f"句型模板数量: {len(patterns)}\n"
        )

        # 锚点详情
        anchor_details = ""
        for a in anchors[:5]:
            if isinstance(a, dict):
                anchor_details += f"- {a.get('label', '未命名')}: {a.get('story', '')[:80]}\n"

        # 变更上下文
        context_str = ""
        if changes_context:
            context_str = f"\n变更上下文: {json.dumps(changes_context, ensure_ascii=False)}"

        system_prompt = """你是一个IELTS口语学习助手，负责生成学习笔记。请根据语料库信息生成结构化笔记。
必须以严格JSON格式输出，不要添加其他文字：
{
  "summary": "简短摘要，描述当前语料库状态和本次变更要点（100字内）",
  "changes": ["变更点1", "变更点2", ...],
  "tips": ["学习建议1", "学习建议2", ...]
}"""

        user_prompt = f"""触发类型: {trigger_type}
{context_str}

当前语料库概况:
{corpus_summary}

锚点详情:
{anchor_details}

请生成本次学习笔记的JSON内容。"""

        try:
            result = await self.llm.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=1024
            )
            # 解析JSON
            parsed = self._parse_json_response(result)
            return parsed
        except Exception as e:
            logger.error(f"Note content generation failed: {e}")
            return {
                "summary": f"笔记自动生成失败: {str(e)}",
                "changes": [],
                "tips": []
            }

    async def generate_mindmap(self, corpus: dict) -> str:
        """
        生成Mermaid思维导图代码
        结构：以语料库为根，锚点为一级分支，桥接题目为二级分支
        """
        anchors = corpus.get("anchors") or []
        bridges = corpus.get("bridges") or []
        vocabulary = corpus.get("vocabulary") or []
        patterns = corpus.get("patterns") or []

        # 构建锚点-桥接映射
        anchor_bridges = {}
        for a in anchors:
            if isinstance(a, dict):
                aid = a.get("id", "")
                anchor_bridges[aid] = {
                    "label": a.get("label", "未命名"),
                    "topics": []
                }

        for b in bridges:
            if isinstance(b, dict):
                aid = b.get("anchor_id", "")
                topic_title = b.get("topic_title", "未知题目")
                if aid in anchor_bridges:
                    anchor_bridges[aid]["topics"].append(topic_title)

        # 构建Mermaid mindmap代码
        lines = ["mindmap", "  root((我的语料库))"]

        for aid, info in anchor_bridges.items():
            label = info["label"]
            lines.append(f"    {label}")
            for topic in info["topics"][:5]:  # 每个锚点最多展示5个桥接题
                # 清理topic名称中的特殊字符
                clean_topic = topic.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
                lines.append(f"      {clean_topic}")

        # 无锚点映射的桥接（孤立桥接）
        orphan_bridges = [b for b in bridges if isinstance(b, dict) and b.get("anchor_id", "") not in anchor_bridges]
        if orphan_bridges:
            lines.append("    其他桥接")
            for b in orphan_bridges[:3]:
                clean_title = b.get("topic_title", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "")
                lines.append(f"      {clean_title}")

        # 词汇统计
        if vocabulary:
            lines.append(f"    词汇升级")
            lines.append(f"      基础→高级 x{len(vocabulary)}")

        # 句型统计
        if patterns:
            persona = corpus.get("persona") or {}
            mbti = persona.get("mbti", "个性化")
            lines.append(f"    句型模板")
            lines.append(f"      {mbti}风格 x{len(patterns)}")

        return "\n".join(lines)

    async def generate_after_corpus_creation(self, corpus_id: str):
        """语料库首次生成后调用"""
        corpus = await get_corpus(corpus_id)
        if not corpus:
            return None

        changes_context = {
            "type": "initial_generation",
            "anchors_count": len(corpus.get("anchors") or []),
            "bridges_count": len(corpus.get("bridges") or []),
            "vocabulary_count": len(corpus.get("vocabulary") or []),
            "patterns_count": len(corpus.get("patterns") or []),
            "band_target": (corpus.get("band_strategy") or {}).get("label", "unknown")
        }
        return await self.generate_note(corpus_id, "corpus_generation", changes_context)

    async def generate_after_conversation(self, corpus_id: str,
                                          conversation_summary: str = None):
        """对话维护会话结束后调用"""
        changes_context = {
            "type": "conversation_maintenance",
            "summary": conversation_summary or "对话维护会话"
        }
        return await self.generate_note(corpus_id, "conversation", changes_context)

    def _parse_json_response(self, text: str) -> dict:
        """从LLM响应中提取JSON"""
        # 尝试直接解析
        text = text.strip()
        # 去除可能的 markdown 代码块标记
        if text.startswith("```"):
            lines = text.split("\n")
            # 移除首尾的 ``` 行
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试找到JSON对象
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        # 解析失败，返回默认
        return {
            "summary": text[:200] if text else "笔记生成中...",
            "changes": [],
            "tips": []
        }


def get_note_generator() -> NoteGenerator:
    """获取笔记生成器实例"""
    return NoteGenerator()
