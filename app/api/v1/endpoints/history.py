from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_history():
    return [
        {
            "id": 1,
            "title": "금융상품 광고 문구.docx",
            "requester": "김준법",
            "requested_at": "2026.05.31 14:30",
            "document_type": "DOCX",
            "status": "검토 완료",
            "issue_count": 3,
            "suggestion_count": 5,
        },
        {
            "id": 2,
            "title": "투자설명서_v2.pdf",
            "requester": "이규숙",
            "requested_at": "2026.05.31 11:20",
            "document_type": "PDF",
            "status": "검토 중",
            "issue_count": 8,
            "suggestion_count": 12,
        },
        {
            "id": 3,
            "title": "대출상품 약관.pdf",
            "requester": "박미성",
            "requested_at": "2026.05.30 16:45",
            "document_type": "PDF",
            "status": "수정본 생성 완료",
            "issue_count": 1,
            "suggestion_count": 2,
        },
    ]