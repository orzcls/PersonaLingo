from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置管理"""

    # OpenAI / LLM 配置
    OPENAI_API_KEY: str = "your-api-key-here"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    MODEL_NAME: str = "gpt-4o"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./personalingo.db"

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """将逗号分隔的 CORS_ORIGINS 字符串转为列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# 全局配置实例
settings = Settings()
