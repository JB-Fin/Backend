# import json

# from app.utils.llm_client import get_llm
# from app.utils.agent_utils import safe_parse_json, clean_text

# MAX_ISSUES_FOR_REVISION = 20


# def run_revision_agent(state: dict) -> dict:
#     highlighted_issues = state.get("highlighted_issues", [])
#     highlighted_issues = highlighted_issues[:MAX_ISSUES_FOR_REVISION]

#     llm = get_llm()

#     prompt = f"""
# 당신은 준법 문서 수정 지원 시스템의 Revision Agent입니다.

# 중요:
# - 당신은 최종 위반 여부를 판정하지 않습니다.
# - 심각도 점수, 위반 확률, 리스크 점수를 생성하지 않습니다.
# - 입력으로 받은 하이라이트 문장과 근거를 바탕으로 "수정안 후보"만 제안합니다.
# - suggested_text에는 설명문이 아니라 문서에 바로 넣을 수 있는 문장만 작성하세요.
# - 근거가 부족하면 suggested_text는 "검토 필요"로 작성하세요.
# - 법령이나 조항이 근거에 없으면 만들어내지 마세요.
# - evidence.content는 검색된 원문 그대로 사용하세요.
# - 요약하거나 재해석하지 마세요.
# - 법령에 없는 문장을 생성하지 마세요.

# suggested_text 금지 표현:
# - "...하십시오"
# - "...하세요"
# - "...수정하십시오"
# - "...명확히 하십시오"
# - "...근거를 제시하십시오"
# - "...검토가 필요합니다"

# 좋은 예:
# 원문: "누구나 연 12%의 확정 수익을 받을 수 있습니다."
# suggested_text: "예상 수익률은 시장 상황에 따라 변동될 수 있으며 원금 손실이 발생할 수 있습니다."

# 나쁜 예:
# suggested_text: "수익률이 확정적임을 명확히 하거나 기대 수익임을 표기하십시오."

# 입력 데이터:
# {json.dumps(highlighted_issues, ensure_ascii=False, indent=2)}

# 반드시 JSON 객체로만 답하세요.
# 마크다운 코드블록을 쓰지 마세요.
# 설명 문장을 쓰지 마세요.

# 출력 형식:
# {{
#   "revised_issues": [
#     {{
#       "issue_id": 1,
#       "highlight_text": "원문 하이라이트 문장",
#       "issue_summary": "검토 필요 사유 요약",
#       "suggested_text": "원문을 대체할 수 있는 완성된 수정안 후보 문장",
#       "revision_reason": "수정안 제안 이유",
#       "legal_basis": []
#     }}
#   ]
# }}
# """

#     response = llm.invoke(prompt)

#     parsed = safe_parse_json(response.content, default={})

#     if not isinstance(parsed, dict):
#         parsed = {}

#     revised_issues = parsed.get("revised_issues", [])

#     if not isinstance(revised_issues, list):
#         revised_issues = []

#     source_map = {
#         item.get("issue_id"): item
#         for item in highlighted_issues
#         if isinstance(item, dict)
#     }

#     normalized = []

#     for idx, item in enumerate(revised_issues, start=1):
#         if not isinstance(item, dict):
#             continue

#         issue_id = item.get("issue_id", idx)
#         source_item = source_map.get(issue_id, {})

#         legal_basis = item.get("legal_basis", [])

#         if not isinstance(legal_basis, list):
#             legal_basis = []

#         suggested_text = clean_text(item.get("suggested_text", ""))

#         if not suggested_text:
#             suggested_text = "검토 필요"

#         normalized.append(
#             {
#                 "issue_id": issue_id,
#                 "highlight_text": clean_text(
#                     item.get(
#                         "highlight_text",
#                         source_item.get("highlight_text", ""),
#                     )
#                 ),
#                 "issue_summary": clean_text(
#                     item.get(
#                         "issue_summary",
#                         source_item.get("issue_summary", ""),
#                     )
#                 ),
#                 "suggested_text": suggested_text,
#                 "revision_reason": clean_text(
#                     item.get("revision_reason", "")
#                 ),
#                 "legal_basis": legal_basis,
#                 "evidence": source_item.get("evidence", []),
#             }
#         )

#     return {
#         "revised_issues": normalized,
#     }

import json
import re

from app.utils.llm_client import get_llm
from app.utils.agent_utils import safe_parse_json, clean_text

MAX_ISSUES_FOR_REVISION = 5


BAD_SUGGESTION_PATTERNS = [
    r"하십시오",
    r"하세요",
    r"수정하",
    r"명확히 하",
    r"제시하",
    r"검토하",
    r"표기하",
    r"보완하",
]


def is_invalid_suggested_text(text: str) -> bool:
    if not text or text == "검토 필요":
        return True

    return any(re.search(pattern, text) for pattern in BAD_SUGGESTION_PATTERNS)


def build_legal_basis_from_evidence(evidence: list, limit: int = 3) -> list:
    if not isinstance(evidence, list):
        return []

    legal_basis = []

    for ev in evidence[:limit]:
        if not isinstance(ev, dict):
            continue

        legal_basis.append(
            {
                "source": ev.get("source", ""),
                "page": ev.get("page", None),
                "article": ev.get("article", ""),
                "content": ev.get("content", ""),
            }
        )

    return legal_basis


def run_revision_agent(state: dict) -> dict:
    highlighted_issues = state.get("highlighted_issues", [])
    highlighted_issues = highlighted_issues[:MAX_ISSUES_FOR_REVISION]

    llm = get_llm()

#     prompt = f"""
# 당신은 준법 문서 수정 지원 시스템의 Revision Agent입니다.

# 역할:
# - 입력으로 받은 highlight_text를 대체할 수 있는 수정안 후보를 작성합니다.
# - 최종 위반 여부를 판정하지 않습니다.
# - 법령 해석, 위반 확률, 심각도 점수, 리스크 점수는 생성하지 않습니다.

# 중요:
# - suggested_text는 반드시 원문 highlight_text를 대체할 수 있는 완성된 문장이어야 합니다.
# - suggested_text에는 설명문, 지시문, 검토 요청 문장을 쓰지 마세요.
# - suggested_text는 실제 문서에 바로 삽입 가능한 광고/안내 문구여야 합니다.
# - 근거가 부족하면 suggested_text는 "검토 필요"로 작성하세요.
# - legal_basis는 생성하지 마세요. 빈 배열 []로 두세요.
# - 법령이나 조항을 새로 만들지 마세요.
# - evidence.content를 요약하거나 재해석하지 마세요.

# suggested_text 금지 표현:
# - "...하십시오"
# - "...하세요"
# - "...수정하십시오"
# - "...명확히 하십시오"
# - "...근거를 제시하십시오"
# - "...검토가 필요합니다"

# 좋은 예:
# 원문: "누구나 연 12%의 확정 수익을 받을 수 있습니다."
# suggested_text: "예상 수익률은 시장 상황에 따라 변동될 수 있으며 원금 손실이 발생할 수 있습니다."

# 나쁜 예:
# suggested_text: "수익률이 확정적임을 명확히 하거나 기대 수익임을 표기하십시오."

# 입력 데이터:
# {json.dumps(highlighted_issues, ensure_ascii=False, indent=2)}

# 반드시 JSON 객체로만 답하세요.
# 마크다운 코드블록을 쓰지 마세요.
# 설명 문장을 쓰지 마세요.

# 출력 형식:
# {{
#   "revised_issues": [
#     {{
#       "issue_id": 1,
#       "highlight_text": "원문 하이라이트 문장",
#       "issue_summary": "검토 필요 사유 요약",
#       "suggested_text": "원문을 대체할 수 있는 완성된 수정안 후보 문장",
#       "revision_reason": "수정안 제안 이유",
#       "legal_basis": []
#     }}
#   ]
# }}
# """

        prompt = f"""
당신은 금융광고 문구 수정 전문가다.

문제 문장과 관련 근거를 참고하여
소비자 오인 가능성을 줄이는 수정안을 작성하라.

반드시 JSON 형식으로 출력하라.

original_text에는
문제 문장을 수정하지 말고
입력된 문제 문장을 그대로 복사하여 넣어라.

suggested_text에는
실제 수정된 문장을 작성하라.

예시:

{{
  "original_text":"...",
  "problem_reason":"...",
  "suggested_text":"..."
}}

문제 문장:

{issue["highlight_text"]}

문제 사유:

{issue["issue_summary"]}

관련 근거:

{evidence_text}
"""

    response = llm.invoke(prompt)

    parsed = safe_parse_json(response.content, default={})

    if not isinstance(parsed, dict):
        parsed = {}

    revised_issues = parsed.get("revised_issues", [])

    if not isinstance(revised_issues, list):
        revised_issues = []

    source_map = {
        item.get("issue_id"): item
        for item in highlighted_issues
        if isinstance(item, dict)
    }

    normalized = []

    for idx, item in enumerate(revised_issues, start=1):
        if not isinstance(item, dict):
            continue

        issue_id = item.get("issue_id", idx)
        source_item = source_map.get(issue_id, {})

        highlight_text = clean_text(
            item.get(
                "highlight_text",
                source_item.get("highlight_text", ""),
            )
        )

        issue_summary = clean_text(
            item.get(
                "issue_summary",
                source_item.get("issue_summary", ""),
            )
        )

        suggested_text = clean_text(item.get("suggested_text", ""))

        if is_invalid_suggested_text(suggested_text):
            suggested_text = "검토 필요"

        evidence = source_item.get("evidence", [])
        legal_basis = build_legal_basis_from_evidence(evidence)

        normalized.append(
            {
                "issue_id": issue_id,
                "highlight_text": highlight_text,
                "issue_summary": issue_summary,
                "suggested_text": suggested_text,
                "revision_reason": clean_text(item.get("revision_reason", "")),
                "legal_basis": legal_basis,
                "evidence": evidence,
            }
        )

    return {
        "revised_issues": normalized,
    }