from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ChatRequest(BaseModel):
    user_id: int
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)


class SourceItem(BaseModel):
    source: str
    file_type: Optional[str] = None
    page: Optional[int] = None
    similarity_score: float
    preview: str


class ChatModel(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    query: str
    answer: str
    sources: List[SourceItem]
    confidence: float
    has_context: Optional[bool] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}