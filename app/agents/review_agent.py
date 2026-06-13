from app.rag.retriever import retrieve_evidence
from app.utils.agent_utils import (
    clean_text,
    safe_parse_json,
    dedupe_by_highlight_text,
    compact_evidence,
)
from app.utils.llm_client import get_llm

TOP_N_ISSUES = 5
MAX_TARGET_CHARS = 12000


def run_review_agent(state: dict) -> dict:
    target_text = state["target_text"]
    vectorstore = state.get("vectorstore")

    if vectorstore is None:
        evidence_pool = []
    else:
        evidence_pool = retrieve_evidence(
            vectorstore=vectorstore,
            query=target_text,
            k=6,
        )

    evidence_pool = compact_evidence(evidence_pool)

    llm = get_llm()

    prompt = f"""
당신은 금융광고 준법 검토 전문가다.

광고 문안을 검토하여
위반 가능성이 있는 문장을
최대 {TOP_N_ISSUES}개 찾아라.

반드시 JSON 배열로만 출력하라.

예시:

[
 {{
   "highlight_text":"본 상품은 원금이 100% 보장됩니다.",
   "issue_summary":"원금보장 표현으로 소비자 오인 가능성 존재"
 }}
]

광고 문안:

{target_text}
"""

    response = llm.invoke(prompt)
    candidates = safe_parse_json(response.content, default=[])

    if not isinstance(candidates, list):
        candidates = []

    highlighted_issues = []

    for idx, item in enumerate(candidates[:TOP_N_ISSUES], start=1):
        if not isinstance(item, dict):
            continue

        highlight_text = clean_text(item.get("highlight_text", ""))
        issue_summary = clean_text(item.get("issue_summary", ""))
        review_focus = clean_text(item.get("review_focus", ""))
        revision_guideline = clean_text(item.get("revision_guideline", ""))

        if not highlight_text:
            continue

        issue_evidence = evidence_pool

        if vectorstore is not None:
            issue_evidence = retrieve_evidence(
                vectorstore=vectorstore,
                query=f"{highlight_text}\n{issue_summary}\n{review_focus}",
                k=6,
            )
            issue_evidence = compact_evidence(issue_evidence)

        highlighted_issues.append(
            {
                "issue_id": idx,
                "highlight_text": highlight_text,
                "issue_summary": issue_summary,
                "review_focus": review_focus,
                "revision_guideline": revision_guideline,
                "evidence": issue_evidence,
            }
        )

    highlighted_issues = dedupe_by_highlight_text(highlighted_issues)

    return {
        "highlighted_issues": highlighted_issues,
    }