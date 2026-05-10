"""
轻量级语料库 RAG 检索引擎
基于 QMD (Query-Match-Decide) 三层架构：
  - Q: 查询扩展 (LLM/规则)
  - M: 多信号检索 (BM25 + TF-IDF Cosine Similarity)
  - D: 重排序 (LLM 相关性评分)

无需外部向量数据库，毫秒级基础检索 + 可选 LLM 增强
参考 Claude Code 的异步预取模式
"""
import math
import re
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional
import json

from app.database import get_db

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """检索结果"""
    doc_id: str
    doc_type: str       # "anchor" | "bridge" | "vocabulary" | "pattern" | "note" | "conversation"
    content: str        # 原始内容
    score: float        # BM25 分数
    metadata: dict      # 额外元数据（part, category, anchor_id等）


# ============================================================
# 停用词集合
# ============================================================
STOP_WORDS = frozenset({
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'shall', 'can',
    'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
    'it', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
    'she', 'we', 'they', 'my', 'your', 'his', 'her', 'our',
    'their', 'and', 'or', 'but', 'not', 'no', 'if', 'when',
    'what', 'which', 'who', 'how', 'where', 'why'
})


def tokenize(text: str) -> list[str]:
    """统一分词函数：英文小写 + 按空格/标点分割 + 过滤停用词"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


# ============================================================
# TF-IDF 余弦相似度引擎 (M层 — 轻量 embedding 替代)
# ============================================================

class TFIDFIndex:
    """TF-IDF 向量空间模型 + 余弦相似度
    
    作为轻量级 embedding 替代方案：
    - 无需外部模型或 API
    - 捕获词汇级别的语义相关性
    - 与 BM25 互补（BM25 偏精确匹配，TF-IDF 偏向量空间相似度）
    """

    def __init__(self):
        self.doc_count = 0
        self.doc_ids: list[str] = []
        self.doc_contents: dict[str, str] = {}
        self.doc_metadata: dict[str, dict] = {}
        # doc_tf 保存原始 TF（归一化后不含 IDF），doc_tfidf 为 _compute_idf 基于 doc_tf 重新计算的结果
        # 分离两者可避免 _compute_idf 被多次调用时原地反复乘 IDF 导致向量爆炸
        self.doc_tf: dict[str, dict[str, float]] = {}
        self.doc_tfidf: dict[str, dict[str, float]] = {}
        self.df: dict[str, int] = defaultdict(int)  # token -> 文档频率
        self._dirty = True  # 标记是否需要重算 IDF

    def add_document(self, doc_id: str, content: str, metadata: dict = None):
        """添加文档"""
        tokens = tokenize(content)
        self.doc_ids.append(doc_id)
        self.doc_contents[doc_id] = content
        self.doc_metadata[doc_id] = metadata or {}

        # TF (词频归一化)——保存到 doc_tf，IDF 加权结果延迟到 _compute_idf 中生成
        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        self.doc_tf[doc_id] = {token: freq / max_tf for token, freq in tf.items()}

        # 更新 DF
        for token in set(tokens):
            self.df[token] += 1

        self.doc_count += 1
        self._dirty = True

    def _compute_idf(self):
        """基于 doc_tf 重新生成 doc_tfidf，避免累计污染"""
        if not self._dirty:
            return
        new_tfidf: dict[str, dict[str, float]] = {}
        for doc_id, tf_vec in self.doc_tf.items():
            weighted = {}
            for token, tf_val in tf_vec.items():
                idf = math.log((self.doc_count + 1) / (self.df.get(token, 0) + 1)) + 1
                weighted[token] = tf_val * idf
            new_tfidf[doc_id] = weighted
        self.doc_tfidf = new_tfidf
        self._dirty = False

    def search(self, query: str, top_k: int = 5, filter_fn=None) -> list[SearchResult]:
        """TF-IDF 余弦相似度检索"""
        self._compute_idf()

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # 构建查询向量
        query_tf = Counter(query_tokens)
        max_qtf = max(query_tf.values()) if query_tf else 1
        query_vec = {}
        for token, freq in query_tf.items():
            idf = math.log((self.doc_count + 1) / (self.df.get(token, 0) + 1)) + 1
            query_vec[token] = (freq / max_qtf) * idf

        # 查询向量模长
        q_norm = math.sqrt(sum(v * v for v in query_vec.values()))
        if q_norm == 0:
            return []

        # 计算余弦相似度
        scores = []
        for doc_id in self.doc_ids:
            if filter_fn and not filter_fn(self.doc_metadata.get(doc_id, {})):
                continue

            doc_vec = self.doc_tfidf.get(doc_id, {})
            # 点积
            dot = sum(query_vec.get(t, 0) * doc_vec.get(t, 0) for t in query_vec)
            # 文档向量模长
            d_norm = math.sqrt(sum(v * v for v in doc_vec.values()))
            if d_norm == 0:
                continue

            cosine = dot / (q_norm * d_norm)
            if cosine > 0:
                scores.append((doc_id, cosine))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in scores[:top_k]:
            metadata = self.doc_metadata.get(doc_id, {})
            results.append(SearchResult(
                doc_id=doc_id,
                doc_type=metadata.get("type", "unknown"),
                content=self.doc_contents.get(doc_id, ""),
                score=score,
                metadata=metadata
            ))
        return results

    def clear(self):
        """清空索引"""
        self.doc_count = 0
        self.doc_ids.clear()
        self.doc_contents.clear()
        self.doc_metadata.clear()
        self.doc_tf.clear()
        self.doc_tfidf.clear()
        self.df.clear()
        self._dirty = True


# ============================================================
# BM25 倒排索引 (M层 — 关键词精确匹配)
# ============================================================

class BM25Index:
    """BM25 倒排索引"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = 0
        self.avg_dl = 0
        self.doc_lengths = {}          # doc_id -> 文档长度
        self.doc_contents = {}         # doc_id -> 原始内容
        self.doc_metadata = {}         # doc_id -> 元数据
        self.inverted_index = defaultdict(list)  # token -> [(doc_id, tf)]
        self.df = defaultdict(int)     # token -> 文档频率
    
    def add_document(self, doc_id: str, content: str, metadata: dict = None):
        """添加文档到索引"""
        tokens = tokenize(content)
        self.doc_lengths[doc_id] = len(tokens)
        self.doc_contents[doc_id] = content
        self.doc_metadata[doc_id] = metadata or {}
        
        # 计算词频
        tf = Counter(tokens)
        seen_tokens = set()
        for token, freq in tf.items():
            self.inverted_index[token].append((doc_id, freq))
            if token not in seen_tokens:
                self.df[token] += 1
                seen_tokens.add(token)
        
        self.doc_count += 1
        # 更新平均文档长度
        total_length = sum(self.doc_lengths.values())
        self.avg_dl = total_length / self.doc_count if self.doc_count > 0 else 0
    
    def search(self, query: str, top_k: int = 5, filter_fn=None) -> list[SearchResult]:
        """BM25 检索"""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        
        scores = defaultdict(float)
        
        for token in query_tokens:
            if token not in self.inverted_index:
                continue
            
            # IDF 计算
            df = self.df[token]
            idf = math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1)
            
            for doc_id, tf in self.inverted_index[token]:
                # 如果有过滤条件，跳过不匹配的文档
                if filter_fn and not filter_fn(self.doc_metadata.get(doc_id, {})):
                    continue
                
                dl = self.doc_lengths[doc_id]
                # BM25 评分公式
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
                scores[doc_id] += idf * (numerator / denominator)
        
        # 排序并返回 top_k
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in sorted_docs:
            metadata = self.doc_metadata.get(doc_id, {})
            results.append(SearchResult(
                doc_id=doc_id,
                doc_type=metadata.get("type", "unknown"),
                content=self.doc_contents.get(doc_id, ""),
                score=score,
                metadata=metadata
            ))
        
        return results
    
    def clear(self):
        """清空索引"""
        self.doc_count = 0
        self.avg_dl = 0
        self.doc_lengths.clear()
        self.doc_contents.clear()
        self.doc_metadata.clear()
        self.inverted_index.clear()
        self.df.clear()


class CorpusRAG:
    """语料库 RAG 检索服务
    
    采用 QMD 三层架构：
    1. Q (Query Expansion) — 扩展查询词，提高召回率
    2. M (Multi-signal Match) — BM25 + TF-IDF 双通道检索
    3. D (Decide/Rerank) — LLM 相关性评分重排
    
    配置选项：
    - enable_query_expansion: 是否启用 LLM 查询扩展（默认True）
    - enable_tfidf: 是否启用 TF-IDF 双通道（默认True）
    - enable_rerank: 是否启用 LLM 重排序（默认True）
    - bm25_weight: BM25 分数权重（默认0.6）
    - tfidf_weight: TF-IDF 分数权重（默认0.4）
    """
    
    def __init__(
        self,
        enable_query_expansion: bool = True,
        enable_tfidf: bool = True,
        enable_rerank: bool = True,
        bm25_weight: float = 0.6,
        tfidf_weight: float = 0.4
    ):
        self._bm25_indexes: dict[str, BM25Index] = {}   # corpus_id -> BM25Index
        self._tfidf_indexes: dict[str, TFIDFIndex] = {}  # corpus_id -> TFIDFIndex
        self.enable_query_expansion = enable_query_expansion
        self.enable_tfidf = enable_tfidf
        self.enable_rerank = enable_rerank
        self.bm25_weight = bm25_weight
        self.tfidf_weight = tfidf_weight
    
    def _add_doc_to_indexes(self, corpus_id: str, doc_id: str, content: str, metadata: dict):
        """同时添加文档到 BM25 和 TF-IDF 索引"""
        self._bm25_indexes[corpus_id].add_document(doc_id, content, metadata)
        if self.enable_tfidf:
            self._tfidf_indexes[corpus_id].add_document(doc_id, content, metadata)

    async def index_corpus(self, corpus_id: str):
        """为指定语料库建立/重建索引（BM25 + TF-IDF 双索引）"""
        from app.db.crud import get_corpus, get_conversation_history, get_notes
        
        self._bm25_indexes[corpus_id] = BM25Index()
        if self.enable_tfidf:
            self._tfidf_indexes[corpus_id] = TFIDFIndex()
        
        corpus = await get_corpus(corpus_id)
        
        if not corpus:
            return
        
        # 索引锚点故事
        anchors = corpus.get("anchors") or []
        if isinstance(anchors, str):
            try:
                anchors = json.loads(anchors)
            except (json.JSONDecodeError, TypeError):
                anchors = []
        for i, anchor in enumerate(anchors):
            if isinstance(anchor, dict):
                content = f"{anchor.get('label', '')} {anchor.get('story', '')} {' '.join(anchor.get('keywords', []))}"
                self._add_doc_to_indexes(
                    corpus_id, f"anchor_{i}", content,
                    {"type": "anchor", "anchor_id": anchor.get("id", str(i)), "label": anchor.get("label", "")}
                )
        
        # 索引桥接
        bridges = corpus.get("bridges") or []
        if isinstance(bridges, str):
            try:
                bridges = json.loads(bridges)
            except (json.JSONDecodeError, TypeError):
                bridges = []
        for i, bridge in enumerate(bridges):
            if isinstance(bridge, dict):
                content = f"{bridge.get('topic_title', '')} {bridge.get('bridge_sentence', '')} {bridge.get('sample_answer', '')} {bridge.get('category', '')}"
                self._add_doc_to_indexes(
                    corpus_id, f"bridge_{i}", content,
                    {"type": "bridge", "topic_id": bridge.get("topic_id", ""),
                     "category": bridge.get("category", ""), "anchor_id": bridge.get("anchor_id", "")}
                )
        
        # 索引词汇
        vocabulary = corpus.get("vocabulary") or []
        if isinstance(vocabulary, str):
            try:
                vocabulary = json.loads(vocabulary)
            except (json.JSONDecodeError, TypeError):
                vocabulary = []
        for i, vocab in enumerate(vocabulary):
            if isinstance(vocab, dict):
                content = f"{vocab.get('basic_word', '')} {vocab.get('upgrade', '')} {vocab.get('context', '')}"
                self._add_doc_to_indexes(
                    corpus_id, f"vocab_{i}", content,
                    {"type": "vocabulary", "category": vocab.get("category", "")}
                )
        
        # 索引句型
        patterns = corpus.get("patterns") or []
        if isinstance(patterns, str):
            try:
                patterns = json.loads(patterns)
            except (json.JSONDecodeError, TypeError):
                patterns = []
        for i, pattern in enumerate(patterns):
            if isinstance(pattern, dict):
                content = f"{pattern.get('name', '')} {pattern.get('formula', '')} {pattern.get('example', '')} {pattern.get('when_to_use', '')}"
                self._add_doc_to_indexes(
                    corpus_id, f"pattern_{i}", content,
                    {"type": "pattern"}
                )
        
        # 索引对话历史
        conversations = await get_conversation_history(corpus_id, limit=100)
        for conv in conversations:
            if conv.get("role") == "user":
                self._add_doc_to_indexes(
                    corpus_id, f"conv_{conv['id']}", conv["content"],
                    {"type": "conversation", "role": "user"}
                )
        
        # 索引笔记
        notes = await get_notes(corpus_id)
        for note in notes:
            content = f"{note.get('title', '')} {note.get('summary', '')}"
            self._add_doc_to_indexes(
                corpus_id, f"note_{note['id']}", content,
                {"type": "note", "trigger_type": note.get("trigger_type", "")}
            )
        
        logger.info(f"Indexed corpus {corpus_id}: BM25 + TF-IDF dual index built")
    
    def _merge_results(self, bm25_results: list[SearchResult], 
                       tfidf_results: list[SearchResult],
                       top_k: int) -> list[SearchResult]:
        """融合 BM25 和 TF-IDF 检索结果（加权 RRF 融合）"""
        # 使用 Reciprocal Rank Fusion (RRF) 融合排名
        rrf_k = 60  # RRF 常数
        doc_scores: dict[str, float] = defaultdict(float)
        doc_map: dict[str, SearchResult] = {}

        # BM25 排名贡献
        for rank, result in enumerate(bm25_results):
            rrf_score = self.bm25_weight / (rrf_k + rank + 1)
            doc_scores[result.doc_id] += rrf_score
            doc_map[result.doc_id] = result

        # TF-IDF 排名贡献
        for rank, result in enumerate(tfidf_results):
            rrf_score = self.tfidf_weight / (rrf_k + rank + 1)
            doc_scores[result.doc_id] += rrf_score
            if result.doc_id not in doc_map:
                doc_map[result.doc_id] = result

        # 按融合分数排序
        sorted_ids = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)
        
        results = []
        for doc_id in sorted_ids[:top_k]:
            result = doc_map[doc_id]
            # 更新分数为融合分数
            results.append(SearchResult(
                doc_id=result.doc_id,
                doc_type=result.doc_type,
                content=result.content,
                score=doc_scores[doc_id],
                metadata=result.metadata
            ))
        return results

    async def search(self, corpus_id: str, query: str, top_k: int = 5,
                     filters: dict = None) -> list[SearchResult]:
        """QMD 三层检索流程
        
        1. Query Expansion: 用 LLM 扩展查询词（可选）
        2. Multi-signal Retrieval: BM25 + TF-IDF 混合检索
        3. Reranking: 对候选结果重排序（可选）
        
        Args:
            corpus_id: 语料库ID
            query: 用户查询
            top_k: 返回结果数量
            filters: 过滤条件 {"type": "anchor", "category": "hobby"}
            
        Returns:
            排序后的 SearchResult 列表
        """
        # 确保索引存在
        if corpus_id not in self._bm25_indexes:
            await self.index_corpus(corpus_id)
        
        bm25_index = self._bm25_indexes.get(corpus_id)
        if not bm25_index:
            return []
        
        # 构建过滤函数
        filter_fn = None
        if filters:
            def filter_fn(metadata):
                for key, value in filters.items():
                    if key in metadata and metadata[key] != value:
                        return False
                return True
        
        # === Q层: Query Expansion ===
        queries = [query]
        if self.enable_query_expansion:
            try:
                from app.services.qmd_engine import get_qmd_engine
                qmd = get_qmd_engine()
                queries = await qmd.expand_query(query)
                logger.debug(f"Query expanded: {query} -> {queries}")
            except Exception as e:
                logger.warning(f"Query expansion failed: {e}")
                queries = [query]
        
        # === M层: Multi-signal Retrieval ===
        # 多查询 BM25 检索（扩展查询的结果合并）
        retrieval_k = top_k * 3  # 检索更多候选用于重排
        
        all_bm25_results = []
        seen_doc_ids = set()
        for q in queries:
            results = bm25_index.search(q, top_k=retrieval_k, filter_fn=filter_fn)
            for r in results:
                if r.doc_id not in seen_doc_ids:
                    all_bm25_results.append(r)
                    seen_doc_ids.add(r.doc_id)
        
        # TF-IDF 检索
        if self.enable_tfidf and corpus_id in self._tfidf_indexes:
            tfidf_index = self._tfidf_indexes[corpus_id]
            all_tfidf_results = []
            seen_tfidf = set()
            for q in queries:
                results = tfidf_index.search(q, top_k=retrieval_k, filter_fn=filter_fn)
                for r in results:
                    if r.doc_id not in seen_tfidf:
                        all_tfidf_results.append(r)
                        seen_tfidf.add(r.doc_id)
            
            # 融合 BM25 + TF-IDF 结果
            merged = self._merge_results(all_bm25_results, all_tfidf_results, retrieval_k)
        else:
            merged = all_bm25_results[:retrieval_k]
        
        # === D层: Reranking ===
        if self.enable_rerank and len(merged) > top_k:
            try:
                from app.services.qmd_engine import get_qmd_engine
                qmd = get_qmd_engine()
                reranked = await qmd.rerank(query, merged, top_k=top_k)
                return reranked
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")
                return merged[:top_k]
        
        return merged[:top_k]
    
    async def search_fast(self, corpus_id: str, query: str, top_k: int = 5,
                          filters: dict = None) -> list[SearchResult]:
        """快速检索（仅 BM25，跳过 LLM 增强）
        
        用于对延迟敏感的场景（如实时对话中的上下文预取）
        """
        if corpus_id not in self._bm25_indexes:
            await self.index_corpus(corpus_id)
        
        bm25_index = self._bm25_indexes.get(corpus_id)
        if not bm25_index:
            return []
        
        filter_fn = None
        if filters:
            def filter_fn(metadata):
                for key, value in filters.items():
                    if key in metadata and metadata[key] != value:
                        return False
                return True
        
        return bm25_index.search(query, top_k=top_k, filter_fn=filter_fn)

    async def get_context_for_conversation(self, corpus_id: str, 
                                            messages: list[dict],
                                            max_context_tokens: int = 2000) -> str:
        """
        为对话维护提供相关上下文（异步预取模式）
        从最近的用户消息中提取查询，检索相关语料
        
        注：此接口使用快速检索模式（仅 BM25 + TF-IDF），
        避免 LLM 调用引入额外延迟。
        """
        # 提取最近的用户消息作为查询
        user_messages = [m["content"] for m in messages if m.get("role") == "user"]
        if not user_messages:
            return ""
        
        # 用最近2条用户消息组合查询
        query = " ".join(user_messages[-2:])
        
        # 使用快速检索（不触发 LLM query expansion / rerank）
        results = await self.search_fast(corpus_id, query, top_k=5)
        
        if not results:
            return ""
        
        # 组装上下文字符串
        context_parts = []
        total_length = 0
        
        for result in results:
            entry = f"[{result.doc_type}] {result.content[:300]}"
            entry_length = len(entry.split())  # 粗略估计 token
            
            if total_length + entry_length > max_context_tokens:
                break
            
            context_parts.append(entry)
            total_length += entry_length
        
        if not context_parts:
            return ""
        
        return "--- Relevant corpus context ---\n" + "\n\n".join(context_parts) + "\n--- End context ---"
    
    def invalidate(self, corpus_id: str):
        """使指定语料库的索引失效（更新后需重建）"""
        if corpus_id in self._bm25_indexes:
            del self._bm25_indexes[corpus_id]
        if corpus_id in self._tfidf_indexes:
            del self._tfidf_indexes[corpus_id]


# 全局单例
_corpus_rag = None

def get_corpus_rag() -> CorpusRAG:
    global _corpus_rag
    if _corpus_rag is None:
        _corpus_rag = CorpusRAG()
    return _corpus_rag
