from pydantic import BaseModel
from datetime import datetime


class DBDocumentCrate(BaseModel):
    filename: str
    file_type: str
    file_path: str


class DBDocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_path: str
    uploaded_at: datetime