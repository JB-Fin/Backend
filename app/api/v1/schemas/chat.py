from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    language: str = "ko"
    review_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []