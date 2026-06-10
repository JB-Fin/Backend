from fastapi import APIRouter, BackgroundTasks, Query, HTTPException, status
from fastapi.responses import FileResponse

from app.api.v1.schemas.review import (
    ReviewAnalyzeRequest,
    ReviewDetailResponse,
    HighlightItem,
)

from app.services.review_service import (
    create_pending_review,
    run_analyze_background,
    get_reviews,
    get_review_by_id,
    get_review_highlights,
    get_review_report_path,
)

router = APIRouter()

@router.post("/analyze", status_code=202)
def analyze_document(
    request: ReviewAnalyzeRequest,
    background_tasks: BackgroundTasks,
):
    """
    즉시 202 + { review_id, status: "pending" } 반환.
    프론트는 GET /reviews/{review_id} 를 폴링해서 status가
    "completed" 또는 "failed"가 될 때까지 기다린다.
    """
    regulation_scope = "internal_external"
    # pending 레코드 즉시 생성
    review = create_pending_review(
        file_id=request.file_id,
        language=request.language,
        regulation_scope=regulation_scope,
    )
    # 실제 분석은 백그라운드에서 실행 (타임아웃 무관)
    background_tasks.add_task(
        run_analyze_background,
        review_id=review["review_id"],
        file_id=request.file_id,
        language=request.language,
        regulation_scope=regulation_scope,
    )
    return {
        "review_id": review["review_id"],
        "status": "pending",
        "message": "분석이 시작되었습니다. GET /reviews/{review_id} 로 결과를 확인하세요.",
    }

@router.get("")
def list_reviews():
    reviews = get_reviews()
    return {"total": len(reviews), "items": reviews}

@router.get("/{review_id}", response_model=ReviewDetailResponse)
def get_review(review_id: int):
    return get_review_by_id(review_id)

@router.get("/{review_id}/highlights", response_model=list[HighlightItem])
def get_highlights(review_id: int):
    return get_review_highlights(review_id)

@router.get("/{review_id}/report")
def download_review_report(
    review_id: int,
    file_format: str = Query(default="pdf", alias="format"),
):
    report_path = get_review_report_path(
        review_id=review_id,
        file_format=file_format.lower(),
    )
    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain; charset=utf-8",
    }
    return FileResponse(
        path=report_path,
        filename=report_path.name,
        media_type=media_types.get(file_format.lower(), "application/octet-stream"),
    )