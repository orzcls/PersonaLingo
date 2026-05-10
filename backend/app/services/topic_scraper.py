"""
IELTS 题源抓取与 RAG 抽取流水线

流程：
    [搜索 provider] → [Jina Reader 抓正文] → [BM25+TF-IDF 临时索引] → [LLM 结构化抽取]

输出：{"p1": [...], "p2": [...], "source_urls": {...}}
"""
import asyncio
import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Optional

import httpx

from app.config import get_settings
from app.services.web_search import get_web_search
from app.services.corpus_rag import BM25Index, TFIDFIndex, tokenize

logger = logging.getLogger(__name__)

JINA_READER = "https://r.jina.ai/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# 优先抓取的可靠 IELTS 题源站点
PREFERRED_DOMAINS = (
    "ieltsliz.com", "ielts-mentor.com", "dcielts.com", "ielts-simulation.com",
    "ieltsadvantage.com", "ielts-exam.net", "takeielts.britishcouncil.org",
    "ieltspodcast.com", "ielts-up.com",
)

# 系统核心 6 类 + 扩展类，与前端 TopicFilter.vue 严格对齐（person 单数）
VALID_CATEGORIES = [
    "hobby_leisure", "person", "place", "event", "object",
    "abstract", "technology", "education", "society", "health",
    "environment", "media",
]


# ================= 季度计算 =================

def get_current_season() -> str:
    """与后端一致的季度计算：IELTS 3 季 = Jan-Apr / May-Aug / Sep-Dec"""
    now = datetime.now()
    quarter = (now.month - 1) // 4 + 1
    return f"{now.year}-Q{quarter}"


# ================= 查询构造 =================

def build_queries(season: str, part: str) -> list[str]:
    """为指定 part 构造多条搜索查询"""
    year = season.split("-")[0]
    if part == "P1":
        return [
            f"IELTS speaking Part 1 new questions {season}",
            f"IELTS Part 1 latest topics {year}",
            f"IELTS speaking Part 1 sample questions {season}",
        ]
    if part == "P2":
        return [
            f"IELTS speaking Part 2 cue card {season}",
            f"latest IELTS Part 2 topics {year}",
            f"IELTS Part 2 describe cue card {season}",
        ]
    if part == "P3":
        return [
            f"IELTS speaking Part 3 follow-up questions {season}",
            f"IELTS Part 3 discussion topics {year}",
        ]
    return []


# ================= 抓取正文 =================

async def fetch_page(url: str, client: httpx.AsyncClient) -> str:
    """先走 r.jina.ai 代理；失败降级 httpx 直连"""
    try:
        resp = await client.get(JINA_READER + url, headers={"User-Agent": UA}, timeout=15)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception as e:
        logger.debug(f"jina reader failed for {url}: {e}")
    try:
        resp = await client.get(url, headers={"User-Agent": UA}, timeout=15, follow_redirects=True)
        if resp.status_code == 200:
            # 简单 strip HTML
            text = re.sub(r"<script[\s\S]*?</script>", " ", resp.text)
            text = re.sub(r"<style[\s\S]*?</style>", " ", text)
            text = re.sub(r"<[^>]+>", " ", text)
            return text
    except Exception as e:
        logger.debug(f"httpx fallback failed for {url}: {e}")
    return ""


# ================= 源 URL 缓存检查 =================

async def _is_cached(url: str, content_hash: str) -> bool:
    from app.database import get_db
    db = await get_db()
    cursor = await db.execute(
        "SELECT content_hash FROM topic_sources WHERE url = ?", (url,)
    )
    row = await cursor.fetchone()
    return row is not None and row[0] == content_hash


async def _save_source(url: str, title: str, content_hash: str, season: str):
    from app.database import get_db
    db = await get_db()
    await db.execute(
        """INSERT OR REPLACE INTO topic_sources (url, title, content_hash, season, fetched_at)
           VALUES (?, ?, ?, ?, ?)""",
        (url, title, content_hash, season, datetime.now().isoformat()),
    )
    await db.commit()


# ================= 文档切片 + 临时 RAG 索引 =================

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """简单按字符数切片，保留段落边界感"""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # 尝试回退到最近的句号
        if end < len(text):
            last_dot = text.rfind(".", start, end)
            if last_dot > start + chunk_size // 2:
                end = last_dot + 1
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def build_temp_index(docs: list[dict]) -> tuple[BM25Index, TFIDFIndex]:
    """为本次抓到的文档构建临时 BM25+TF-IDF 索引。
    docs: [{"id": str, "content": str, "url": str}]
    """
    bm = BM25Index()
    tf = TFIDFIndex()
    for d in docs:
        bm.add_document(d["id"], d["content"], {"url": d["url"]})
        tf.add_document(d["id"], d["content"], {"url": d["url"]})
    return bm, tf


def retrieve_context(bm: BM25Index, tf: TFIDFIndex, query: str, top_k: int = 6) -> list[dict]:
    """合并 BM25 + TF-IDF 结果作为 LLM context"""
    bm_hits = bm.search(query, top_k=top_k)
    tf_hits = tf.search(query, top_k=top_k)
    seen = set()
    out = []
    for r in bm_hits + tf_hits:
        if r.doc_id in seen:
            continue
        seen.add(r.doc_id)
        out.append({"content": r.content, "url": r.metadata.get("url", ""), "score": r.score})
        if len(out) >= top_k:
            break
    return out


# ================= LLM 抽取 =================

EXTRACT_SYSTEM = (
    "You extract real IELTS speaking topics ONLY from the provided context. "
    "Strictly forbidden to invent topics that are not clearly present in the context. "
    "Return valid JSON array only, no markdown fences."
)


def _build_extract_prompt(part: str, season: str, chunks: list[dict]) -> str:
    context_block = "\n\n".join(
        f"[{i+1}] (url: {c['url']})\n{c['content'][:1500]}"
        for i, c in enumerate(chunks)
    )
    category_list = ", ".join(VALID_CATEGORIES)
    if part == "P1":
        part_rule = "P1 topics are short everyday topics with 3-4 simple questions each."
    elif part == "P2":
        part_rule = "P2 topics are 'Describe a ...' cue cards; put the 4 cue-card bullets into 'questions'."
    else:
        part_rule = "P3 topics are abstract discussion sets with 3-4 follow-up questions each."

    return f"""Extract IELTS {part} speaking topics for season {season}.

{part_rule}

Rules:
- Only include topics that ACTUALLY APPEAR in the context below. Do NOT invent.
- If no real topics are present, return [].
- Each topic must include: part, title, questions (string[]), category (one of: {category_list}), difficulty (easy|medium|hard), source_url (best-matching url from the context).
- Set season to "{season}" for every item.
- Return ONLY a JSON array. No markdown, no explanation.

Context:
{context_block}
"""


async def _llm_extract(part: str, season: str, chunks: list[dict]) -> list[dict]:
    from app.services.llm_adapter import get_llm
    llm = get_llm()
    if not chunks:
        return []
    try:
        resp = await llm.chat(
            [
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": _build_extract_prompt(part, season, chunks)},
            ],
            temperature=0.2,
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
        items = json.loads(raw)
        if not isinstance(items, list):
            return []
        cleaned = []
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("part") != part:
                it["part"] = part
            if not it.get("title") or not isinstance(it.get("questions"), list):
                continue
            if it.get("category") not in VALID_CATEGORIES:
                it["category"] = "abstract"
            if it.get("difficulty") not in ("easy", "medium", "hard"):
                it["difficulty"] = {"P1": "easy", "P2": "medium", "P3": "hard"}[part]
            it["season"] = season
            it.setdefault("is_new", True)
            it.setdefault("source", "web_scraped")
            cleaned.append(it)
        return cleaned
    except json.JSONDecodeError as e:
        logger.warning(f"LLM extract JSON decode failed for {part}: {e}")
        return []
    except Exception as e:
        logger.warning(f"LLM extract failed for {part}: {e}")
        return []


# ================= 主流水线 =================

def _sort_urls(urls: list[str]) -> list[str]:
    """优先常见 IELTS 站点"""
    def rank(u: str) -> int:
        for i, d in enumerate(PREFERRED_DOMAINS):
            if d in u:
                return i
        return len(PREFERRED_DOMAINS)
    return sorted(urls, key=rank)


async def scrape_topics_pipeline(
    season: Optional[str] = None,
    parts: tuple = ("P1", "P2"),
    max_urls: int = 10,
) -> dict:
    """端到端：搜索 → 抓取 → 索引 → LLM 抽取

    返回 {"season", "by_part": {P1: [...], P2: [...]}, "source_urls": [...], "errors": [...]}"""
    settings = get_settings()
    season = season or get_current_season()

    # 0. 校验搜索 provider
    searcher = get_web_search()
    if searcher is None:
        return {
            "season": season,
            "by_part": {p: [] for p in parts},
            "source_urls": [],
            "errors": ["未配置搜索服务，请在 设置 → 网络搜索 配置 Provider"],
        }

    errors: list[str] = []

    # 1. 收集 URL
    url_set: dict[str, str] = {}  # url -> title
    top_k_each = max(3, settings.SEARCH_MAX_RESULTS // 3)
    for part in parts:
        for q in build_queries(season, part):
            try:
                hits = await searcher.search(q, top_k=top_k_each, include_date=settings.SEARCH_INCLUDE_DATE)
            except Exception as e:
                errors.append(f"search failed [{q}]: {e}")
                continue
            for h in hits:
                url = (h.get("url") or "").strip()
                if url and url not in url_set:
                    url_set[url] = h.get("title") or ""
    if not url_set:
        return {
            "season": season,
            "by_part": {p: [] for p in parts},
            "source_urls": [],
            "errors": errors + ["搜索未返回任何 URL"],
        }

    # 2. 优先级 + 截断 + 并发抓取
    urls = _sort_urls(list(url_set.keys()))[:max_urls]
    docs: list[dict] = []
    async with httpx.AsyncClient() as client:
        pages = await asyncio.gather(*(fetch_page(u, client) for u in urls), return_exceptions=True)
    for url, text in zip(urls, pages):
        if isinstance(text, Exception) or not text or len(text) < 200:
            continue
        content_hash = hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()
        try:
            await _save_source(url, url_set.get(url, ""), content_hash, season)
        except Exception as e:
            logger.debug(f"save source failed: {e}")
        for i, ck in enumerate(chunk_text(text)):
            docs.append({"id": f"{url}#{i}", "content": ck, "url": url})

    if not docs:
        return {
            "season": season,
            "by_part": {p: [] for p in parts},
            "source_urls": urls,
            "errors": errors + ["抓取全部失败或内容过短"],
        }

    # 3. 临时 RAG 索引
    bm, tf = build_temp_index(docs)

    # 4. 按 part 检索 + LLM 抽取
    chunk_count = max(2, min(settings.SEARCH_CHUNK_COUNT * 2, 10))
    by_part: dict[str, list[dict]] = {}
    for part in parts:
        part_queries = build_queries(season, part)
        merged_chunks: list[dict] = []
        seen_ids = set()
        for q in part_queries:
            for item in retrieve_context(bm, tf, q, top_k=chunk_count):
                key = item["url"] + "::" + item["content"][:80]
                if key in seen_ids:
                    continue
                seen_ids.add(key)
                merged_chunks.append(item)
        # 若启用 truncate 策略，按 chunk_count 截断；rag 则保留合并结果
        if settings.SEARCH_COMPRESSION == "truncate":
            merged_chunks = merged_chunks[:chunk_count]
        elif settings.SEARCH_COMPRESSION == "none":
            merged_chunks = merged_chunks[: chunk_count * 2]
        extracted = await _llm_extract(part, season, merged_chunks)
        by_part[part] = extracted

    return {
        "season": season,
        "by_part": by_part,
        "source_urls": urls,
        "errors": errors,
    }
