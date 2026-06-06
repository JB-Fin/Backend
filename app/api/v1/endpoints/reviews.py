from fastapi import APIRouter, Query, HTTPException, status
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
    try:
        return analyze_review(
            file_id=request.file_id,
            language=request.language,
            regulation_scope=request.regulation_scope,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 검토 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("")
def list_reviews():
    try:
        reviews = get_reviews()

        return {
            "total": len(reviews),
            "items": reviews,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"검토 목록 조회 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/{review_id}", response_model=ReviewDetailResponse)
def get_review(review_id: int):
    try:
        return get_review_by_id(review_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"검토 결과 조회 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/{review_id}/highlights", response_model=list[HighlightItem])
def get_highlights(review_id: int):
    try:
        return get_review_highlights(review_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"하이라이트 조회 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/{review_id}/report")
def download_review_report(
    review_id: int,
    file_format: str = Query(default="pdf", alias="format"),
):
    try:
        file_format = file_format.lower()

        report_path = get_review_report_path(
            review_id=review_id,
            file_format=file_format,
        )

        media_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain; charset=utf-8",
        }

        return FileResponse(
            path=report_path,
            filename=report_path.name,
            media_type=media_types.get(file_format, "application/octet-stream"),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 다운로드 중 오류가 발생했습니다: {str(e)}",
        )