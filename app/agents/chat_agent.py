from app.utils.llm_client import get_llm


def run_faq_agent(
    question: str,
    evidence: list[dict],
    language: str = "ko",
) -> dict:
    sources = [
        item.get("title")
        or item.get("source")
        or item.get("regulation_id")
        or "unknown"
        for item in evidence
    ]

    context = "\n\n".join(
        [
            f"[근거 {idx}]\n"
            f"문서: {item.get('title') or item.get('source') or item.get('regulation_id') or 'unknown'}\n"
            f"페이지: {item.get('page', '-')}\n"
            f"내용: {item.get('content', '')}"
            for idx, item in enumerate(evidence, start=1)
        ]
    )

    llm = get_llm()

    prompt = f"""
당신은 규정 기반 FAQ 답변 Agent입니다.

원칙:
- 제공된 규정 근거만 바탕으로 답변하세요.
- 근거에 없는 내용은 추측하지 마세요.
- 근거가 부족하면 "현재 제공된 규정만으로는 판단하기 어렵습니다."라고 답하세요.
- 최종 법률 판단을 단정하지 마세요.
- 답변 언어는 {language}입니다.

질문:
{question}

관련 근거:
{context}

답변에는 다음을 포함하세요.
1. 질문에 대한 답변
2. 확인한 근거
3. 담당자가 추가 확인할 검토 포인트
"""

    response = llm.invoke(prompt)

    return {
        "answer": str(response.content),
        "sources": sources,
        "review_point": [],
    }