from fastapi import APIRouter
from app.models.corpus import PersonalCorpus, AnchorStory, BridgeResponse, VocabularyUpgrade, SentencePattern
from datetime import datetime

router = APIRouter(prefix="/corpus", tags=["语料生成"])


@router.post("/generate")
async def generate_corpus(user_profile: dict):
    """根据用户画像生成个性化语料库"""
    # Placeholder：返回示例语料库
    return {
        "status": "success",
        "message": "语料库生成中",
        "data": {
            "corpus_id": "corpus_placeholder_001",
            "user_profile": user_profile,
            "anchors": [
                {
                    "id": "anchor_1",
                    "title": "大学编程竞赛经历",
                    "description": "参加 ICPC 竞赛的经历让我学会了团队协作和高压下思考",
                    "keywords": ["teamwork", "problem-solving", "competition"],
                }
            ],
            "bridges": [
                {
                    "topic": "Describe a challenge you faced",
                    "anchor_id": "anchor_1",
                    "bridge_sentence": "Speaking of challenges, one that immediately comes to mind is...",
                    "sample_answer": "One of the most significant challenges I've faced was during a programming competition...",
                }
            ],
            "vocabulary": [
                {
                    "basic_word": "difficult",
                    "advanced_alternatives": ["daunting", "formidable", "arduous"],
                    "context": "Describing challenges and obstacles",
                }
            ],
            "patterns": [
                {
                    "pattern_name": "Personal Anecdote Opener",
                    "template": "One experience that really shaped my perspective on [TOPIC] was when I [EVENT].",
                    "example": "One experience that really shaped my perspective on teamwork was when I participated in ICPC.",
                    "usage_context": "Part 2 长回答开头",
                }
            ],
            "created_at": datetime.now().isoformat(),
        },
    }


@router.get("/{corpus_id}")
async def get_corpus(corpus_id: str):
    """获取指定语料库详情"""
    # Placeholder
    return {
        "status": "success",
        "data": {
            "id": corpus_id,
            "user_profile": {"mbti": "INFP", "interests": ["technology", "travel"]},
            "anchors": [],
            "bridges": [],
            "vocabulary": [],
            "patterns": [],
            "created_at": datetime.now().isoformat(),
        },
    }
