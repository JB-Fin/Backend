from fastapi import APIRouter

from app.services.review_service import get_reviews

router = APIRouter()

@router.get("")
def get_history():
    reviews = get_reviews()

    return {
        "total": len(reviews),
        "items": reviews,
    }