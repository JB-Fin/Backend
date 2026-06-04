from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.v1.schemas.review import (
    ReviewAnalyzeRequest,
    ReviewAnalyzeResponse,
    ReviewDetailResponse,
    HighlightItem,
)
from app.services.review_service import (
    analyze_review,
    get_reviews,
    get_review_by_id,
    get_review_highlights,
    get_review_report_path,
)

router = APIRouter()

@router.post("/analyze", response_model=ReviewAnalyzeResponse)
def analyze_document(request: ReviewAnalyzeRequest):
    return analyze_review(
        file_id=request.file_id,
        language=request.language,
        regulation_scope=request.regulation_scope,
    )

@router.get("", response_model=list[ReviewDetailResponse])
def list_reviews():
    return get_reviews()

@router.get("/{review_id}", response_model=ReviewDetailResponse)
def get_review(review_id: int):
    return get_review_by_id(review_id)

@router.get("/{review_id}/highlights", response_model=list[HighlightItem])
def get_highlights(review_id: int):
    return get_review_highlights(review_id)

@router.get("/{review_id}/report")
def download_review_report(review_id: int, format: str = "pdf"):
    report_path = get_review_report_path(
        review_id=review_id,
        file_format=format,
    )

    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
    }

    return FileResponse(
        path=report_path,
        filename=report_path.name,
        media_type=media_types.get(format, "application/octet-stream"),
    )