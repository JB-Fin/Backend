def answer_question(question: str, language: str = "ko") -> dict:
    return {
        "answer": f"'{question}'에 대한 임시 RAG 기반 답변입니다.",
        "sources": [
            "내부 규정 문서",
            "금융소비자보호법",
            "상품 설명서 가이드라인",
        ],
    }