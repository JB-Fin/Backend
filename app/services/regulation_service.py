import logging
import re
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException, status

logger = logging.getLogger("regulation_search")

REGULATION_DIR = Path("regulations")
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

MAX_CHUNK_CHARS = 2500


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", str(text or ""))


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF 문서를 읽으려면 requirements.txt에 PyMuPDF를 추가하세요.",
        )

    pages = []

    with fitz.open(path) as doc:
        for page_no, page in enumerate(doc, start=1):
            text = page.get_text()
            if text and text.strip():
                pages.append(f"[페이지 {page_no}]\n{text}")

    return "\n\n".join(pages)


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DOCX 문서를 읽으려면 requirements.txt에 python-docx를 추가하세요.",
        )

    doc = Document(path)

    paragraphs = [
        p.text.strip()
        for p in doc.paragraphs
        if p.text and p.text.strip()
    ]

    return "\n".join(paragraphs)


def _read_regulation_file(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return _read_txt(path)

    if suffix == ".pdf":
        return _read_pdf(path)

    if suffix == ".docx":
        return _read_docx(path)

    return ""


def _split_long_chunk(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    text = text.strip()

    if len(text) <= max_chars:
        return [text]

    parts = []
    start = 0

    while start < len(text):
        end = start + max_chars
        parts.append(text[start:end].strip())
        start = end

    return [p for p in parts if p]


def _split_by_article(text: str) -> list[str]:
    text = text.strip()

    if not text:
        return []

    # 제1조(목적), 제 1 조 【목적】, 제1조. 목적, 제1조 목적 등 대응
    chunks = re.split(
        r"(?=제\s*\d+\s*조(?:의\s*\d+)?\s*(?:\(|（|【|\[|\.|\.|\s))",
        text,
    )

    chunks = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]

    if len(chunks) <= 1:
        chunks = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph and paragraph.strip()
        ]

    if not chunks:
        chunks = [text]

    final_chunks = []

    for chunk in chunks:
        final_chunks.extend(_split_long_chunk(chunk))

    return final_chunks


@lru_cache(maxsize=1)
def load_regulations() -> list[dict]:
    if not REGULATION_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="regulations 폴더가 없습니다. 프로젝트 루트에 regulations 폴더를 생성하세요.",
        )

    files = sorted(
        [
            path
            for path in REGULATION_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ],
        key=lambda p: p.name,
    )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="regulations 폴더에 규정 문서가 없습니다. txt, pdf, docx 파일을 추가하세요.",
        )

    regulations = []

    logger.warning("[REGULATION LOAD] file_count=%d", len(files))

    for file_path in files:
        raw_text = _read_regulation_file(file_path)

        if not raw_text.strip():
            logger.warning("[REGULATION LOAD] 텍스트 추출 실패 또는 빈 문서: %s", file_path.name)
            continue

        chunks = _split_by_article(raw_text)

        logger.warning(
            "[REGULATION LOAD] file=%s raw_length=%d chunk_count=%d",
            file_path.name,
            len(raw_text),
            len(chunks),
        )

        for idx, chunk in enumerate(chunks, start=1):
            content = chunk.strip()

            if not content:
                continue

            regulations.append(
                {
                    "regulation_id": f"{file_path.stem}-{idx}",
                    "title": file_path.stem,
                    "source": file_path.name,
                    "page": None,
                    "chunk_index": idx,
                    "content": content,
                }
            )

    logger.warning("[REGULATION LOAD] loaded_chunk_count=%d", len(regulations))

    for i, item in enumerate(regulations[:10], start=1):
        logger.warning(
            "[REGULATION LOAD] sample %d source=%s chunk=%s content=%s",
            i,
            item.get("source"),
            item.get("chunk_index"),
            item.get("content", "")[:200],
        )

    return regulations


def _extract_query_terms(query: str) -> list[str]:
    query = _normalize_text(query)
    compact_query = _compact(query)

    terms = []

    law_names = re.findall(r"[가-힣A-Za-z0-9·\s]+법", query)
    for law_name in law_names:
        law_name = law_name.strip()
        if law_name:
            terms.append(law_name)
            terms.append(_compact(law_name))

    articles = re.findall(r"제\s*\d+\s*조(?:의\s*\d+)?", query)
    for article in articles:
        terms.append(_compact(article))

    # 자주 나오는 조사 제거
    cleaned_query = re.sub(r"[^\w가-힣]", " ", query)
    for term in re.split(r"\s+", cleaned_query):
        term = term.strip()
        if len(term) >= 2:
            terms.append(term)

    # 특정 질문 보정
    if "금융소비자보호법" in compact_query:
        terms.extend(["금융소비자보호법", "금융소비자", "소비자보호"])

    if "개인정보보호법" in compact_query:
        terms.extend(["개인정보보호법", "개인정보"])

    if "목적" in query:
        terms.append("목적")

    deduped = []

    for term in terms:
        if term and term not in deduped:
            deduped.append(term)

    return deduped


def _score_regulation(query: str, item: dict) -> int:
    title = str(item.get("title", ""))
    source = str(item.get("source", ""))
    regulation_id = str(item.get("regulation_id", ""))
    content = str(item.get("content", ""))

    text = _normalize_text(f"{title} {source} {regulation_id} {content}")
    compact_text = _compact(text)
    compact_title = _compact(title)
    compact_source = _compact(source)
    compact_query = _compact(query)

    terms = _extract_query_terms(query)

    score = 0

    for term in terms:
        compact_term = _compact(term)

        if not compact_term:
            continue

        if compact_term in compact_text:
            score += 3

        if compact_term in compact_title:
            score += 8

        if compact_term in compact_source:
            score += 8

    article_match = re.search(r"제\s*(\d+)\s*조", query)
    if article_match:
        article = f"제{article_match.group(1)}조"
        if article in compact_text:
            score += 30

    if "목적" in query and "목적" in text:
        score += 20

    if "금융소비자보호법" in compact_query:
        if "금융소비자보호법" in compact_text:
            score += 40
        if "금융소비자보호" in compact_source or "금융소비자보호" in compact_title:
            score += 25

    if "개인정보보호법" in compact_query:
        if "개인정보보호법" in compact_text:
            score += 40
        if "개인정보보호" in compact_source or "개인정보보호" in compact_title:
            score += 25

    return score


def search_regulations(query: str, language: str = "ko", top_k: int = 12):
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검색어를 입력해야 합니다.",
        )

    if top_k <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_k는 1 이상이어야 합니다.",
        )

    regulations = load_regulations()

    logger.warning("[SEARCH DEBUG] query=%s", query)
    logger.warning("[SEARCH DEBUG] total_chunks=%d", len(regulations))

    scored_results = []

    for item in regulations:
        score = _score_regulation(query, item)

        if score > 0:
            scored_results.append(
                {
                    **item,
                    "score": score,
                    "search_type": "keyword",
                }
            )

    scored_results.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 관련 점수가 있는 chunk 우선
    results = scored_results[:top_k]

    # 그래도 검색 결과가 없으면 전체 문서의 앞 chunk들을 fallback으로 제공
    if not results:
        logger.warning("[SEARCH DEBUG] keyword match 없음. regulations 전체 앞부분 fallback 사용")
        results = [
            {
                **item,
                "score": 0,
                "search_type": "fallback_all_documents",
            }
            for item in regulations[:top_k]
        ]

    logger.warning("[SEARCH DEBUG] matched_count=%d", len(results))

    for i, item in enumerate(results, start=1):
        logger.warning(
            "[SEARCH DEBUG] result %d score=%s source=%s chunk=%s content=%s",
            i,
            item.get("score"),
            item.get("source"),
            item.get("chunk_index"),
            item.get("content", "")[:300],
        )

    return {
        "query": query.strip(),
        "language": language,
        "top_k": top_k,
        "results": results,
    }