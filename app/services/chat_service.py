# from fastapi import HTTPException, status

# from app.services.regulation_service import search_regulations
# from app.agents.chat_agent import run_faq_agent

# def answer_question(message: str, language: str) -> dict:
#     if not message or not message.strip():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="질문을 입력해주세요.",
#         )

#     regulation_result = search_regulations(
#         query=message.strip(),
#         language=language,
#         top_k=6,
#     )

#     evidence = regulation_result.get("results", [])

#     return run_faq_agent(
#         question=message.strip(),
#         evidence=evidence,
#         language=language,
#     )

import logging
from datetime import datetime

from fastapi import HTTPException, status

from app.services.regulation_service import search_regulations
from app.agents.chat_agent import run_faq_agent


logger = logging.getLogger("chat_service")


def answer_question(message: str, language: str) -> dict:
    request_start = datetime.now()

    logger.info("=" * 60)
    logger.info("[CHAT STEP 0] 질문 처리 시작")
    logger.info("[CHAT STEP 0] language=%s", language)
    logger.info("[CHAT STEP 0] message_length=%d", len(message or ""))
    logger.info("=" * 60)

    try:
        # STEP 1: 입력값 검증
        logger.info("[CHAT STEP 1] 입력값 검증 중...")

        if not message or not message.strip():
            logger.warning("[CHAT STEP 1] 실패 - 빈 질문")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="질문을 입력해주세요.",
            )

        clean_message = message.strip()
        logger.info("[CHAT STEP 1] 완료 - 질문 앞부분: %s", clean_message[:80])

        # STEP 2: 규정 검색
        logger.info("[CHAT STEP 2] 규정 검색 시작 - top_k=6")

        regulation_start = datetime.now()

        regulation_result = search_regulations(
            query=clean_message,
            language=language,
            top_k=6,
        )

        regulation_elapsed = (datetime.now() - regulation_start).total_seconds()

        logger.info("[CHAT STEP 2] 규정 검색 완료 - 소요 시간: %.2f초", regulation_elapsed)
        logger.debug(
            "[CHAT STEP 2] regulation_result keys: %s",
            list(regulation_result.keys()) if isinstance(regulation_result, dict) else type(regulation_result),
        )

        evidence = regulation_result.get("results", [])

        logger.info("[CHAT STEP 2] 검색 근거 개수: %d", len(evidence))

        if evidence:
            first = evidence[0]
            logger.debug(
                "[CHAT STEP 2] 첫 번째 근거: source=%s, page=%s, score=%s, content_preview=%s",
                first.get("source"),
                first.get("page"),
                first.get("retrieval_score"),
                str(first.get("content", ""))[:120],
            )
        else:
            logger.warning("[CHAT STEP 2] 검색 근거 없음")

        # STEP 3: FAQ Agent 실행
        logger.info("[CHAT STEP 3] FAQ Agent 실행 시작")

        agent_start = datetime.now()

        answer = run_faq_agent(
            question=clean_message,
            evidence=evidence,
            language=language,
        )

        agent_elapsed = (datetime.now() - agent_start).total_seconds()

        logger.info("[CHAT STEP 3] FAQ Agent 완료 - 소요 시간: %.2f초", agent_elapsed)

        if isinstance(answer, dict):
            logger.debug("[CHAT STEP 3] answer keys: %s", list(answer.keys()))
        else:
            logger.warning("[CHAT STEP 3] answer 타입이 dict가 아님: %s", type(answer))

        # STEP 4: 전체 완료
        total_elapsed = (datetime.now() - request_start).total_seconds()

        logger.info("[CHAT STEP 4] 질문 처리 완료 - 총 소요 시간: %.2f초", total_elapsed)
        logger.info("=" * 60)

        return answer

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("[CHAT ERROR] 질문 처리 실패 - %s", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"질문 처리 중 오류가 발생했습니다: {str(e)}",
        )