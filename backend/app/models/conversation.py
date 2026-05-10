from pydantic import BaseModel
from typing import Optional


class ConversationMessage(BaseModel):
    corpus_id: str
    content: str


class ConversationResponse(BaseModel):
    id: str
    corpus_id: str
    role: str
    content: str
    extracted_items: Optional[list] = None
    created_at: str
