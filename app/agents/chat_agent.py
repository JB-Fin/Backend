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

def _get_evidence_content(item: dict) -> str:
    """
    RAG 결과 구조가 content / page_content / text / chunk 등
    제각각일 수 있으므로 가능한 필드를 모두 확인한다.
    """
    if not isinstance(item, dict):
        return ""

    content = (
        item.get("content")
        or item.get("page_content")
        or item.get("text")
        or item.get("chunk")
        or item.get("document")
        or ""
    )

    if not content and isinstance(item.get("metadata"), dict):
        content = (
            item.get("metadata", {}).get("content")
            or item.get("metadata", {}).get("text")
            or ""
        )

    return str(content).strip()

def _get_source_name(item: dict) -> str:
    if not isinstance(item, dict):
        return "unknown"

    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}

    return (
        item.get("title")
        or item.get("source")
        or item.get("regulation_id")
        or metadata.get("title")
        or metadata.get("source")
        or metadata.get("regulation_id")
        or "unknown"
    )


def _get_page(item: dict):
    if not isinstance(item, dict):
        return "-"

    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}

    return (
        item.get("page")
        or item.get("page_number")
        or metadata.get("page")
        or metadata.get("page_number")
        or "-"
    )

def run_faq_agent(
    question: str,
    evidence: list[dict],
    language: str = "ko",
) -> dict:
    start_time = datetime.now()

    logger.info("[FAQ AGENT] 시작")
    logger.info("[FAQ AGENT] language=%s", language)
    logger.info("[FAQ AGENT] question_length=%d", len(question or ""))

    evidence = evidence or []
    logger.info("[FAQ AGENT] evidence_count=%d", len(evidence or []))

    logger.warning("[FAQ DEBUG] evidence_sample=%s", evidence[:2])

    try:
        sources = []
        context_items = []

        for idx, item in enumerate(evidence, start=1):
            if not isinstance(item, dict):
                logger.warning("[FAQ DEBUG] evidence item이 dict가 아님 - idx=%d, item=%s", idx, item)
                continue

            source_name = _get_source_name(item)
            page = _get_page(item)
            content = _get_evidence_content(item)

            sources.append(source_name)

            if not content:
                logger.warning(
                    "[FAQ DEBUG] content 없음 - idx=%d, keys=%s, item=%s",
                    idx,
                    list(item.keys()),
                    item,
                )
                continue

            context_items.append(
                f"[근거 {idx}]\n"
                f"문서: {source_name}\n"
                f"페이지: {page}\n"
                f"내용: {content}"
            )

        context = "\n\n".join(context_items)

        logger.warning("[FAQ DEBUG] question=%s", question)
        logger.warning("[FAQ DEBUG] context_length=%d", len(context))
        logger.warning("[FAQ DEBUG] context_preview=%s", context[:2000])

        if not context.strip():
            return {
                "answer": "현재 제공된 규정 근거가 없어 판단하기 어렵습니다.",
                "sources": sources,
                "review_point": [
                    "RAG 검색 결과에 content/page_content/text/chunk 필드가 있는지 확인하세요.",
                    "검색된 evidence가 비어 있거나, 근거 텍스트가 누락되었습니다.",
                ],
                "debug": {
                    "evidence_count": len(evidence),
                    "context_length": 0,
                    "reason": "empty_context",
                },
            }

        llm = get_llm()
        logger.info("[FAQ AGENT] LLM 객체 생성 완료")

        prompt = f"""
당신은 규정 기반 FAQ 답변 Agent입니다.

역할:
- 사용자의 질문에 대해 제공된 관련 근거를 바탕으로 답변합니다.
- 최종 법률 판단이 아니라, 제공된 규정 근거에 기반한 안내 답변을 작성합니다.

매우 중요한 답변 원칙:
- 반드시 관련 근거의 내용 안에서만 답변하세요.
- 관련 근거에 질문과 완전히 같은 표현이 없어도, 같은 의미의 규정 내용이 있으면 그 근거를 바탕으로 답변하세요.
- 근거에 직접적으로 관련된 내용이 있으면 "답변할 수 없다"고 하지 마세요.
- 근거가 일부만 충분하면, 가능한 부분은 답변하고 부족한 부분은 별도로 표시하세요.
- 근거가 전혀 관련 없을 때만 "현재 제공된 규정만으로는 판단하기 어렵습니다."라고 답하세요.
- 답변에는 어떤 근거 번호를 사용했는지 포함하세요.
- 법령명, 문서명, 페이지, 근거 번호를 활용하세요.
- 답변 언어는 {language}입니다.

질문:
{question}

관련 근거:
{context}

반드시 JSON 객체로만 답하세요.
마크다운 코드블록을 쓰지 마세요.
설명 문장을 JSON 밖에 쓰지 마세요.

출력 형식:
{{
  "answer": "근거 기반 답변. 사용한 근거 번호를 포함하세요.",
  "matched_evidence": [
    {{
      "evidence_no": 1,
      "reason": "이 근거가 질문과 관련되는 이유"
    }}
  ],
  "review_point": [
    "추가 확인이 필요한 사항"
  ]
}}
"""

        logger.info("[FAQ AGENT] LLM 호출 시작")
        llm_start = datetime.now()

        response = llm.invoke(prompt)

        llm_elapsed = (datetime.now() - llm_start).total_seconds()
        logger.info("[FAQ AGENT] LLM 호출 완료 - %.2f초", llm_elapsed)

        content = getattr(response, "content", "")
        logger.debug("[FAQ AGENT] raw_response_preview=%s", str(content)[:2000])

        parsed = safe_parse_json(content, default={})
        logger.info("[FAQ AGENT] JSON 파싱 완료 - parsed_type=%s", type(parsed).__name__)

        if not isinstance(parsed, dict):
            logger.warning("[FAQ AGENT] parsed가 dict가 아님. fallback 처리")
            parsed = {}

        answer = parsed.get("answer") or str(content)
        review_point = parsed.get("review_point", [])
        matched_evidence = parsed.get("matched_evidence", [])

        if not isinstance(review_point, list):
            review_point = []

        if not isinstance(matched_evidence, list):
            matched_evidence = []

        result = {
            "answer": str(answer),
            "sources": sources,
            "matched_evidence": matched_evidence,
            "review_point": review_point,
        }

        total_elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("[FAQ AGENT] 완료 - total_elapsed=%.2f초", total_elapsed)

        return result

    except Exception as e:
        logger.exception("[FAQ AGENT ERROR] 실패 - %s", str(e))
        raise