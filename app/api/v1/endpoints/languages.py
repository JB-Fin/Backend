from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_languages():
    return {
        "languages": [
            {"code": "ko", "name": "Korean"},
            {"code": "en", "name": "English"},
            {"code": "ja", "name": "Japanese"},
            {"code": "zh", "name": "Chinese"},
            {"code": "es", "name": "Spanish"},
        ]
    }