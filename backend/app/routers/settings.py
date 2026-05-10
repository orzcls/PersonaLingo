"""
Settings 路由 - 管理 LLM 配置、动态获取模型列表、测试连接
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx

from app.config import get_settings, update_settings_runtime

router = APIRouter()


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    openai_base_url: Optional[str] = None
    anthropic_base_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    anthropic_model: Optional[str] = None
    target_score: Optional[str] = None
    search_provider: Optional[str] = None
    search_api_key: Optional[str] = None
    search_base_url: Optional[str] = None
    search_include_date: Optional[bool] = None
    search_max_results: Optional[int] = None
    search_compression: Optional[str] = None
    search_chunk_count: Optional[int] = None
    search_embedding_model: Optional[str] = None
    search_embedding_dim: Optional[int] = None
    search_reranker_model: Optional[str] = None


class ConnectionTest(BaseModel):
    provider: str  # "openai" or "anthropic"
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class SearchTest(BaseModel):
    provider: str  # tavily|exa|examcp|bocha|zhipu|querit|searxng|google|bing|baidu
    api_key: Optional[str] = ""
    base_url: Optional[str] = ""


# === Helper Functions ===

async def fetch_openai_models(base_url: str, api_key: str) -> list[str]:
    """从 OpenAI-compatible API 获取模型列表"""
    if not api_key:
        return []
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{base_url.rstrip('/')}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                # 过滤只保留 chat 模型
                chat_keywords = ["gpt", "chat", "claude", "qwen", "deepseek", "glm", "yi", "mistral", "gemma"]
                chat_models = [m for m in models if any(k in m.lower() for k in chat_keywords)]
                return sorted(chat_models) if chat_models else sorted(models)[:20]
        except Exception:
            pass
    return []


def get_anthropic_models() -> list[str]:
    """Anthropic 不提供 /models 端点，返回已知模型列表"""
    return [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
    ]


# === Helper: Mask API Key ===

def mask_api_key(key: str) -> str:
    """脱敏 API Key：显示前3位 + **** + 后4位"""
    if not key or len(key) < 8:
        return ""
    return key[:3] + "****" + key[-4:]


# === Endpoints ===

@router.get("/")
async def get_current_settings():
    """获取当前所有设置（API Key 脱敏返回）"""
    settings = get_settings()
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "openai_base_url": settings.OPENAI_BASE_URL,
        "anthropic_base_url": settings.ANTHROPIC_BASE_URL,
        "openai_api_key": mask_api_key(settings.OPENAI_API_KEY),
        "anthropic_api_key": mask_api_key(settings.ANTHROPIC_API_KEY),
        "openai_api_key_set": bool(settings.OPENAI_API_KEY),
        "anthropic_api_key_set": bool(settings.ANTHROPIC_API_KEY),
        "openai_model": settings.OPENAI_MODEL,
        "anthropic_model": settings.ANTHROPIC_MODEL,
        "target_score": settings.TARGET_SCORE,
        "search_provider": settings.SEARCH_PROVIDER,
        "search_api_key": mask_api_key(settings.SEARCH_API_KEY),
        "search_api_key_set": bool(settings.SEARCH_API_KEY),
        "search_base_url": settings.SEARCH_BASE_URL,
        "search_include_date": settings.SEARCH_INCLUDE_DATE,
        "search_max_results": settings.SEARCH_MAX_RESULTS,
        "search_compression": settings.SEARCH_COMPRESSION,
        "search_chunk_count": settings.SEARCH_CHUNK_COUNT,
        "search_embedding_model": settings.SEARCH_EMBEDDING_MODEL,
        "search_embedding_dim": settings.SEARCH_EMBEDDING_DIM,
        "search_reranker_model": settings.SEARCH_RERANKER_MODEL,
    }


@router.put("/")
async def update_settings(data: SettingsUpdate):
    """更新设置"""
    update_map = {}
    if data.llm_provider is not None:
        update_map["LLM_PROVIDER"] = data.llm_provider
    if data.openai_base_url is not None:
        update_map["OPENAI_BASE_URL"] = data.openai_base_url
    if data.anthropic_base_url is not None:
        update_map["ANTHROPIC_BASE_URL"] = data.anthropic_base_url
    if data.openai_api_key is not None and data.openai_api_key.strip() and "****" not in data.openai_api_key:
        update_map["OPENAI_API_KEY"] = data.openai_api_key
    if data.anthropic_api_key is not None and data.anthropic_api_key.strip() and "****" not in data.anthropic_api_key:
        update_map["ANTHROPIC_API_KEY"] = data.anthropic_api_key
    if data.openai_model is not None:
        update_map["OPENAI_MODEL"] = data.openai_model
    if data.anthropic_model is not None:
        update_map["ANTHROPIC_MODEL"] = data.anthropic_model
    if data.target_score is not None:
        update_map["TARGET_SCORE"] = data.target_score
    if data.search_provider is not None:
        update_map["SEARCH_PROVIDER"] = data.search_provider
    if data.search_api_key is not None and data.search_api_key.strip() and "****" not in data.search_api_key:
        update_map["SEARCH_API_KEY"] = data.search_api_key
    if data.search_base_url is not None:
        update_map["SEARCH_BASE_URL"] = data.search_base_url
    if data.search_include_date is not None:
        update_map["SEARCH_INCLUDE_DATE"] = data.search_include_date
    if data.search_max_results is not None:
        update_map["SEARCH_MAX_RESULTS"] = data.search_max_results
    if data.search_compression is not None:
        update_map["SEARCH_COMPRESSION"] = data.search_compression
    if data.search_chunk_count is not None:
        update_map["SEARCH_CHUNK_COUNT"] = data.search_chunk_count
    if data.search_embedding_model is not None:
        update_map["SEARCH_EMBEDDING_MODEL"] = data.search_embedding_model
    if data.search_embedding_dim is not None:
        update_map["SEARCH_EMBEDDING_DIM"] = data.search_embedding_dim
    if data.search_reranker_model is not None:
        update_map["SEARCH_RERANKER_MODEL"] = data.search_reranker_model

    if update_map:
        update_settings_runtime(**update_map)

    return {"status": "ok", "message": "Settings updated successfully"}


@router.get("/models")
async def get_available_models():
    """
    根据当前配置的 base_url 和 API key，动态获取可用模型列表
    """
    settings = get_settings()

    # OpenAI models
    openai_models = await fetch_openai_models(
        settings.OPENAI_BASE_URL,
        settings.OPENAI_API_KEY
    )

    # Anthropic models (硬编码已知列表)
    anthropic_models = get_anthropic_models()

    return {
        "openai": {
            "base_url": settings.OPENAI_BASE_URL,
            "models": openai_models,
            "current": settings.OPENAI_MODEL,
            "available": bool(settings.OPENAI_API_KEY)
        },
        "anthropic": {
            "base_url": settings.ANTHROPIC_BASE_URL,
            "models": anthropic_models,
            "current": settings.ANTHROPIC_MODEL,
            "available": bool(settings.ANTHROPIC_API_KEY)
        }
    }


@router.post("/test-connection")
async def test_connection(data: ConnectionTest):
    """测试 API 连接是否有效"""
    settings = get_settings()
    provider = data.provider
    base_url = data.base_url
    api_key = data.api_key

    if provider == "openai":
        base_url = base_url or settings.OPENAI_BASE_URL
        api_key = api_key or settings.OPENAI_API_KEY
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{base_url.rstrip('/')}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    return {"status": "ok", "message": "Connection successful"}
                else:
                    return {"status": "error", "message": f"API returned status {resp.status_code}"}
            except httpx.TimeoutException:
                return {"status": "error", "message": "Connection timed out"}
            except Exception as e:
                return {"status": "error", "message": f"Connection failed: {str(e)}"}

    elif provider == "anthropic":
        base_url = base_url or settings.ANTHROPIC_BASE_URL
        api_key = api_key or settings.ANTHROPIC_API_KEY
        if not api_key:
            raise HTTPException(status_code=400, detail="Anthropic API key not configured")

        async with httpx.AsyncClient() as client:
            try:
                # Anthropic: 尝试发送一个简单请求来验证 key
                # 使用当前配置的模型或 fallback 列表中的第一个
                test_model = settings.ANTHROPIC_MODEL or get_anthropic_models()[0]
                resp = await client.post(
                    f"{base_url.rstrip('/')}/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": test_model,
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "hi"}]
                    },
                    timeout=10
                )
                if resp.status_code in (200, 201):
                    return {"status": "ok", "message": "Connection successful"}
                elif resp.status_code == 401:
                    return {"status": "error", "message": "Invalid API key"}
                else:
                    # Even a 400 with proper error format means connection works
                    try:
                        err = resp.json()
                        if "error" in err:
                            return {"status": "ok", "message": "Connection successful (API key valid)"}
                    except Exception:
                        pass
                    return {"status": "error", "message": f"API returned status {resp.status_code}"}
            except httpx.TimeoutException:
                return {"status": "error", "message": "Connection timed out"}
            except Exception as e:
                return {"status": "error", "message": f"Connection failed: {str(e)}"}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")


# === 网络搜索 Provider ===

@router.get("/search/providers")
async def list_search_providers():
    """返回所有可用的搜索 provider 元信息，按 group 分为 api / local。"""
    from app.services.web_search import get_provider_catalog
    return {"status": "ok", "data": get_provider_catalog()}


@router.get("/search/rag-models")
async def list_search_rag_models():
    """返回 QMD 系统内置/推荐的嵌入模型与重排模型清单。

    前端据此生成下拉菜单，用户无需手动输入模型名。
    QMD 引擎本身是零外部模型（BM25+TF-IDF），下列清单作为
    对接外部向量检索/重排服务时的官方推荐。
    """
    embedding_presets = [
        {
            "id": "",
            "label": "Built-in BM25+TF-IDF",
            "label_cn": "内置 BM25+TF-IDF（推荐，零依赖）",
            "dim": 0,
            "provider": "local",
            "note": "QMD 默认：无需外部 API，毫秒级响应",
        },
        {
            "id": "text-embedding-3-small",
            "label": "OpenAI text-embedding-3-small",
            "label_cn": "OpenAI text-embedding-3-small",
            "dim": 1536,
            "provider": "openai",
            "note": "性价比首选，维度可缩减到 256/512/1024",
        },
        {
            "id": "text-embedding-3-large",
            "label": "OpenAI text-embedding-3-large",
            "label_cn": "OpenAI text-embedding-3-large",
            "dim": 3072,
            "provider": "openai",
            "note": "高精度，维度可缩减到 256/1024/3072",
        },
        {
            "id": "bge-m3",
            "label": "BAAI bge-m3 (multilingual)",
            "label_cn": "BAAI bge-m3（多语言，中英混合首选）",
            "dim": 1024,
            "provider": "hf",
            "note": "多语言 dense+sparse 混合向量",
        },
        {
            "id": "embeddinggemma",
            "label": "Google EmbeddingGemma",
            "label_cn": "Google EmbeddingGemma（轻量 768D）",
            "dim": 768,
            "provider": "hf",
            "note": "轻量本地部署友好",
        },
        {
            "id": "custom",
            "label": "Custom (manual input)",
            "label_cn": "自定义（手动填写）",
            "dim": 0,
            "provider": "custom",
            "note": "输入任意模型 ID",
        },
    ]

    reranker_presets = [
        {
            "id": "",
            "label": "No rerank (QMD LLM-based)",
            "label_cn": "不配置外部重排（默认走 QMD LLM 重排）",
            "provider": "local",
            "note": "QMD D 层已用 LLM 做重排，无需额外模型",
        },
        {
            "id": "bge-reranker-v2-m3",
            "label": "BAAI bge-reranker-v2-m3",
            "label_cn": "BAAI bge-reranker-v2-m3（多语言推荐）",
            "provider": "hf",
            "note": "多语言交叉编码器，对 TopK 片段二次重排",
        },
        {
            "id": "Qwen/Qwen2-Reranker-1.5B",
            "label": "Qwen2-Reranker-1.5B",
            "label_cn": "通义 Qwen2-Reranker-1.5B",
            "provider": "hf",
            "note": "中文场景更强，资源占用中等",
        },
        {
            "id": "custom",
            "label": "Custom (manual input)",
            "label_cn": "自定义（手动填写）",
            "provider": "custom",
            "note": "输入任意重排模型 ID",
        },
    ]

    settings = get_settings()
    return {
        "status": "ok",
        "data": {
            "embedding_presets": embedding_presets,
            "reranker_presets": reranker_presets,
            "current": {
                "embedding_model": settings.SEARCH_EMBEDDING_MODEL,
                "embedding_dim": settings.SEARCH_EMBEDDING_DIM,
                "reranker_model": settings.SEARCH_RERANKER_MODEL,
            },
        },
    }


@router.post("/search/test")
async def test_search_connection(data: SearchTest):
    """测试搜索 provider 连接。如果 api_key 含 *** 掩码，则回退到设置中的真实 Key。"""
    from app.services.web_search import test_search
    settings = get_settings()
    api_key = (data.api_key or "").strip()
    base_url = (data.base_url or "").strip()
    if "***" in api_key or not api_key:
        api_key = settings.SEARCH_API_KEY
    if not base_url:
        base_url = settings.SEARCH_BASE_URL
    return await test_search(data.provider, api_key, base_url)
