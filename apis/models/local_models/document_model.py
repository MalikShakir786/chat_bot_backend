from pydantic import BaseModel
from datetime import datetime


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_path: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_path: str
    uploaded_at: datetime