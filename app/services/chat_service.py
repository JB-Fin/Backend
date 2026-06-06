from fastapi import HTTPException, status

from app.services.regulation_service import search_regulations
from app.agents.chat_agent import generate_chat_answer

def answer_question(question: str, language: str) -> dict:

    if not question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문을 입력해주세요.",
        )

    regulation_result = search_regulations(
        query=question,
        language=language,
        top_k=6,
    )

    # return generate_chat_answer(
    #     question=question,                         
    #     language=language,
    #     regulations=regulation_result["results"],
    # )

    regulations = regulation_result["results"]

    # context,  sources 부분들은 Agent 코드 구현 이후 빼야함
    sources = [
        item["title"]
        for item in regulations
    ]

    context = "\n\n".join(
        [
            f"[{item['regulation_id']}] {item['title']}\n{item['content']}"
            for item in regulations
        ]
    )

    # 임시 stub 응답
    return {
        "answer": (
            f"질문: {question}\n\n"
            f"아래 규정을 참고하여 답변합니다.\n\n"
            f"{context}"
        ),
        "sources": sources,
    }