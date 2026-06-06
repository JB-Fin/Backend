from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import answer_question

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return answer_question(
            question=request.message,
            language=request.language,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"채팅 응답 생성 중 오류가 발생했습니다: {str(e)}",
        )