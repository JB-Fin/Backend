from typing import List, Dict, Any, TypedDict

# class ReviewState(TypedDict, total=False):
#     target_filename: str
#     target_text: str
#     highlighted_issues: List[Dict[str, Any]]
#     revised_issues: List[Dict[str, Any]]
#     report: dict[str, Any]
#     revised_document: str

# class ReportState(TypedDict, total=False):
#     revised_issues: List[Dict[str, Any]]
#     human_feedback: List[Dict[str, Any]]
#     document_info: Dict[str, Any]
#     report: Dict[str, Any]

from typing import TypedDict, Any


class ReviewState(TypedDict, total=False):
    file_id: int
    file_name: str
    language: str
    regulation_scope: str
    target_text: str
    vectorstore: Any
    document_info: dict[str, Any]

    highlighted_issues: list[dict[str, Any]]
    revised_issues: list[dict[str, Any]]
    report: dict[str, Any]
    revised_document: str