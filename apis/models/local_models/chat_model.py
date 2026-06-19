from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's question")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of chunks to retrieve")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score (0-1) for a chunk to be used")


class SourceItem(BaseModel):
    source: str
    file_type: Optional[str] = None
    page: Optional[int] = None
    similarity_score: float
    preview: str


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceItem]
    confidence: float
    has_context: bool


class ChatHistoryItem(BaseModel):
    id: int
    query: str
    answer: str
    sources: List[SourceItem]
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}