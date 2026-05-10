from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # pydantic-settings v2 写法：允许 .env 中存在未映射到 Settings 的变量（如 CORS_ALLOW_ORIGINS 由 main.py 直接读取）
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"  # 可自定义为任何 OpenAI-compatible 地址
    OPENAI_MODEL: str = ""  # 用户从模型列表选择

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"  # Anthropic API 地址
    ANTHROPIC_MODEL: str = ""  # 用户从模型列表选择

    # Web Search Provider （用于题库动态更新，对标 CherryStudio 设置布局）
    # Provider id: tavily|exa|examcp|bocha|zhipu|querit|searxng|google|bing|baidu
    SEARCH_PROVIDER: str = ""
    SEARCH_API_KEY: str = ""
    SEARCH_BASE_URL: str = ""  # searxng / examcp 自部署地址
    # 常规设置（对应 CherryStudio 截图“常规设置”）
    SEARCH_INCLUDE_DATE: bool = True   # 搜索包含日期
    SEARCH_MAX_RESULTS: int = 20       # 搜索结果个数：1/5/20/50/100
    # 搜索结果压缩（对应 CherryStudio 截图“搜索结果压缩”）
    SEARCH_COMPRESSION: str = "rag"    # rag | truncate | none
    SEARCH_CHUNK_COUNT: int = 3        # 文档片段数量 1–10
    # QMD 可选增强（对标 CherryStudio：嵌入模型 / 嵌入维度 / 重排模型）
    # 留空时 qmd_engine 自动回退到 BM25+TF-IDF 纯本地实现
    SEARCH_EMBEDDING_MODEL: str = ""   # e.g. text-embedding-3-small / bge-m3
    SEARCH_EMBEDDING_DIM: int = 0      # 0 表示自动探测
    SEARCH_RERANKER_MODEL: str = ""    # e.g. bge-reranker-v2-m3

    # Database
    DB_PATH: str = "app/data/personalingo.db"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 9849

    # App
    APP_NAME: str = "PersonaLingo"
    DEBUG: bool = False

    # Target Score
    TARGET_SCORE: str = "7.0"

    # Distill Pipeline (三段式蒸馏)
    DISTILL_RESEARCH_WEB_SEARCH: bool = False  # Stage 1 是否调用 web_search 做深度调研(默认关闭)
    SKILL_RUNNABLE_OUT_ROOT: str = ""          # 可运行 Skill 包输出根路径;留空则默认为 <repo>/skills/runnable/



_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def update_settings_runtime(**kwargs):
    """运行时更新设置（不持久化到 .env）"""
    global _settings
    settings = get_settings()
    for key, value in kwargs.items():
        if hasattr(settings, key):
            object.__setattr__(settings, key, value)
    return settings
