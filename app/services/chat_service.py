from fastapi import HTTPException, status

from app.services.regulation_service import search_regulations
from app.agents.chat_agent import run_faq_agent

def answer_question(message: str, language: str) -> dict:
    if not message or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문을 입력해주세요.",
        )

    regulation_result = search_regulations(
        query=message.strip(),
        language=language,
        top_k=6,
    )

    evidence = regulation_result.get("results", [])

    return run_faq_agent(
        question=message.strip(),
        evidence=evidence,
        language=language,
    )