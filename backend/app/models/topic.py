from pydantic import BaseModel
from typing import Optional


class TopicCreate(BaseModel):
    part: str
    season: Optional[str] = ""
    category: Optional[str] = ""
    title: str
    questions: list[str] = []
    is_new: bool = True
    difficulty: str = "medium"
    recommended_anchors: list[str] = []
    source: str = "user"
    linked_p2_id: Optional[str] = None


class TopicResponse(BaseModel):
    id: str
    part: str
    season: str
    category: str
    title: str
    questions: list
    is_new: bool
    difficulty: str
    recommended_anchors: list
    source: str
    linked_p2_id: Optional[str] = None


class TopicFilter(BaseModel):
    part: Optional[str] = None
    season: Optional[str] = None
    category: Optional[str] = None
