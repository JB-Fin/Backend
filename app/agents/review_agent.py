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
당신은 준법 검토 지원 시스템의 Review Agent입니다.

중요:
- 당신은 최종 위반 여부를 판정하지 않습니다.
- 심각도 점수, 리스크 점수, 위반 확률을 생성하지 않습니다.
- 설명 가능한 AI를 위해 문서에서 "검토가 필요한 후보 문장"만 추출합니다.
- 후보는 최대 {TOP_N_ISSUES}개만 반환합니다.
- 각 후보는 원문에 실제로 존재하는 문장이어야 합니다.
- 법령 내용을 지어내지 마세요.

참고 근거:
{evidence_pool}

반드시 JSON 배열로만 답하세요.
마크다운 코드블록을 쓰지 마세요.
설명 문장을 쓰지 마세요.
반드시 [ 로 시작하고 ] 로 끝나는 JSON 배열만 출력하세요.

출력 형식:
[
  {{
    "issue_id": 1,
    "highlight_text": "원문에서 하이라이트할 문장",
    "issue_summary": "검토 필요 사유 요약",
    "review_focus": "어떤 기준과 대조 검토가 필요한지",
    "revision_guideline": "수정 방향 제안"
  }}
]

[검토 대상 문서]
{target_text[:MAX_TARGET_CHARS]}
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