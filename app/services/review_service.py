# import itertools, threading

# from datetime import datetime, timezone
# from pathlib import Path

# from fastapi import HTTPException,status

# from app.services.file_service import get_file_by_id
# from app.services.report_service import create_reports
# import app.graphs.review_graph
# from app.rag.document_loader import load_file
# from app.rag.vector_store import build_vectorstore

# OUTPUT_DIR = Path("outputs")
# OUTPUT_DIR.mkdir(exist_ok=True)

# REGULATION_DIR = Path("regulations")

# SUPPORTED_REPORT_FORMATS = {"pdf", "docx", "txt"}
# SUPPORTED_REGULATION_EXTENSIONS = {".pdf", ".docx", ".txt"}

# REVIEWS_DB: list[dict] = []

# _lock = threading.Lock()
# _id_counter = itertools.count(1)

# def extract_text_from_file(file_info: dict) -> str:
#     file_path = (
#         file_info.get("saved_path")
#         or file_info.get("storage_path")
#         or file_info.get("file_path")
#     )
#     if not file_path:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="파일 경로 정보가 없습니다.",
#         )
#     docs = load_file(file_path)
#     document_text = "\n\n".join(
#         doc.page_content
#         for doc in docs
#         if doc.page_content and doc.page_content.strip()
#     )
#     if not document_text.strip():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="문서에서 텍스트를 추출할 수 없습니다.",
#         )
#     return document_text

# def get_regulation_paths() -> list[str]:
#     if not REGULATION_DIR.exists():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="regulations 폴더가 없습니다. 프로젝트 루트에 regulations 폴더를 생성하세요.",
#         )
#     regulation_paths = [
#         str(file_path)
#         for file_path in REGULATION_DIR.iterdir()
#         if file_path.is_file()
#         and file_path.suffix.lower() in SUPPORTED_REGULATION_EXTENSIONS
#     ]
#     if not regulation_paths:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="regulations 폴더에 규정 문서가 없습니다. pdf, docx, txt 파일을 추가하세요.",
#         )
#     return regulation_paths

# def normalize_summary(summary: dict | None, highlights: list[dict]) -> dict:
#     if not isinstance(summary, dict):
#         summary = {}
#     issue_summary_counts = summary.get("issue_summary_counts")
#     if not isinstance(issue_summary_counts, dict):
#         issue_summary_counts = {}
#     return {
#         "total_issues": summary.get("total_issues", len(highlights)),
#         "issue_summary_counts": issue_summary_counts,
#     }

# def normalize_highlight(item: dict, index: int) -> dict:
#     if not isinstance(item, dict):
#         item = {}
#     legal_basis = item.get("legal_basis", [])
#     evidence = item.get("evidence", [])
#     if not isinstance(legal_basis, list):
#         legal_basis = []
#     if not isinstance(evidence, list):
#         evidence = []
#     return {
#         "issue_id": item.get("issue_id", index + 1),
#         "page": item.get("page"),
#         "original_text": (
#             item.get("original_text") or item.get("highlight_text") or ""
#         ),
#         "issue_summary": item.get("issue_summary", ""),
#         "reason": (
#             item.get("reason") or item.get("revision_reason") or ""
#         ),
#         "suggested_text": item.get("suggested_text", ""),
#         "revision_detail": (
#             item.get("revision_detail")
#             or item.get("revision_reason")
#             or item.get("reason")
#             or ""
#         ),
#         "legal_basis": legal_basis,
#         "evidence": evidence,
#     }

# def normalize_highlights(raw_highlights: list | None) -> list[dict]:
#     if not isinstance(raw_highlights, list):
#         return []
#     return [normalize_highlight(item, i) for i, item in enumerate(raw_highlights)]

# def run_analyze_background(review_id: int, file_id: int, language: str, regulation_scope: str):
#     """
#     BackgroundTasks에서 실행되는 실제 분석 함수.
#     완료/실패 여부를 REVIEWS_DB의 status 필드에 기록한다.
#     """
#     def _update_status(status_val: str, **extra):
#         with _lock:
#             for review in REVIEWS_DB:
#                 if review["review_id"] == review_id:
#                     review["status"] = status_val
#                     review.update(extra)
#                     break
#     try:
#         file_info = get_file_by_id(file_id)
#         file_name = (
#             file_info.get("file_name")
#             or file_info.get("original_filename")
#             or file_info.get("filename")
#             or file_info.get("saved_filename")
#             or "unknown_file"
#         )
#         document_text = extract_text_from_file(file_info)
#         regulation_paths = get_regulation_paths()
#         vectorstore, regulation_doc_count, regulation_chunk_count = build_vectorstore(regulation_paths)
#         state = {
#             "file_id": file_id,
#             "file_name": file_name,
#             "language": language,
#             "regulation_scope": regulation_scope,
#             "target_text": document_text,
#             "vectorstore": vectorstore,
#             "document_info": {
#                 "file_id": file_id,
#                 "file_name": file_name,
#                 "regulation_scope": regulation_scope,
#                 "language": language,
#                 "regulation_files": [Path(p).name for p in regulation_paths],
#                 "regulation_doc_count": regulation_doc_count,
#                 "regulation_chunk_count": regulation_chunk_count,
#                 "target_text_length": len(document_text),
#             },
#         }
#         # LLM 호출 (블로킹이지만 백그라운드 스레드에서 실행되므로 타임아웃 무관)
#         state = app.graphs.review_graph.review_graph.invoke(state)
#         report = state.get("report", {})
#         raw_highlights = state.get("revised_issues", [])
#         highlights = normalize_highlights(raw_highlights)
#         summary = normalize_summary(report.get("summary", {}), highlights)
#         # 임시로 만들어둔 review dict에 결과 채워넣기
#         partial_review = {
#             "file_name": file_name,
#             "status": "completed",
#             "summary": summary,
#             "highlights": highlights,
#             "report": report,
#             "revised_document": state.get("revised_document", ""),
#             "document_info": state.get("document_info", {}),
#             "report_files": {},
#         }
#         # 보고서 파일 생성을 위해 review_id 포함 전체 dict 구성
#         full_review = {
#             "review_id": review_id,
#             "file_id": file_id,
#             "language": language,
#             "regulation_scope": regulation_scope,
#             "created_at": datetime.now(tz=timezone.utc),
#             **partial_review,
#         }
#         full_review["report_files"] = create_reports(full_review)
#         _update_status("completed", **{k: v for k, v in full_review.items() if k != "review_id"})
#     except Exception as e:
#         _update_status("failed", error_detail=str(e))

# def create_pending_review(file_id: int, language: str, regulation_scope: str) -> dict:
#     """
#     즉시 pending 상태의 review를 생성하고 반환한다.
#     실제 분석은 BackgroundTasks가 run_analyze_background()를 호출해 처리한다.
#     """
#     with _lock:
#         review_id = next(_id_counter)
#         review = {
#             "review_id": review_id,
#             "file_id": file_id,
#             "file_name": None,
#             "status": "pending",           # ← 프론트가 폴링할 상태값
#             "language": language,
#             "regulation_scope": regulation_scope,
#             "summary": {},
#             "highlights": [],
#             "report": {},
#             "revised_document": "",
#             "created_at": datetime.now(tz=timezone.utc),
#             "document_info": {},
#             "report_files": {},
#             "error_detail": None,
#         }
#         REVIEWS_DB.append(review)
#     return review

# def get_reviews() -> list[dict]:
#     return REVIEWS_DB

# def get_review_by_id(review_id: int) -> dict:
#     for review in REVIEWS_DB:
#         if review["review_id"] == review_id:
#             return review
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="검토 결과를 찾을 수 없습니다.",
#     )

# def get_review_highlights(review_id: int) -> list:
#     review = get_review_by_id(review_id)
#     return review.get("highlights", [])

# def get_review_report_path(review_id: int, file_format: str = "pdf") -> Path:
#     review = get_review_by_id(review_id)
#     file_format = file_format.lower()
#     if file_format not in SUPPORTED_REPORT_FORMATS:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=(
#                 f"지원하지 않는 보고서 형식입니다. "
#                 f"{', '.join(sorted(SUPPORTED_REPORT_FORMATS))} 중 하나를 사용하세요."
#             ),
#         )
#     if review.get("status") != "completed":
#         raise HTTPException(
#             status_code=status.HTTP_202_ACCEPTED,
#             detail="아직 분석이 완료되지 않았습니다.",
#         )
#     report_files = review.get("report_files")
#     if not report_files:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="보고서 파일이 없습니다.",
#         )
#     if file_format not in report_files:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"{file_format.upper()} 보고서가 아직 생성되지 않았습니다.",
#         )
#     report_path = OUTPUT_DIR / report_files[file_format]
#     if not report_path.exists():
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="보고서 파일을 찾을 수 없습니다.",
#         )
#     return report_path

import itertools, threading, logging

from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, status

from app.services.file_service import get_file_by_id
from app.services.report_service import create_reports
from app.graphs.review_graph import review_graph
from app.rag.document_loader import load_file
from app.rag.vector_store import build_vectorstore

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("review_service")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

REGULATION_DIR = Path("regulations")

SUPPORTED_REPORT_FORMATS = {"pdf", "docx", "txt"}
SUPPORTED_REGULATION_EXTENSIONS = {".pdf", ".docx", ".txt"}

REVIEWS_DB: list[dict] = []

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

    logger.debug("[텍스트 추출] 파일 경로: %s", file_path)

    docs = load_file(file_path)
    logger.debug("[텍스트 추출] load_file 완료 - 페이지 수: %d", len(docs))

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

    logger.debug("[텍스트 추출] 완료 - 총 문자 수: %d", len(document_text))
    return document_text


def get_regulation_paths() -> list[str]:
    if not REGULATION_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="regulations 폴더가 없습니다.",
        )

    regulation_paths = [
        str(file_path)
        for file_path in REGULATION_DIR.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_REGULATION_EXTENSIONS
    ]

    if not regulation_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="regulations 폴더에 규정 문서가 없습니다.",
        )

    logger.debug("[규정 로드] 발견된 규정 파일: %s", regulation_paths)
    return regulation_paths


def normalize_summary(summary: dict | None, highlights: list[dict]) -> dict:
    if not isinstance(summary, dict):
        summary = {}

    issue_summary_counts = summary.get("issue_summary_counts")
    if not isinstance(issue_summary_counts, dict):
        issue_summary_counts = {}

    return {
        "total_issues": summary.get("total_issues", len(highlights)),
        "issue_summary_counts": issue_summary_counts,
    }


def normalize_highlight(item: dict, index: int) -> dict:
    if not isinstance(item, dict):
        item = {}

    legal_basis = item.get("legal_basis", [])
    evidence = item.get("evidence", [])

    if not isinstance(legal_basis, list):
        legal_basis = []
    if not isinstance(evidence, list):
        evidence = []

    return {
        "issue_id": item.get("issue_id", index + 1),
        "page": item.get("page"),
        "original_text": (
            item.get("original_text") or item.get("highlight_text") or ""
        ),
        "issue_summary": item.get("issue_summary", ""),
        "reason": (
            item.get("reason") or item.get("revision_reason") or ""
        ),
        "suggested_text": item.get("suggested_text", ""),
        "revision_detail": (
            item.get("revision_detail")
            or item.get("revision_reason")
            or item.get("reason")
            or ""
        ),
        "legal_basis": legal_basis,
        "evidence": evidence,
    }


def normalize_highlights(raw_highlights: list | None) -> list[dict]:
    if not isinstance(raw_highlights, list):
        return []
    return [normalize_highlight(item, i) for i, item in enumerate(raw_highlights)]


def run_analyze_background(review_id: int, file_id: int, language: str, regulation_scope: str):
    logger.info("=" * 60)
    logger.info("[STEP 0] 분석 시작 - review_id=%d, file_id=%d", review_id, file_id)
    logger.info("=" * 60)

    def _update_status(status_val: str, **extra):
        with _lock:
            for review in REVIEWS_DB:
                if review["review_id"] == review_id:
                    review["status"] = status_val
                    review.update(extra)
                    break

    try:
        logger.info("[STEP 1] 파일 정보 조회 중 - file_id=%d", file_id)
        file_info = get_file_by_id(file_id)
        logger.info("[STEP 1] 완료 - file_info keys: %s", list(file_info.keys()))

        file_name = (
            file_info.get("file_name")
            or file_info.get("original_filename")
            or file_info.get("filename")
            or file_info.get("saved_filename")
            or "unknown_file"
        )
        logger.info("[STEP 1] 파일명: %s", file_name)

        logger.info("[STEP 2] 텍스트 추출 중...")
        document_text = extract_text_from_file(file_info)
        logger.info("[STEP 2] 완료 - 텍스트 길이: %d자", len(document_text))

        logger.info("[STEP 3] 규정 파일 경로 수집 중...")
        regulation_paths = get_regulation_paths()
        logger.info("[STEP 3] 완료 - 파일 수: %d", len(regulation_paths))

        logger.info("[STEP 4] 벡터스토어 빌드 중...")
        vectorstore, regulation_doc_count, regulation_chunk_count = build_vectorstore(regulation_paths)
        logger.info(
            "[STEP 4] 완료 - 문서 수: %d, 청크 수: %d",
            regulation_doc_count,
            regulation_chunk_count,
        )

        state = {
            "file_id": file_id,
            "file_name": file_name,
            "language": language,
            "regulation_scope": regulation_scope,
            "target_text": document_text,
            "vectorstore": vectorstore,
            "document_info": {
                "file_id": file_id,
                "file_name": file_name,
                "regulation_scope": regulation_scope,
                "language": language,
                "regulation_files": [Path(p).name for p in regulation_paths],
                "regulation_doc_count": regulation_doc_count,
                "regulation_chunk_count": regulation_chunk_count,
                "target_text_length": len(document_text),
            },
        }

        logger.info("[STEP 5] review_graph.invoke() 시작 - LLM 호출 구간")
        graph_start = datetime.now()

        state = review_graph.invoke(state)

        elapsed = (datetime.now() - graph_start).total_seconds()
        logger.info("[STEP 5] 완료 - 소요 시간: %.1f초", elapsed)
        logger.debug("[STEP 5] state keys: %s", list(state.keys()))

        logger.info("[STEP 6] 결과 정규화 중...")
        report = state.get("report", {})
        raw_highlights = state.get("revised_issues", [])

        logger.debug("[STEP 6] raw_highlights 수: %d", len(raw_highlights) if isinstance(raw_highlights, list) else -1)
        logger.debug("[STEP 6] report keys: %s", list(report.keys()) if isinstance(report, dict) else report)

        highlights = normalize_highlights(raw_highlights)
        summary = normalize_summary(report.get("summary", {}), highlights)
        logger.info("[STEP 6] 완료 - 이슈 수: %d", len(highlights))

        logger.info("[STEP 7] 보고서 파일 생성 중...")
        full_review = {
            "review_id": review_id,
            "file_id": file_id,
            "file_name": file_name,
            "status": "completed",
            "language": language,
            "regulation_scope": regulation_scope,
            "summary": summary,
            "highlights": highlights,
            "report": report,
            "revised_document": state.get("revised_document", ""),
            "created_at": datetime.now(tz=timezone.utc),
            "document_info": state.get("document_info", {}),
            "report_files": {},
        }
        full_review["report_files"] = create_reports(full_review)
        logger.info("[STEP 7] 완료 - 생성된 파일: %s", full_review["report_files"])

        _update_status("completed", **{k: v for k, v in full_review.items() if k != "review_id"})
        logger.info("[STEP 8] DB 저장 완료 - review_id=%d 분석 성공", review_id)
        logger.info("=" * 60)

    except Exception as e:
        logger.exception("[ERROR] review_id=%d 분석 실패 - %s", review_id, str(e))
        _update_status("failed", error_detail=str(e))

def create_pending_review(file_id: int, language: str, regulation_scope: str) -> dict:
    with _lock:
        review_id = next(_id_counter)
        review = {
            "review_id": review_id,
            "file_id": file_id,
            "file_name": None,
            "status": "pending",
            "language": language,
            "regulation_scope": regulation_scope,
            "summary": {},
            "highlights": [],
            "report": {},
            "revised_document": "",
            "created_at": datetime.now(tz=timezone.utc),
            "document_info": {},
            "report_files": {},
            "error_detail": None,
        }
        REVIEWS_DB.append(review)

    logger.info("[create_pending_review] review_id=%d 생성됨", review_id)
    return review


def get_reviews(status_filter: str | None = None) -> list[dict]:
    reviews = REVIEWS_DB

    if status_filter:
        reviews = [
            review for review in reviews
            if review.get("status") == status_filter
        ]

    return reviews

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

    if review.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="아직 분석이 완료되지 않았습니다.",
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
