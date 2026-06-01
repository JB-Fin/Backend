from fastapi import APIRouter

from app.api.v1.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import answer_question

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    return answer_question(
        question=request.question,
        language=request.language,
    )