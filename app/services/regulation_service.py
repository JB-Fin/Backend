def search_regulations(query: str, language: str = "ko", top_k: int = 5):
    # TODO:
    # 1. 규정 문서 임베딩
    # 2. 벡터 DB 검색
    # 3. 관련 조항 반환

    dummy_results = [
        {
            "regulation_id": "REG-001",
            "title": "개인정보 처리 기준",
            "content": "개인정보 수집 시 목적, 보관 기간, 제3자 제공 여부를 명확히 고지해야 한다.",
            "score": 0.92,
        },
        {
            "regulation_id": "REG-002",
            "title": "금융소비자 보호 기준",
            "content": "소비자에게 불리한 계약 조건은 명확하고 이해 가능한 방식으로 설명되어야 한다.",
            "score": 0.87,
        },
    ]

    return {
        "query": query,
        "results": dummy_results[:top_k],
    }