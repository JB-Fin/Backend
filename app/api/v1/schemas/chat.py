from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    language: str = "ko"

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    review_points: list[str] = []