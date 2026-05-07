from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MBTIQuestion(BaseModel):
    """单道 MBTI 题目模型"""
    id: int
    dimension: str
    question: str
    option_a: str
    option_b: str


class MBTISubmission(BaseModel):
    """MBTI 提交数据"""
    mode: str  # "test" or "direct"
    answers: Optional[dict] = None  # {question_id: "a"/"b"} when mode="test"
    type_code: Optional[str] = None  # when mode="direct"


class InterestSubmission(BaseModel):
    """兴趣提交数据"""
    tags: list[str] = Field(..., min_length=3, max_length=8)
    descriptions: list[str] = Field(..., min_length=1, max_length=3)


class IELTSSubmission(BaseModel):
    """IELTS 考试偏好"""
    topic_types: list[str]
    target_score: str
    exam_date: Optional[str] = None


class QuestionnaireSubmission(BaseModel):
    """完整问卷提交数据"""
    mbti: MBTISubmission
    interests: InterestSubmission
    ielts: IELTSSubmission


class QuestionnaireResponse(BaseModel):
    """问卷提交响应"""
    id: str
    mbti_result: dict
    interests: dict
    ielts: dict
    created_at: str


# 保留旧模型兼容性（其他模块可能引用）
class MBTIResult(BaseModel):
    """MBTI 测试结果"""
    type_code: str
    dimensions: dict


class InterestProfile(BaseModel):
    """兴趣画像"""
    tags: list[str]
    descriptions: list[str]


class IELTSPreference(BaseModel):
    """IELTS 考试偏好（旧模型兼容）"""
    topic_types: list[str]
    target_score: str
    exam_date: str = ""
