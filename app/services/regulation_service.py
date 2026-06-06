from fastapi import HTTPException, status

def search_regulations(query: str, language: str = "ko", top_k: int = 6):

    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검색어를 입력해야 합니다.",
        )

    if top_k <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_k는 1 이상이어야 합니다.",
        )

    dummy_results = [
        {
            "regulation_id": "REG-001",
            "title": "개인정보 처리 기준",
            "content": "개인정보 수집 시 목적, 보관 기간, 제3자 제공 여부를 명확히 고지해야 한다.",
        },
        {
            "regulation_id": "REG-002",
            "title": "금융소비자 보호 기준",
            "content": "소비자에게 불리한 계약 조건은 명확하고 이해 가능한 방식으로 설명되어야 한다.",
        },
    ]

    return {
        "query": query.strip(),
        "language": language,
        "top_k": top_k,
        "results": dummy_results[:top_k],
    }