from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.regulation import (
    RegulationSearchRequest,
    RegulationSearchResponse,
)

from app.services.regulation_service import search_regulations

router = APIRouter()

@router.post("/search", response_model=RegulationSearchResponse)
def search(request: RegulationSearchRequest):
    try:
        return search_regulations(
            query=request.query,
            language=request.language,
            top_k=request.top_k,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"규정 검색 중 오류가 발생했습니다: {str(e)}",
        )