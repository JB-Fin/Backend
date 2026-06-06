import itertools, threading

from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException,status

from app.services.file_service import get_file_by_id
from app.services.report_service import create_reports
# from app.graphs.review_graph import build_review_graph
from app.graphs.review_graph import review_graph

from app.agents.report_agent import run_report_agent
from app.rag.document_loader import load_file

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_REPORT_FORMATS = {"pdf", "docx", "txt"}

REVIEWS_DB = []

_lock = threading.Lock()
_id_counter = itertools.count(1)

def extract_text_from_file(file_info: dict) -> str:
    file_path = (
        file_info.get("saved_path")
        or file_info.get("storage_path")
        or file_info.get("file_path")
    )

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 경로 정보가 없습니다.",
        )

    docs = load_file(file_path)

    document_text = "\n\n".join(
        doc.page_content
        for doc in docs
        if doc.page_content and doc.page_content.strip()
    )

    if not document_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="문서에서 텍스트를 추출할 수 없습니다.",
        )

    return document_text

def analyze_review(file_id: int, language: str, regulation_scope: str):
    try:
        file_info = get_file_by_id(file_id)

        file_name = (
            file_info.get("file_name")
            or file_info.get("original_filename")
            or file_info.get("filename")
            or file_info.get("saved_filename")
            or "unknown_file"
        )

        document_text = extract_text_from_file(file_info)

        state = {
            "file_id": file_id,
            "file_name": file_name,
            "language": language,
            "regulation_scope": regulation_scope,
            "target_text": document_text,
        }

        state = review_graph.invoke(state)

        with _lock:
            review_id = next(_id_counter)

        report = state["report"]

        review = {
            "review_id": review_id,
            "file_id": file_id,
            "file_name": file_name,
            "status": "completed",
            "language": language,
            "regulation_scope": regulation_scope,
            "summary": report.get("summary", {}),
            "highlights": state.get("revised_issues", []),
            "report": report,
            "created_at": datetime.now(tz=timezone.utc),
            "report_files": {},
        }

        review["report_files"] = create_reports(review)

        with _lock:
            REVIEWS_DB.append(review)

        return review

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 검토 처리 중 오류가 발생했습니다: {str(e)}",
        )

def get_reviews() -> list[dict]:
    return REVIEWS_DB


def get_review_by_id(review_id: int) -> dict:
    for review in REVIEWS_DB:
        if review["review_id"] == review_id:
            return review

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="검토 결과를 찾을 수 없습니다.",
    )


def get_review_highlights(review_id: int) -> list:
    review = get_review_by_id(review_id)
    return review.get("highlights", [])


def get_review_report_path(review_id: int, file_format: str = "pdf") -> Path:
    review = get_review_by_id(review_id)

    file_format = file_format.lower()

    if file_format not in SUPPORTED_REPORT_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"지원하지 않는 보고서 형식입니다. "
                f"{', '.join(sorted(SUPPORTED_REPORT_FORMATS))} 중 하나를 사용하세요."
            ),
        )

    report_files = review.get("report_files")

    if not report_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보고서 파일이 없습니다.",
        )

    if file_format not in report_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{file_format.upper()} 보고서가 아직 생성되지 않았습니다.",
        )

    report_path = OUTPUT_DIR / report_files[file_format]

    if not report_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="보고서 파일을 찾을 수 없습니다.",
        )

    return report_path