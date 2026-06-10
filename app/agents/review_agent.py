# from app.rag.retriever import retrieve_evidence
# from app.utils.agent_utils import (
#     clean_text,
#     safe_parse_json,
#     dedupe_by_highlight_text,
#     compact_evidence,
# )
# from app.utils.llm_client import get_llm

# TOP_N_ISSUES = 5
# MAX_TARGET_CHARS = 12000


# def run_review_agent(state: dict) -> dict:
#     target_text = state["target_text"]
#     vectorstore = state.get("vectorstore")

#     if vectorstore is None:
#         evidence_pool = []
#     else:
#         evidence_pool = retrieve_evidence(
#             vectorstore=vectorstore,
#             query=target_text,
#             k=6,
#         )

#     evidence_pool = compact_evidence(evidence_pool)

#     llm = get_llm()

#     prompt = f"""
# 당신은 준법 검토 지원 시스템의 Review Agent입니다.

# 중요:
# - 당신은 최종 위반 여부를 판정하지 않습니다.
# - 심각도 점수, 리스크 점수, 위반 확률을 생성하지 않습니다.
# - 설명 가능한 AI를 위해 문서에서 "검토가 필요한 후보 문장"만 추출합니다.
# - 후보는 최대 {TOP_N_ISSUES}개만 반환합니다.
# - 각 후보는 원문에 실제로 존재하는 문장이어야 합니다.
# - 법령 내용을 지어내지 마세요.

# 참고 근거:
# {evidence_pool}

# 반드시 JSON 배열로만 답하세요.
# 마크다운 코드블록을 쓰지 마세요.
# 설명 문장을 쓰지 마세요.
# 반드시 [ 로 시작하고 ] 로 끝나는 JSON 배열만 출력하세요.

# 출력 형식:
# [
#   {{
#     "issue_id": 1,
#     "highlight_text": "원문에서 하이라이트할 문장",
#     "issue_summary": "검토 필요 사유 요약",
#     "review_focus": "어떤 기준과 대조 검토가 필요한지",
#     "revision_guideline": "수정 방향 제안"
#   }}
# ]

# [검토 대상 문서]
# {target_text[:MAX_TARGET_CHARS]}
# """

#     response = llm.invoke(prompt)
#     candidates = safe_parse_json(response.content, default=[])

#     if not isinstance(candidates, list):
#         candidates = []

#     highlighted_issues = []

#     for idx, item in enumerate(candidates[:TOP_N_ISSUES], start=1):
#         if not isinstance(item, dict):
#             continue

#         highlight_text = clean_text(item.get("highlight_text", ""))
#         issue_summary = clean_text(item.get("issue_summary", ""))
#         review_focus = clean_text(item.get("review_focus", ""))
#         revision_guideline = clean_text(item.get("revision_guideline", ""))

#         if not highlight_text:
#             continue

#         issue_evidence = evidence_pool

#         if vectorstore is not None:
#             issue_evidence = retrieve_evidence(
#                 vectorstore=vectorstore,
#                 query=f"{highlight_text}\n{issue_summary}\n{review_focus}",
#                 k=6,
#             )
#             issue_evidence = compact_evidence(issue_evidence)

#         highlighted_issues.append(
#             {
#                 "issue_id": idx,
#                 "highlight_text": highlight_text,
#                 "issue_summary": issue_summary,
#                 "review_focus": review_focus,
#                 "revision_guideline": revision_guideline,
#                 "evidence": issue_evidence,
#             }
#         )

#     highlighted_issues = dedupe_by_highlight_text(highlighted_issues)

#     return {
#         "highlighted_issues": highlighted_issues,
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