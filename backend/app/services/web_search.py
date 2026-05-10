"""
通用 Web 搜索服务抽象层（对标 CherryStudio 的多 provider 集成）

两类 provider：
- API 服务商（7 个，需 Key 或 Base URL）：Tavily / Exa / ExaMCP / Bocha / Zhipu / Querit / Searxng
- 本地搜索（3 个，免 Key，通过 r.jina.ai 代理抓 HTML SERP）：Google / Bing / Baidu

所有 provider 统一返回 [{"url", "title", "snippet", "published_at"?}]
"""
from typing import Optional
import re
import html
import httpx
import urllib.parse

from app.config import get_settings


# ================= Provider 元信息 =================

PROVIDER_CATALOG = [
    # ---- API 服务商 ----
    {
        "id": "tavily", "name": "Tavily", "group": "api",
        "description": "专为 AI 优化的搜索 API，返回高质量正文片段",
        "key_required": True, "base_url_required": False,
        "api_key_url": "https://tavily.com",
    },
    {
        "id": "exa", "name": "Exa", "group": "api",
        "description": "神经网络驱动的语义搜索引擎",
        "key_required": True, "base_url_required": False,
        "api_key_url": "https://exa.ai",
    },
    {
        "id": "examcp", "name": "ExaMCP", "group": "api",
        "description": "通过 MCP 端点访问 Exa，可配置 Base URL",
        "key_required": True, "base_url_required": True,
        "api_key_url": "https://exa.ai",
    },
    {
        "id": "bocha", "name": "Bocha 博查", "group": "api",
        "description": "国内 AI 搜索 API，中英文双语支持",
        "key_required": True, "base_url_required": False,
        "api_key_url": "https://bochaai.com",
    },
    {
        "id": "zhipu", "name": "Zhipu 智谱", "group": "api",
        "description": "智谱 AI web_search 工具接口",
        "key_required": True, "base_url_required": False,
        "api_key_url": "https://open.bigmodel.cn",
    },
    {
        "id": "querit", "name": "Querit", "group": "api",
        "description": "Querit 搜索 API，面向 AI 场景的检索服务",
        "key_required": True, "base_url_required": False,
        "api_key_url": "https://querit.io",
    },
    {
        "id": "searxng", "name": "SearXNG (自部署)", "group": "api",
        "description": "开源元搜索引擎，需自部署实例并填写 Base URL",
        "key_required": False, "base_url_required": True,
        "api_key_url": "https://docs.searxng.org",
    },
    # ---- 本地搜索（免 Key，抓 HTML SERP）----
    {
        "id": "google", "name": "Google", "group": "local",
        "description": "免 Key，通过 r.jina.ai 代理抓取 Google SERP",
        "key_required": False, "base_url_required": False,
        "api_key_url": "",
    },
    {
        "id": "bing", "name": "Bing", "group": "local",
        "description": "免 Key，通过 r.jina.ai 代理抓取 Bing SERP",
        "key_required": False, "base_url_required": False,
        "api_key_url": "",
    },
    {
        "id": "baidu", "name": "Baidu", "group": "local",
        "description": "免 Key，通过 r.jina.ai 代理抓取百度 SERP",
        "key_required": False, "base_url_required": False,
        "api_key_url": "",
    },
]


def get_provider_catalog() -> list[dict]:
    return PROVIDER_CATALOG


# ================= Provider 基类 =================

class WebSearchProvider:
    provider_id: str = ""

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        raise NotImplementedError


# ================= API 服务商实现 =================

class TavilyProvider(WebSearchProvider):
    provider_id = "tavily"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": top_k,
                    "search_depth": "basic",
                    "include_answer": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "url": it.get("url", ""),
                    "title": it.get("title", ""),
                    "snippet": it.get("content", ""),
                    "published_at": it.get("published_date", "") if include_date else "",
                }
                for it in data.get("results", [])
            ]


class ExaProvider(WebSearchProvider):
    provider_id = "exa"
    endpoint = "https://api.exa.ai/search"

    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key
        if base_url:
            self.endpoint = base_url.rstrip("/") + "/search"

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                self.endpoint,
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "numResults": top_k,
                    "type": "neural",
                    "contents": {"text": {"maxCharacters": 500}},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for it in data.get("results", []):
                text = it.get("text", "")
                results.append({
                    "url": it.get("url", ""),
                    "title": it.get("title", ""),
                    "snippet": text[:500] if text else "",
                    "published_at": it.get("publishedDate", "") if include_date else "",
                })
            return results


class ExaMCPProvider(ExaProvider):
    """通过 MCP 端点访问 Exa（Base URL 必填）"""
    provider_id = "examcp"

    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key, base_url)


class BochaProvider(WebSearchProvider):
    provider_id = "bocha"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.bochaai.com/v1/web-search",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"query": query, "summary": True, "count": top_k},
            )
            resp.raise_for_status()
            data = resp.json()
            pages = data.get("data", {}).get("webPages", {}).get("value", [])
            return [
                {
                    "url": it.get("url", ""),
                    "title": it.get("name", ""),
                    "snippet": it.get("summary") or it.get("snippet", ""),
                    "published_at": it.get("datePublished", "") if include_date else "",
                }
                for it in pages
            ]


class ZhipuProvider(WebSearchProvider):
    """智谱 web_search_pro 工具接口"""
    provider_id = "zhipu"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/tools",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "tool": "web-search-pro",
                    "messages": [{"role": "user", "content": query}],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for choice in data.get("choices", []):
                msg = choice.get("message", {})
                for tc in msg.get("tool_calls", []):
                    for r in tc.get("search_result", [])[:top_k]:
                        results.append({
                            "url": r.get("link", ""),
                            "title": r.get("title", ""),
                            "snippet": r.get("content", ""),
                            "published_at": r.get("publish_time", "") if include_date else "",
                        })
            return results[:top_k]


class QueritProvider(WebSearchProvider):
    provider_id = "querit"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.querit.io/v1/search",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"query": query, "num_results": top_k},
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "url": it.get("url", ""),
                    "title": it.get("title", ""),
                    "snippet": it.get("snippet") or it.get("content", ""),
                    "published_at": it.get("published_at", "") if include_date else "",
                }
                for it in data.get("results", [])[:top_k]
            ]


class SearxngProvider(WebSearchProvider):
    provider_id = "searxng"

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{self.base_url}/search",
                params={"q": query, "format": "json"},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "url": it.get("url", ""),
                    "title": it.get("title", ""),
                    "snippet": it.get("content", ""),
                    "published_at": it.get("publishedDate", "") if include_date else "",
                }
                for it in data.get("results", [])[:top_k]
            ]


# ================= 本地搜索（HTML SERP 抓取）=================

_JINA_PROXY = "https://r.jina.ai/"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


async def _fetch_serp_text(serp_url: str) -> str:
    """先走 r.jina.ai 代理取纯文本；失败降级为 httpx 直接 GET HTML"""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(_JINA_PROXY + serp_url, headers={"User-Agent": _UA})
            if resp.status_code == 200 and resp.text:
                return resp.text
    except Exception:
        pass
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(serp_url, headers={"User-Agent": _UA})
            return resp.text if resp.status_code == 200 else ""
    except Exception:
        return ""


# r.jina.ai 返回的是 Markdown：正常链接形如 [标题](url)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")


def _parse_markdown_results(text: str, top_k: int, exclude_hosts: tuple) -> list[dict]:
    seen = set()
    out = []
    for m in _MD_LINK_RE.finditer(text):
        title = html.unescape(m.group(1)).strip()
        url = m.group(2).strip()
        if not title or not url:
            continue
        host = urllib.parse.urlparse(url).netloc.lower()
        if any(h in host for h in exclude_hosts):
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append({"url": url, "title": title, "snippet": "", "published_at": ""})
        if len(out) >= top_k:
            break
    return out


class GoogleProvider(WebSearchProvider):
    provider_id = "google"

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        q = urllib.parse.quote_plus(query)
        text = await _fetch_serp_text(f"https://www.google.com/search?q={q}&num={top_k * 2}")
        return _parse_markdown_results(text, top_k, exclude_hosts=("google.com", "gstatic.com", "googleusercontent.com"))


class BingProvider(WebSearchProvider):
    provider_id = "bing"

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        q = urllib.parse.quote_plus(query)
        text = await _fetch_serp_text(f"https://www.bing.com/search?q={q}&count={top_k * 2}")
        return _parse_markdown_results(text, top_k, exclude_hosts=("bing.com", "microsoft.com", "msn.com"))


class BaiduProvider(WebSearchProvider):
    provider_id = "baidu"

    async def search(self, query: str, top_k: int = 8, include_date: bool = True) -> list[dict]:
        q = urllib.parse.quote_plus(query)
        text = await _fetch_serp_text(f"https://www.baidu.com/s?wd={q}&rn={top_k * 2}")
        return _parse_markdown_results(text, top_k, exclude_hosts=("baidu.com",))


# ================= 工厂与测试 =================

def _build_provider(provider_id: str, api_key: str, base_url: str) -> Optional[WebSearchProvider]:
    pid = (provider_id or "").strip().lower()
    if not pid:
        return None
    # API 服务商
    if pid == "tavily" and api_key:
        return TavilyProvider(api_key)
    if pid == "exa" and api_key:
        return ExaProvider(api_key)
    if pid == "examcp" and api_key and base_url:
        return ExaMCPProvider(api_key, base_url)
    if pid == "bocha" and api_key:
        return BochaProvider(api_key)
    if pid == "zhipu" and api_key:
        return ZhipuProvider(api_key)
    if pid == "querit" and api_key:
        return QueritProvider(api_key)
    if pid == "searxng" and base_url:
        return SearxngProvider(base_url, api_key)
    # 本地搜索（免 Key）
    if pid == "google":
        return GoogleProvider()
    if pid == "bing":
        return BingProvider()
    if pid == "baidu":
        return BaiduProvider()
    return None


def get_web_search() -> Optional[WebSearchProvider]:
    """按当前配置返回搜索 provider 实例；未配置或必备字段缺失返回 None"""
    settings = get_settings()
    return _build_provider(
        settings.SEARCH_PROVIDER,
        settings.SEARCH_API_KEY.strip(),
        settings.SEARCH_BASE_URL.strip(),
    )


async def test_search(provider_id: str, api_key: str = "", base_url: str = "") -> dict:
    """测试搜索连接（用于设置页测试按钮）"""
    import time
    pid = (provider_id or "").lower()
    provider = _build_provider(pid, api_key or "", base_url or "")
    if provider is None:
        return {"status": "error", "message": "缺少 API Key 或 Base URL"}
    try:
        t0 = time.time()
        results = await provider.search("IELTS speaking test", top_k=3, include_date=True)
        elapsed = round((time.time() - t0) * 1000)
        return {
            "status": "ok",
            "message": f"连接成功，返回 {len(results)} 条结果（{elapsed}ms）",
            "elapsed_ms": elapsed,
            "result_count": len(results),
            "sample_results": results[:3],
        }
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"连接失败: {str(e)}"}
