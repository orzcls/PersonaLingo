from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import questionnaire, corpus, skill

app = FastAPI(
    title="PersonaLingo API",
    description="基于 MBTI 性格分析的雅思口语个性化语料库生成系统",
    version="0.1.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(questionnaire.router, prefix="/api")
app.include_router(corpus.router, prefix="/api")
app.include_router(skill.router, prefix="/api")


@app.get("/", tags=["默认"])
async def root():
    """根路由 - 欢迎信息"""
    return {
        "message": "Welcome to PersonaLingo API",
        "description": "基于 MBTI 性格分析的雅思口语个性化语料库生成系统",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["默认"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "PersonaLingo API",
        "version": "0.1.0",
    }
