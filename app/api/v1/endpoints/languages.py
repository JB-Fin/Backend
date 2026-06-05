from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_languages():
    return {
        "languages": [
            {"code": "ko", "name": "한국어(Korean)"},
            {"code": "en", "name": "English(영어)"},
            {"code": "ja", "name": "ភាសាខ្មែរ(캄도디아어)"},
            {"code": "zh", "name": "Tiếng Việt(베트남어)"},
            {"code": "es", "name": "မြန်မာဘာသာ(미얀마어)"},
        ]
    }