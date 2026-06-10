from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

class ReviewAnalyzeRequest(BaseModel):
    file_id: int
    language: str = "ko"

class HighlightItem(BaseModel):
    issue_id: int
    page: Optional[int] = None
    original_text: str
    issue_summary: str
    reason: str
    suggested_text: str
    revision_detail: str
    legal_basis: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)

class ReviewSummary(BaseModel):
    total_issues: int
    issue_summary_counts: dict[str, int]

class ReviewAnalyzeResponse(BaseModel):
    review_id: int
    file_id: int
    file_name: Optional[str] = None
    status: str
    language: str
    regulation_scope: Optional[str] = None
    summary: ReviewSummary
    highlights: list[HighlightItem] = Field(default_factory=list)
    created_at: datetime
    report_files: dict[str, str] = Field(default_factory=dict)

class ReviewDetailResponse(ReviewAnalyzeResponse):
    """
    현재는 ReviewAnalyzeResponse와 동일.
    추후 상세 조회 전용 필드 추가 시 여기에 확장.
    """
    pass