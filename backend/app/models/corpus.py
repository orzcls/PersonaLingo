from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnchorStory(BaseModel):
    """锚点故事 - 用户的个人经历/故事"""
    id: str
    title: str
    description: str
    keywords: list[str]


class BridgeResponse(BaseModel):
    """桥接回答 - 将任意话题桥接到个人锚点"""
    topic: str
    anchor_id: str
    bridge_sentence: str
    sample_answer: str


class VocabularyUpgrade(BaseModel):
    """词汇升级 - 基础词汇到高级替代"""
    basic_word: str
    advanced_alternatives: list[str]
    context: str


class SentencePattern(BaseModel):
    """句型模板 - 可复用的句型结构"""
    pattern_name: str
    template: str
    example: str
    usage_context: str


class PersonalCorpus(BaseModel):
    """完整个人语料库"""
    id: str
    user_profile: dict
    anchors: list[AnchorStory]
    bridges: list[BridgeResponse]
    vocabulary: list[VocabularyUpgrade]
    patterns: list[SentencePattern]
    created_at: datetime = datetime.now()
