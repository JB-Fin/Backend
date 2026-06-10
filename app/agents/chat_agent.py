# import json

# from app.utils.llm_client import get_llm
# from app.utils.agent_utils import safe_parse_json

# def run_faq_agent(
#     question: str,
#     evidence: list[dict],
#     language: str = "ko",
# ) -> dict:
#     sources = [
#         item.get("title")
#         or item.get("source")
#         or item.get("regulation_id")
#         or "unknown"
#         for item in evidence
#     ]

#     context = "\n\n".join(
#         [
#             f"[근거 {idx}]\n"
#             f"문서: {item.get('title') or item.get('source') or item.get('regulation_id') or 'unknown'}\n"
#             f"페이지: {item.get('page', '-')}\n"
#             f"내용: {item.get('content', '')}"
#             for idx, item in enumerate(evidence, start=1)
#         ]
#     )

#     llm = get_llm()

#     prompt = f"""
# 당신은 규정 기반 FAQ 답변 Agent입니다.

# 원칙:
# - 제공된 규정 근거만 바탕으로 답변하세요.
# - 근거에 없는 내용은 추측하지 마세요.
# - 근거가 부족하면 "현재 제공된 규정만으로는 판단하기 어렵습니다."라고 답하세요.
# - 최종 법률 판단을 단정하지 마세요.
# - 답변 언어는 {language}입니다.

# 질문:
# {question}

# 관련 근거:
# {context}

# 반드시 JSON 객체로만 답하세요.
# 마크다운 코드블록을 쓰지 마세요.
# 설명 문장을 쓰지 마세요.

# 출력 형식:
# {{
#   "answer": "질문에 대한 답변",
#   "review_point": [
#     "담당자가 추가로 확인해야 할 검토 포인트 1",
#     "담당자가 추가로 확인해야 할 검토 포인트 2"
#   ]
# }}
# """

#     response = llm.invoke(prompt)

#     parsed = safe_parse_json(response.content, default={})

#     if not isinstance(parsed, dict):
#         parsed = {}

#     answer = parsed.get("answer")
#     review_point = parsed.get("review_point", [])

#     if not isinstance(review_point, list):
#         review_point = []

#     return {
#         "answer": str(answer or response.content),
#         "sources": sources,
#         "review_point": review_point,
#     }

import logging
from datetime import datetime

from app.utils.llm_client import get_llm
from app.utils.agent_utils import safe_parse_json

logger = logging.getLogger("faq_agent")


def run_faq_agent(
    question: str,
    evidence: list[dict],
    language: str = "ko",
) -> dict:
    start_time = datetime.now()

    logger.info("[FAQ AGENT] 시작")
    logger.info("[FAQ AGENT] language=%s", language)
    logger.info("[FAQ AGENT] question_length=%d", len(question or ""))
    logger.info("[FAQ AGENT] evidence_count=%d", len(evidence or []))

    try:
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

        logger.info("[FAQ AGENT] context 생성 완료 - context_length=%d", len(context))
        logger.debug("[FAQ AGENT] sources=%s", sources)

        llm = get_llm()
        logger.info("[FAQ AGENT] LLM 객체 생성 완료")

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

반드시 JSON 객체로만 답하세요.
마크다운 코드블록을 쓰지 마세요.
설명 문장을 쓰지 마세요.

출력 형식:
{{
  "answer": "질문에 대한 답변",
  "review_point": [
    "담당자가 추가로 확인해야 할 검토 포인트 1",
    "담당자가 추가로 확인해야 할 검토 포인트 2"
  ]
}}
"""

        logger.info("[FAQ AGENT] LLM 호출 시작")
        llm_start = datetime.now()

        response = llm.invoke(prompt)

        llm_elapsed = (datetime.now() - llm_start).total_seconds()
        logger.info("[FAQ AGENT] LLM 호출 완료 - %.2f초", llm_elapsed)

        content = getattr(response, "content", "")
        logger.debug("[FAQ AGENT] raw_response_preview=%s", str(content)[:500])

        parsed = safe_parse_json(content, default={})
        logger.info("[FAQ AGENT] JSON 파싱 완료 - parsed_type=%s", type(parsed).__name__)

        if not isinstance(parsed, dict):
            logger.warning("[FAQ AGENT] parsed가 dict가 아님. fallback 처리")
            parsed = {}

        answer = parsed.get("answer")
        review_point = parsed.get("review_point", [])

        if not isinstance(review_point, list):
            logger.warning("[FAQ AGENT] review_point가 list가 아님. 빈 배열 처리")
            review_point = []

        result = {
            "answer": str(answer or content),
            "sources": sources,
            "review_point": review_point,
        }

        total_elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("[FAQ AGENT] 완료 - total_elapsed=%.2f초", total_elapsed)

        return result

    except Exception as e:
        logger.exception("[FAQ AGENT ERROR] 실패 - %s", str(e))
        raise