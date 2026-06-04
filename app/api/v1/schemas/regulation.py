from pydantic import BaseModel


class RegulationSearchRequest(BaseModel):
    query: str
    language: str = "ko"
    top_k: int = 5


class RegulationSearchItem(BaseModel):
    regulation_id: str
    title: str
    content: str
    score: float


class RegulationSearchResponse(BaseModel):
    query: str
    results: list[RegulationSearchItem]