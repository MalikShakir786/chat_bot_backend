from pydantic import BaseModel
from datetime import datetime


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_path: str
    file_size: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_path: str
    file_size: str
    uploaded_at: datetime
    
    model_config = {
        "from_attributes": True
    }