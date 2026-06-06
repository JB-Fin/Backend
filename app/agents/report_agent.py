import json

from app.utils.agent_utils import safe_parse_json
from app.utils.llm_client import get_llm

MAX_REPORT_INPUT_CHARS = 15000

def run_report_agent(state: dict) -> dict:
    revised_issues = state.get("revised_issues", [])

    document_info = state.get("document_info") or {
        "file_id": state.get("file_id"),
        "file_name": state.get("file_name"),
        "language": state.get("language"),
        "regulation_scope": state.get("regulation_scope"),
    }

    report_input = {
        "document_info": document_info,
        "revised_issues": revised_issues,
    }

    llm = get_llm()

    prompt = f"""
당신은 준법 검토 결과보고서 작성 Agent입니다.

중요:
- AI가 최종 위반 여부를 판정한 것처럼 작성하지 마세요.
- 입력으로 받은 검토 필요 문장과 수정안 후보를 바탕으로 보고서를 작성하세요.
- 보고서는 "준법 검토 지원 결과"의 형태로 작성하세요.
- suggested_text는 최종 확정 문구가 아니라 AI 수정안 후보로 표현하세요.

입력 데이터:
{json.dumps(report_input, ensure_ascii=False, indent=2)[:MAX_REPORT_INPUT_CHARS]}

반드시 JSON 객체로만 답하세요.

출력 형식:
{{
  "review_overview": "검토 개요",
  "overall_opinion": "종합 의견",
  "summary": {{
    "total_items": 0,
    "key_findings": []
  }},
  "detailed_reviews": [
    {{
      "issue_id": 1,
      "highlight_text": "원문",
      "suggested_text": "AI 수정안 후보",
      "legal_basis": [],
      "revision_reason": "수정 이유"
    }}
  ],
  "follow_up_actions": []
}}
"""

    response = llm.invoke(prompt)

    # test #
    print("=== REPORT AGENT RAW RESPONSE ===")
    print(response.content)

    report = safe_parse_json(response.content, default={})

    # test #
    print("=== PARSED REPORT ===")
    print(report)

    if not isinstance(report, dict):
        report = {}

    report.setdefault("summary", {})
    report["summary"]["total_items"] = len(revised_issues)
    report["summary"]["total_issues"] = len(revised_issues)

    state["report"] = report

    return state