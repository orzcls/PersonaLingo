from pydantic import BaseModel, Field
from typing import Optional, List
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


class InterestTag(BaseModel):
    """兴趣标签（支持自定义）"""
    name: str
    is_custom: bool = False  # 是否用户自定义标签


class InterestSubmission(BaseModel):
    """兴趣提交数据"""
    tags: List[InterestTag]  # 改为支持自定义标签
    descriptions: List[str] = []


class IELTSSubmission(BaseModel):
    """IELTS 考试偏好"""
    topic_types: list[str]
    target_score: str
    exam_date: Optional[str] = None


class PersonItem(BaseModel):
    """人物维度：重要的人"""
    relationship: str  # 挚友/对象/家人/导师/同学等
    nickname: str  # 称呼
    description: str  # 一句话描述这个人的特点或你们之间的故事
    memorable_experience: Optional[str] = None  # 难忘经历


class ObjectItem(BaseModel):
    """物品维度：有意义的物"""
    category: str  # 宠物/乐器/书/车/礼物/收藏品等
    name: str  # 物品名
    significance: str  # 为什么重要/有什么故事


class PlaceItem(BaseModel):
    """地点维度：印象深刻的地"""
    category: str  # 山水名胜/国家/博物馆/公园/城市/校园等
    name: str  # 地点名
    experience: str  # 去过的经历/感受/故事


class LifeExperiences(BaseModel):
    """真实经历场景"""
    people: List[PersonItem] = []  # 重要的人
    objects: List[ObjectItem] = []  # 有意义的物
    places: List[PlaceItem] = []  # 印象深刻的地


class PersonalBackground(BaseModel):
    """个人背景"""
    age: Optional[int] = None
    gender: Optional[str] = None
    zodiac: Optional[str] = None  # 星座
    profession: Optional[str] = None  # 职业/专业
    city: Optional[str] = None  # 所在城市
    self_description: Optional[str] = None  # 自我描述（自由文本）


class QuestionnaireSubmission(BaseModel):
    """完整问卷提交数据"""
    mbti: MBTISubmission
    interests: InterestSubmission
    ielts: IELTSSubmission
    personal_background: Optional[PersonalBackground] = None
    life_experiences: Optional[LifeExperiences] = None


class QuestionnaireResponse(BaseModel):
    """问卷提交响应"""
    id: str
    mbti_result: dict
    interests: dict
    ielts: dict
    personal_background: Optional[dict] = None
    life_experiences: Optional[dict] = None
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
