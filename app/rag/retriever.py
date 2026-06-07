from typing import Any, List, Dict

from app.utils.agent_utils import clean_text

MAX_EVIDENCE_CONTENT_CHARS = 500

def retrieve_evidence(vectorstore, query: str, k: int = 6,) -> List[Dict[str, Any]]:
    """
    RAG 검색 함수.
    Agent가 아니라 Review Agent를 보조하는 근거 검색 함수.
    """

    docs_with_scores = vectorstore.similarity_search_with_score(query, k=k)

    evidence = []

    for idx, item in enumerate(docs_with_scores, start=1):
        doc, score = item

        evidence.append(
            {
                "evidence_id": idx,
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page"),
                "article": "",
                "content": clean_text(doc.page_content)[:MAX_EVIDENCE_CONTENT_CHARS],
                "retrieval_score": float(score) if score is not None else None,
            }
        )

    return evidence