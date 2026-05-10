from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.models.questionnaire import (
    MBTIQuestion,
    QuestionnaireSubmission,
    QuestionnaireResponse,
    InterestTag,
)
from app.services.mbti_analyzer import MBTIAnalyzer
from app.db.crud import create_questionnaire, get_questionnaire

router = APIRouter(tags=["Questionnaire"])

# 实例化 MBTI 分析器
mbti_analyzer = MBTIAnalyzer()

# 预设兴趣标签列表（按分类）
INTEREST_TAGS = {
    "creative": ["Photography", "Music", "Art", "Writing", "Film", "Dance"],
    "tech": ["Coding", "AIGC", "Gaming", "Technology", "Science"],
    "lifestyle": ["Travel", "Cooking", "Reading", "Fitness", "Fashion"],
    "nature": ["Nature", "Animals", "Gardening", "Hiking", "Stargazing"],
    "social": ["Volunteering", "Sports", "Board Games", "Table Tennis", "Piano"]
}

# 人/物/地预设分类
RELATIONSHIP_TYPES = ["挚友", "对象", "家人", "导师", "同学", "室友", "宠物"]
OBJECT_CATEGORIES = ["乐器", "书", "宠物", "车", "礼物", "收藏品", "电子设备", "运动器材"]
PLACE_CATEGORIES = ["山水名胜", "国家/城市", "博物馆", "公园", "校园", "餐厅/咖啡店", "旅行目的地"]


@router.get("/mbti-questions")
async def get_mbti_questions():
    """获取 MBTI 测试题目列表 + 16种类型列表（支持直接选择）"""
    questions = mbti_analyzer.get_questions()
    type_list = [
        {"code": code, "description": desc}
        for code, desc in mbti_analyzer.TYPE_DESCRIPTIONS.items()
    ]
    return {
        "questions": questions,
        "types": type_list,
    }


@router.get("/interest-tags")
async def get_interest_tags():
    """获取可选的兴趣标签列表（按分类）"""
    return {
        "tags": INTEREST_TAGS,
        "relationship_types": RELATIONSHIP_TYPES,
        "object_categories": OBJECT_CATEGORIES,
        "place_categories": PLACE_CATEGORIES,
    }


@router.post("/submit", response_model=QuestionnaireResponse)
async def submit_questionnaire(submission: QuestionnaireSubmission):
    """提交完整问卷数据，验证并存储，返回 questionnaire_id"""

    # 处理 MBTI 部分
    if submission.mbti.mode == "test":
        if not submission.mbti.answers:
            raise HTTPException(status_code=400, detail="Test mode requires answers")
        mbti_result = mbti_analyzer.analyze(submission.mbti.answers)
    elif submission.mbti.mode == "direct":
        if not submission.mbti.type_code:
            raise HTTPException(status_code=400, detail="Direct mode requires type_code")
        type_code = submission.mbti.type_code.upper()
        if type_code not in mbti_analyzer.TYPE_DESCRIPTIONS:
            raise HTTPException(status_code=400, detail=f"Invalid MBTI type: {type_code}")
        mbti_result = mbti_analyzer.get_type_info(type_code)
    else:
        raise HTTPException(status_code=400, detail="Invalid mbti mode, must be 'test' or 'direct'")

    # 持久化到 SQLite（字段结构与 corpus_generator 读取约定一致）
    db_payload = {
        "mbti_type": mbti_result.get("type_code", ""),
        "mbti_dimensions": mbti_result.get("dimensions", {}),
        "interests_tags": [tag.name for tag in submission.interests.tags],
        "interests_descriptions": submission.interests.descriptions,
        "ielts_target_score": submission.ielts.target_score,
        "ielts_topic_types": submission.ielts.topic_types,
        "ielts_exam_date": submission.ielts.exam_date or "",
        "personal_background": submission.personal_background.model_dump() if submission.personal_background else None,
        "life_experiences": submission.life_experiences.model_dump() if submission.life_experiences else None,
    }
    questionnaire_id = await create_questionnaire(db_payload)
    created_at = datetime.now(timezone.utc).isoformat()

    return QuestionnaireResponse(
        id=questionnaire_id,
        mbti_result=mbti_result,
        interests={
            "tags": [tag.model_dump() for tag in submission.interests.tags],
            "descriptions": submission.interests.descriptions,
        },
        ielts={
            "topic_types": submission.ielts.topic_types,
            "target_score": submission.ielts.target_score,
            "exam_date": submission.ielts.exam_date,
        },
        personal_background=submission.personal_background.model_dump() if submission.personal_background else None,
        life_experiences=submission.life_experiences.model_dump() if submission.life_experiences else None,
        created_at=created_at,
    )
