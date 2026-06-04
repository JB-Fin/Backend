from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReviewAnalyzeRequest(BaseModel):
    file_id: int
    language: str = "ko"
    regulation_scope: str = "internal_external"


class HighlightItem(BaseModel):
    page: Optional[int] = None
    original_text: str
    issue: str
    suggestion: str
    risk_level: str


class ReviewAnalyzeResponse(BaseModel):
    review_id: int
    file_id: int
    file_name: Optional[str] = None
    status: str
    language: str
    regulation_scope: Optional[str] = None
    summary: str
    risk_level: str
    highlights: list[HighlightItem]
    created_at: datetime
    report_files: dict[str, str] = {}


class ReviewDetailResponse(ReviewAnalyzeResponse):
    pass