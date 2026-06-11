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
    if not isinstance(item, dict):
        return ""

    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}

    content = (
        item.get("content")
        or item.get("page_content")
        or item.get("text")
        or item.get("chunk")
        or item.get("document")
        or metadata.get("content")
        or metadata.get("text")
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


def _normalize_list(value):
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [str(value)]


def _build_context(evidence: list[dict]) -> tuple[list[str], str]:
    sources = []
    context_items = []

    for idx, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            logger.warning(
                "[FAQ DEBUG] evidence item이 dict가 아님 - idx=%d, item=%s",
                idx,
                item,
            )
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

    return sources, "\n\n".join(context_items)


def _build_prompt(question: str, context: str, language: str) -> str:
    return f"""
당신은 금융회사 법무팀 및 준법감시인을 지원하는 FAQ Assistant입니다.

반드시 제공된 문서 내용만 근거로 답변하세요.

답변 원칙:
1. 문서에서 확인되는 내용만 답변하세요.
2. 문서에 없는 내용은 추측하지 마세요.
3. 근거가 부족하거나 확인할 수 없는 경우에도 반드시 JSON 형식으로 답하세요.
4. 근거가 부족한 경우 answer에는 "현재 제공된 규정만으로는 판단하기 어렵습니다."라고 작성하세요.
5. 최종 법률 판단을 하지 마세요.
6. 관련 규정명 또는 조항이 확인되는 경우 함께 제시하세요.
7. 답변 언어는 {language}입니다.

질문:
{question}

관련 문서:
{context}

반드시 아래 JSON 객체 형식으로만 답하세요.
마크다운 코드블록을 쓰지 마세요.
JSON 밖에 설명 문장을 쓰지 마세요.
일반 문장만 단독으로 출력하지 마세요.

출력 형식:
{{
  "answer": "근거 기반 답변",
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
    logger.info("[FAQ AGENT] evidence_count=%d", len(evidence))
    logger.warning("[FAQ DEBUG] evidence_sample=%s", evidence[:2])

    try:
        sources, context = _build_context(evidence)

        logger.warning("[FAQ DEBUG] question=%s", question)
        logger.warning("[FAQ DEBUG] context_length=%d", len(context))
        logger.warning("[FAQ DEBUG] context_preview=%s", context[:2000])

        if not context.strip():
            return {
                "answer": "현재 제공된 규정 근거가 없어 판단하기 어렵습니다.",
                "sources": sources,
                "matched_evidence": [],
                "review_point": [
                    "RAG 검색 결과에 근거 텍스트가 없습니다.",
                    "content, page_content, text, chunk 필드명을 확인하세요.",
                ],
                "debug": {
                    "evidence_count": len(evidence),
                    "context_length": 0,
                    "reason": "empty_context",
                },
            }

        llm = get_llm()
        logger.info("[FAQ AGENT] LLM 객체 생성 완료")

        prompt = _build_prompt(
            question=question,
            context=context,
            language=language,
        )

        logger.info("[FAQ AGENT] LLM 호출 시작")
        llm_start = datetime.now()

        response = llm.invoke(prompt)

        llm_elapsed = (datetime.now() - llm_start).total_seconds()
        logger.info("[FAQ AGENT] LLM 호출 완료 - %.2f초", llm_elapsed)

        raw_content = getattr(response, "content", "")
        content = str(raw_content).strip()

        logger.warning("[FAQ DEBUG] raw_response=%r", content[:2000])

        parsed = safe_parse_json(content, default=None)

        if not isinstance(parsed, dict):
            logger.warning("[FAQ AGENT] JSON 파싱 실패. raw text fallback 처리")
            parsed = {
                "answer": content or "현재 제공된 규정만으로는 판단하기 어렵습니다.",
                "matched_evidence": [],
                "review_point": [
                    "LLM 응답이 JSON 형식이 아니어서 원문 응답을 answer로 처리했습니다."
                ],
            }

        logger.info(
            "[FAQ AGENT] JSON 파싱 처리 완료 - parsed_type=%s",
            type(parsed).__name__,
        )

        answer = parsed.get("answer")
        if not answer:
            answer = "현재 제공된 규정만으로는 판단하기 어렵습니다."

        review_point = _normalize_list(parsed.get("review_point"))
        matched_evidence = _normalize_list(parsed.get("matched_evidence"))

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