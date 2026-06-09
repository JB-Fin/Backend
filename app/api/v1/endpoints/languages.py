from fastapi import APIRouter, HTTPException, status
from app.api.v1.schemas.language import LanguageUpdateRequest

router = APIRouter()

@router.get("")
def get_languages():
    try:
        return {
            "languages": [
                {"code": "ko", "name": "한국어(Korean)"},
                {"code": "en", "name": "English(영어)"},
                {"code": "km", "name": "ភាសាខ្មែរ(캄보디아어)"},
                {"code": "vi", "name": "Tiếng Việt(베트남어)"},
                {"code": "my", "name": "မြန်မာဘာသာ(미얀마어)"},
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"언어 목록 조회 중 오류가 발생했습니다: {str(e)}",
        )
    
@router.put("/settings/language")
def update_language(request: LanguageUpdateRequest):
    return {
        "message": "언어 설정 변경 완료",
        "language": request.language,
    }