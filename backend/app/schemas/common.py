from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    error: bool = True
    code: str
    message: str
    event_id: Optional[str] = None


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
