import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db, close_db

app = FastAPI(
    title="PersonaLingo API",
    description="AI-Powered Personalized IELTS Speaking Corpus Generator",
    version="2.0.0"
)

# CORS：allow_credentials=True 时不可使用通配 "*"，需显式列出前端来源
# 默认涵盖本地开发端口；可通过环境变量 CORS_ALLOW_ORIGINS 以英文逗号分隔覆盖
_default_origins = [
    "http://localhost:5273",
    "http://127.0.0.1:5273",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
_env_origins = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
_allow_origins = (
    [o.strip() for o in _env_origins.split(",") if o.strip()]
    if _env_origins else _default_origins
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup/Shutdown events
@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


# Routers
from app.routers import questionnaire, corpus, skill, topic, material, conversation, note, settings, distill
app.include_router(questionnaire.router, prefix="/api/questionnaire", tags=["Questionnaire"])
app.include_router(corpus.router, prefix="/api/corpus", tags=["Corpus"])
app.include_router(skill.router, prefix="/api/skills", tags=["Skills"])
app.include_router(topic.router, prefix="/api/topics", tags=["Topics"])
app.include_router(material.router, prefix="/api/materials", tags=["Materials"])
app.include_router(conversation.router)
app.include_router(note.router)
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(distill.router, prefix="/api/distill", tags=["Distill"])


@app.get("/")
async def root():
    return {
        "name": "PersonaLingo API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}
