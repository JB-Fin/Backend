from pydantic import BaseModel

class RegulationSearchItem(BaseModel):
    regulation_id: str
    title: str
    content: str

class RegulationSearchRequest(BaseModel):
    query: str
    language: str = "ko"
    top_k: int = 6

class RegulationSearchResponse(BaseModel):
    query: str
    language: str
    top_k: int
    results: list[RegulationSearchItem]