from typing import List, Dict, Any, TypedDict

class ReviewState(TypedDict, total=False):
    target_filename: str
    target_text: str
    highlighted_issues: List[Dict[str, Any]]
    revised_issues: List[Dict[str, Any]]
    report: dict[str, Any]


class ReportState(TypedDict, total=False):
    revised_issues: List[Dict[str, Any]]
    human_feedback: List[Dict[str, Any]]
    document_info: Dict[str, Any]
    report: Dict[str, Any]