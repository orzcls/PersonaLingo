from pydantic import BaseModel
from typing import Optional


class MaterialUpload(BaseModel):
    filename: str
    file_type: str
    raw_content: str


class MaterialResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    parsed_content: Optional[dict] = None
    analysis_result: Optional[dict] = None
    merged_to_corpus: Optional[str] = None
    created_at: str
