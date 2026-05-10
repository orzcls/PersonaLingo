"""
QMD (Query-Match-Decide) 检索增强引擎

三层架构：
1. Query Expansion — 用 LLM 扩展用户查询（同义词/相关词/意图分析）
2. Match — 多信号检索（BM25 + TF-IDF 余弦相似度）
3. Decide/Rerank — 用 LLM 对检索结果进行相关性重排

设计原则：
- 零外部模型依赖（不下载 EmbeddingGemma/Qwen2-reranker 等大模型）
- 利用已有的 LLM API 适配层做 Query Expansion 和 Reranking
- TF-IDF + Cosine Similarity 作为轻量 embedding 替代方案
- 全部异步，毫秒级基础检索 + 可选 LLM 增强
"""
import json
import logging
from typing import Optional

from app.services.llm_adapter import get_llm

logger = logging.getLogger(__name__)


# ============================================================
# Query Expansion (Q层)
# ============================================================

QUERY_EXPANSION_PROMPT = """You are a search query expansion assistant for an IELTS speaking corpus system.

Given the user's query, generate 3-5 expanded search terms that capture:
1. Synonyms and related phrases
2. IELTS-specific terminology related to the query
3. Topic variations that might match relevant corpus entries

User query: "{query}"

Respond with ONLY a JSON array of expanded query strings. Example:
["photography hobby", "taking photos", "camera skills", "visual arts interest"]

JSON array:"""


class QueryExpander:
    """查询扩展器 — 用 LLM 生成扩展查询词"""

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

    async def expand(self, query: str) -> list[str]:
        """
        扩展查询词
        
        Args:
            query: 原始查询
            
        Returns:
            扩展后的查询词列表（包含原始查询）
        """
        expanded = [query]  # 始终包含原始查询

        if self.use_llm:
            try:
                llm_expansions = await self._llm_expand(query)
                expanded.extend(llm_expansions)
            except Exception as e:
                logger.warning(f"LLM query expansion failed, falling back to rule-based: {e}")
                expanded.extend(self._rule_expand(query))
        else:
            expanded.extend(self._rule_expand(query))

        return expanded

    async def _llm_expand(self, query: str) -> list[str]:
        """用 LLM 做查询扩展"""
        llm = get_llm()
        prompt = QUERY_EXPANSION_PROMPT.format(query=query)

        response = await llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )

        # 解析 JSON 数组
        try:
            # 尝试提取 JSON 数组
            text = response.strip()
            if text.startswith("["):
                expansions = json.loads(text)
            else:
                # 尝试从文本中提取 JSON 部分
                start = text.find("[")
                end = text.rfind("]") + 1
                if start >= 0 and end > start:
                    expansions = json.loads(text[start:end])
                else:
                    expansions = []

            return [str(e) for e in expansions if isinstance(e, str)][:5]
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse LLM expansion response: {response[:100]}")
            return self._rule_expand(query)

    def _rule_expand(self, query: str) -> list[str]:
        """基于规则的简单查询扩展（fallback）"""
        expansions = []
        words = query.lower().split()

        # 简单的同义词映射（IELTS 口语常见话题）
        synonym_map = {
            "hobby": ["interest", "leisure activity", "pastime"],
            "travel": ["trip", "journey", "vacation", "tourism"],
            "food": ["cuisine", "cooking", "eating", "diet"],
            "music": ["song", "concert", "instrument", "melody"],
            "sport": ["exercise", "fitness", "workout", "physical activity"],
            "study": ["education", "learning", "academic", "school"],
            "work": ["job", "career", "profession", "occupation"],
            "family": ["parents", "relatives", "household", "home"],
            "friend": ["friendship", "companion", "social", "relationship"],
            "technology": ["tech", "digital", "internet", "gadget"],
            "book": ["reading", "literature", "novel", "story"],
            "movie": ["film", "cinema", "show", "entertainment"],
            "nature": ["environment", "outdoor", "scenery", "landscape"],
            "city": ["urban", "town", "metropolitan", "downtown"],
            "health": ["wellness", "medical", "fitness", "well-being"],
        }

        for word in words:
            if word in synonym_map:
                expansions.extend(synonym_map[word][:2])

        # 如果没匹配到同义词，生成 n-gram 变体
        if not expansions and len(words) > 1:
            # bigram 组合
            for i in range(len(words) - 1):
                expansions.append(f"{words[i]} {words[i+1]}")

        return expansions[:3]


# ============================================================
# Reranking (D层)
# ============================================================

RERANK_PROMPT = """You are a relevance scoring assistant for an IELTS speaking corpus retrieval system.

Given a user query and a list of retrieved corpus entries, score each entry's relevance from 0-10.

User query: "{query}"

Retrieved entries:
{entries}

Score each entry based on:
- Direct relevance to the query topic
- Usefulness for IELTS speaking preparation
- Quality of vocabulary/expressions contained

Respond with ONLY a JSON array of objects with "index" and "score" fields. Example:
[{{"index": 0, "score": 8}}, {{"index": 1, "score": 5}}]

JSON array:"""


class Reranker:
    """重排序器 — 用 LLM 对检索结果进行相关性评分"""

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

    async def rerank(self, query: str, results: list, top_k: int = 5) -> list:
        """
        对检索结果重排序
        
        Args:
            query: 用户查询
            results: SearchResult 列表
            top_k: 返回前 k 个结果
            
        Returns:
            重排序后的结果列表
        """
        if not results or len(results) <= 1:
            return results[:top_k]

        if self.use_llm and len(results) > 2:
            try:
                reranked = await self._llm_rerank(query, results, top_k)
                return reranked
            except Exception as e:
                logger.warning(f"LLM reranking failed, returning original order: {e}")
                return results[:top_k]
        else:
            return results[:top_k]

    async def _llm_rerank(self, query: str, results: list, top_k: int) -> list:
        """用 LLM 做重排序"""
        # 构造条目列表（截断内容避免超长）
        entries_text = ""
        for i, r in enumerate(results[:10]):  # 最多重排前10个
            content_preview = r.content[:150].replace("\n", " ")
            entries_text += f"[{i}] ({r.doc_type}) {content_preview}\n"

        llm = get_llm()
        prompt = RERANK_PROMPT.format(query=query, entries=entries_text)

        response = await llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )

        # 解析评分结果
        try:
            text = response.strip()
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                scores = json.loads(text[start:end])
            else:
                return results[:top_k]

            # 按分数排序
            score_map = {}
            for item in scores:
                idx = item.get("index", -1)
                score = item.get("score", 0)
                if 0 <= idx < len(results):
                    score_map[idx] = score

            # 对结果按 LLM 评分重排
            indexed_results = list(enumerate(results[:10]))
            indexed_results.sort(
                key=lambda x: score_map.get(x[0], 0),
                reverse=True
            )

            reranked = [r for _, r in indexed_results]
            return reranked[:top_k]

        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.warning(f"Failed to parse rerank response: {e}")
            return results[:top_k]


# ============================================================
# QMD Engine (统一入口)
# ============================================================

class QMDEngine:
    """
    QMD (Query-Match-Decide) 检索增强引擎
    
    整合查询扩展、多信号检索、结果重排三个阶段。
    可通过配置控制各层是否启用 LLM 增强。
    
    使用方式：
        engine = QMDEngine(use_llm_expansion=True, use_llm_rerank=True)
        expanded_queries = await engine.expand_query("photography hobby")
        reranked_results = await engine.rerank(query, candidate_results, top_k=5)
    """

    def __init__(
        self,
        use_llm_expansion: bool = True,
        use_llm_rerank: bool = True
    ):
        self.expander = QueryExpander(use_llm=use_llm_expansion)
        self.reranker = Reranker(use_llm=use_llm_rerank)

    async def expand_query(self, query: str) -> list[str]:
        """
        查询扩展：生成同义词/相关词
        
        Args:
            query: 原始查询字符串
            
        Returns:
            扩展后的查询词列表
        """
        return await self.expander.expand(query)

    async def rerank(self, query: str, results: list, top_k: int = 5) -> list:
        """
        重排序：用 LLM 对检索结果打分重排
        
        Args:
            query: 原始查询
            results: 候选检索结果列表
            top_k: 返回前 k 个
            
        Returns:
            重排序后的结果列表
        """
        return await self.reranker.rerank(query, results, top_k)

    async def search(self, query: str, candidates: list, top_k: int = 5) -> list:
        """
        完整 QMD 三层检索流程
        
        对已有候选列表执行：
        1. Q层 — 查询扩展（生成扩展查询词用于候选过滤/加权）
        2. M层 — 基于扩展词对候选进行多信号匹配评分
        3. D层 — LLM 重排序最终结果
        
        Args:
            query: 原始用户查询
            candidates: 候选结果列表（SearchResult 对象）
            top_k: 最终返回数量
            
        Returns:
            经过三层处理后的最终结果列表
        """
        if not candidates:
            return []

        # === Q层: Query Expansion ===
        try:
            expanded_queries = await self.expander.expand(query)
            logger.debug(f"QMD Q-layer: '{query}' -> {expanded_queries}")
        except Exception as e:
            logger.warning(f"QMD Q-layer failed, using original query: {e}")
            expanded_queries = [query]

        # === M层: Multi-signal Match (基于扩展词对候选评分) ===
        try:
            scored_candidates = self._score_candidates(expanded_queries, candidates)
            # 按匹配分排序，取 top_k * 2 作为重排候选
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            rerank_pool = [item[0] for item in scored_candidates[:top_k * 2]]
        except Exception as e:
            logger.warning(f"QMD M-layer scoring failed, using original order: {e}")
            rerank_pool = candidates[:top_k * 2]

        # === D层: Reranking ===
        try:
            final_results = await self.reranker.rerank(query, rerank_pool, top_k)
            return final_results
        except Exception as e:
            logger.warning(f"QMD D-layer failed, returning M-layer results: {e}")
            return rerank_pool[:top_k]

    def _score_candidates(self, queries: list[str], candidates: list) -> list[tuple]:
        """
        基于扩展查询词对候选进行简单词汇匹配评分
        
        作为 M 层在无索引场景下的轻量实现：
        统计扩展查询词在候选内容中出现的次数作为匹配信号。
        """
        from collections import Counter
        
        # 构建查询词集合
        query_tokens = set()
        for q in queries:
            tokens = q.lower().split()
            query_tokens.update(tokens)
        
        scored = []
        for candidate in candidates:
            content_lower = candidate.content.lower()
            # 计算匹配分：查询词在内容中的命中次数
            match_score = sum(1 for token in query_tokens if token in content_lower)
            # 融合原始分数（如果有）与匹配分
            combined_score = candidate.score * 0.7 + match_score * 0.3
            scored.append((candidate, combined_score))
        
        return scored


# 全局单例
_qmd_engine: Optional[QMDEngine] = None


def get_qmd_engine(
    use_llm_expansion: bool = True,
    use_llm_rerank: bool = True
) -> QMDEngine:
    """获取 QMD 引擎单例"""
    global _qmd_engine
    if _qmd_engine is None:
        _qmd_engine = QMDEngine(
            use_llm_expansion=use_llm_expansion,
            use_llm_rerank=use_llm_rerank
        )
    return _qmd_engine
