from pydantic import BaseModel
from typing import Optional, Any


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None