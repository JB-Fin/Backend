def answer_question(question: str, language: str) -> dict:
    """
    사용자 질문에 답변을 반환합니다.
    현재는 stub 상태입니다. OpenAI 연동 시 아래 주석을 해제하세요.
    """
    
    # from openai import OpenAI
    # import os
    #
    # client = OpenAI()
    # MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    #
    # response = client.chat.completions.create(
    #     model=MODEL_NAME,
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": f"You are a legal compliance assistant. Respond in {language}.",
    #         },
    #         {
    #             "role": "user",
    #             "content": question,
    #         },
    #     ],
    # )
    #
    # return {"answer": response.choices[0].message.content}

    # 임시 stub 응답
    return {"answer": f"'{question}'에 대한 답변 기능은 준비 중입니다."}
