from typing import List
from pydantic import BaseModel

class ReviewAnalyzeRequest(BaseModel):
    filename: str
    language: str = "ko"

class RiskComment(BaseModel):
    title: str
    category: str
    related_rule: str
    description: str
    suggestion: str
    status: str

class ReviewAnalyzeResponse(BaseModel):
    review_id: int
    filename: str
    language: str
    status: str
    issue_count: int
    suggestion_count: int
    original_text: List[str]
    revised_text: List[str]
    comments: List[RiskComment]