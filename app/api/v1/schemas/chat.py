from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    language: str = "ko"


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]