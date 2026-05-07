import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.models.questionnaire import (
    MBTIQuestion,
    QuestionnaireSubmission,
    QuestionnaireResponse,
)
from app.services.mbti_analyzer import MBTIAnalyzer
from app.storage import questionnaire_store

router = APIRouter(prefix="/questionnaire", tags=["问卷系统"])

# 实例化 MBTI 分析器
mbti_analyzer = MBTIAnalyzer()

# 预设兴趣标签列表
INTEREST_TAGS = [
    "Photography", "Music", "Coding", "Gaming", "Reading",
    "Travel", "Sports", "Cooking", "Art", "Film",
    "Nature", "Writing", "Dance", "Fitness", "Technology",
    "Science", "History", "Philosophy", "Fashion", "Animals"
]


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


@router.get("/interest-tags", response_model=list[str])
async def get_interest_tags():
    """获取可选的兴趣标签列表"""
    return INTEREST_TAGS


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

    # 生成唯一 ID 和时间戳
    questionnaire_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    # 构建存储数据
    record = {
        "id": questionnaire_id,
        "mbti_result": mbti_result,
        "interests": {
            "tags": submission.interests.tags,
            "descriptions": submission.interests.descriptions,
        },
        "ielts": {
            "topic_types": submission.ielts.topic_types,
            "target_score": submission.ielts.target_score,
            "exam_date": submission.ielts.exam_date,
        },
        "created_at": created_at,
    }

    # 存入内存
    questionnaire_store[questionnaire_id] = record

    return QuestionnaireResponse(**record)
