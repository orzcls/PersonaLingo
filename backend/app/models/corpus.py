from pydantic import BaseModel, ConfigDict
from typing import Optional


class CorpusGenerate(BaseModel):
    questionnaire_id: str


class AnchorStory(BaseModel):
    id: str
    label: str = ""
    story: str = ""
    keywords: list[str] = []
    emotion: str = ""
    connectable_topics: list[str] = []


class BridgeItem(BaseModel):
    topic_id: str = ""
    topic_title: str = ""
    category: str = ""
    anchor_id: str = ""
    bridge_sentence: str = ""
    sample_answer: str = ""
    safe_stop_point: str = ""
    techniques_used: list[str] = []


class VocabItem(BaseModel):
    basic_word: str
    upgrade: str = ""
    context: str = ""
    category: str = ""


class PatternItem(BaseModel):
    name: str
    formula: str = ""
    example: str = ""
    when_to_use: str = ""


class PracticeItem(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    topic_title: str
    thinking_guide: list[str] = []
    steps: list[str] = []
    model_answer: str = ""
    checklist: list[str] = []


class CorpusData(BaseModel):
    persona: Optional[dict] = None
    anchors: list[AnchorStory] = []
    bridges: list[BridgeItem] = []
    vocabulary: list[VocabItem] = []
    patterns: list[PatternItem] = []
    practices: list[PracticeItem] = []
    band_strategy: Optional[dict] = None
    user_style: Optional[dict] = None


class CorpusResponse(BaseModel):
    id: str
    questionnaire_id: str
    status: str
    corpus: Optional[CorpusData] = None
    created_at: str
    updated_at: str


# ============ 向后兼容别名（旧路由引用） ============

class BridgeResponse(BaseModel):
    """桥接回答 - 兼容旧路由"""
    topic: str = ""
    anchor_id: str = ""
    bridge_sentence: str = ""
    sample_answer: str = ""


class VocabularyUpgrade(BaseModel):
    """词汇升级 - 兼容旧路由"""
    basic_word: str
    advanced_alternatives: list[str] = []
    context: str = ""


class SentencePattern(BaseModel):
    """句型模板 - 兼容旧路由"""
    pattern_name: str
    template: str = ""
    example: str = ""
    usage_context: str = ""


class PersonalCorpus(BaseModel):
    """完整个人语料库 - 兼容旧路由"""
    id: str
    user_profile: dict = {}
    anchors: list = []
    bridges: list = []
    vocabulary: list = []
    patterns: list = []
