import json

from app.utils.llm_client import get_llm
from app.utils.agent_utils import safe_parse_json, clean_text

MAX_ISSUES_FOR_REVISION = 5

def run_revision_agent(state: dict) -> dict:
    highlighted_issues = state.get("highlighted_issues", [])
    highlighted_issues = highlighted_issues[:MAX_ISSUES_FOR_REVISION]
    llm = get_llm()
    prompt = f"""
당신은 준법 문서 수정 지원 시스템의 Revision Agent입니다.
중요:
- 당신은 최종 위반 여부를 판정하지 않습니다.
- 심각도 점수, 위반 확률, 리스크 점수를 생성하지 않습니다.
- 입력으로 받은 하이라이트 문장과 근거를 바탕으로 "수정안 후보"만 제안합니다.
- 수정안은 Human Reviewer가 채택 또는 반려할 수 있는 제안입니다.
- suggested_text에는 설명문이 아니라 문서에 바로 넣을 수 있는 문장만 작성하세요.
- 근거가 부족하면 suggested_text는 "검토 필요"로 작성하세요.
입력 데이터:
{json.dumps(highlighted_issues, ensure_ascii=False, indent=2)}
반드시 JSON 객체로만 답하세요.
출력 형식:
{{
  "revised_issues": [
    {{
      "issue_id": 1,
      "highlight_text": "원문 하이라이트 문장",
      "issue_summary": "검토 필요 사유 요약",
      "suggested_text": "수정안 후보",
      "revision_reason": "수정안 제안 이유",
      "legal_basis": [
        {{
          "source": "근거 문서명",
          "page": 1,
          "article": "",
          "content": "근거 내용 요약"
        }}
      ],
      "human_review_required": true
    }}
  ]
}}
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
        legal_basis = item.get("legal_basis", [])
        if not isinstance(legal_basis, list):
            legal_basis = []
        normalized.append(
            {
                "issue_id": issue_id,
                "highlight_text": clean_text(
                    item.get("highlight_text", source_item.get("highlight_text", ""))
                ),
                "issue_summary": clean_text(
                    item.get("issue_summary", source_item.get("issue_summary", ""))
                ),
                "suggested_text": clean_text(item.get("suggested_text", "")),
                "revision_reason": clean_text(item.get("revision_reason", "")),
                "legal_basis": legal_basis,
                "evidence": source_item.get("evidence", []),
                "human_review_required": True,
            }
        )
    state["revised_issues"] = normalized
    return state