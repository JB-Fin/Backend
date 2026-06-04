from fastapi import APIRouter

from app.api.v1.schemas.regulation import (
    RegulationSearchRequest,
    RegulationSearchResponse,
)
from app.services.regulation_service import search_regulations

router = APIRouter()


@router.post("/search", response_model=RegulationSearchResponse)
def search(request: RegulationSearchRequest):
    return search_regulations(
        query=request.query,
        language=request.language,
        top_k=request.top_k,
    )