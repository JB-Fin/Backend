import json

from app.utils.agent_utils import safe_parse_json
from app.utils.llm_client import get_llm

MAX_REPORT_INPUT_CHARS = 15000
SKIP_REPLACEMENT_TEXTS = {
    "",
    "검토 필요",
    "담당자 추가 검토 필요",
}

def run_report_agent(state: dict) -> dict:
    revised_issues = state.get("revised_issues", [])
    target_text = state.get("target_text", "")

    revised_document = build_revised_document(
        target_text=target_text,
        revised_issues=revised_issues,
    )

    document_info = state.get("document_info") or {
        "file_id": state.get("file_id"),
        "file_name": state.get("file_name"),
        "language": state.get("language"),
        "regulation_scope": state.get("regulation_scope"),
    }

    report_input = {
        "document_info": document_info,
        "revised_issues": revised_issues,
        "revised_document": revised_document,
    }

    llm = get_llm()

    prompt = f"""
당신은 금융회사 법무팀 및 준법감시인을 지원하는
FAQ Assistant다.

반드시 제공된 문서 내용만 근거로 답변하라.

답변 원칙

1. 문서에서 확인되는 내용만 답변하라.

2. 문서에 없는 내용은 추측하지 마라.

3. 근거가 부족하거나 확인할 수 없는 경우

"현재 제공된 규정만으로는 판단하기 어렵습니다."

라고 답하라.

4. 최종 법률 판단을 하지 마라.

5. 관련 규정명 또는 조항이 확인되는 경우 함께 제시하라.

6. 필요한 경우 검토 포인트를 제시할 수 있다.

검토 데이터:

{json.dumps(report_input, ensure_ascii=False, indent=2)[:MAX_REPORT_INPUT_CHARS]}
"""

    response = llm.invoke(prompt)

    report = safe_parse_json(response.content, default={})

    if not isinstance(report, dict):
        report = {}

    report.setdefault("summary", {})
    report["summary"]["total_items"] = len(revised_issues)
    report["summary"]["total_issues"] = len(revised_issues)

    return {
        "report": report,
        "revised_document": revised_document,
    }

def build_revised_document(
    target_text: str,
    revised_issues: list[dict],
) -> str:
    revised_text = target_text or ""

    for item in revised_issues:
        original = (
            item.get("original_text")
            or item.get("highlight_text")
            or ""
        )

        suggested = item.get("suggested_text", "")

        if not original:
            continue

        if suggested in SKIP_REPLACEMENT_TEXTS:
            continue

        if original not in revised_text:
            continue

        revised_text = revised_text.replace(original, suggested)

    return revised_text