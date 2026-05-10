from pydantic import BaseModel
from typing import Optional


class NoteResponse(BaseModel):
    id: str
    corpus_id: Optional[str] = None
    trigger_type: str
    title: str
    summary: str
    changes: list = []
    tips: list = []
    mindmap_mermaid: str = ""
    created_at: str
