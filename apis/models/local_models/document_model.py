from pydantic import BaseModel
from datetime import datetime


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_path: str
    file_size: float


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_path: str
    file_size: float
    uploaded_at: datetime