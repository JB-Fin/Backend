from fastapi import APIRouter

from app.api.v1.schemas.review import ReviewAnalyzeRequest, ReviewAnalyzeResponse
from app.services.review_service import analyze_document, generate_report

router = APIRouter()


@router.post("/analyze", response_model=ReviewAnalyzeResponse)
def analyze_review(request: ReviewAnalyzeRequest):
    return analyze_document(
        filename=request.filename,
        language=request.language,
    )


@router.get("/{review_id}", response_model=ReviewAnalyzeResponse)
def get_review_detail(review_id: int):
    return analyze_document(
        filename="금융상품 광고 문구.docx",
        language="ko",
    )


@router.get("/{review_id}/report")
def get_review_report(review_id: int):
    return generate_report(review_id)