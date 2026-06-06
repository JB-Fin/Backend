def generate_chat_answer(
    question: str,
    language: str,
    regulations: list[dict],
) -> dict:
    sources = [item["title"] for item in regulations]

    context = "\n\n".join(
        [
            f"[{item['regulation_id']}] {item['title']}\n{item['content']}"
            for item in regulations
        ]
    )

    # TODO: OpenAI 연동 시 여기서 LLM 호출
    return {
        "answer": (
            f"질문: {question}\n\n"
            f"아래 규정을 참고하여 답변합니다.\n\n"
            f"{context}"
        ),
        "sources": sources,
    }