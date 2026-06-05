import json, os, itertools, threading

from datetime import datetime, timezone
from pathlib import Path
from fastapi import HTTPException
# from openai import OpenAI

from app.services.file_service import get_file_by_id
from app.services.report_service import create_reports

# client = OpenAI()  
# MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
SUPPORTED_REPORT_FORMATS = {"pdf", "docx", "txt"}

# UPLOAD_DIR = Path("uploads")
# MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

REVIEWS_DB = []
REVIEW_ID_SEQ = 1

_lock = threading.Lock()
_id_counter = itertools.count(1)

def analyze_review(file_id: int, language: str, regulation_scope: str):
    file_info = get_file_by_id(file_id)
    file_name = (
        file_info.get("file_name")
        or file_info.get("original_filename")
        or file_info.get("filename")
        or file_info.get("saved_filename")
        or "unknown_file"
    )

    # ── AI 모델 연동 시 주석 해제 ─────────────────────────────────────────────
    # document_text = extract_text(file_info)  # 파일에서 텍스트 추출
    # analysis_result = analyze_document_with_model(
    #     file_name=file_name,
    #     document_text=document_text,
    #     language=language,
    #     regulation_scope=regulation_scope,
    # )
    # summary   = analysis_result["summary"]
    # highlights = analysis_result["highlights"]

    summary = {
        "total_issues": 1,
        "issue_summary_counts": {
            "해지 사유 불명확": 1,
        },
    }
    highlights = [
        {
            "issue_id": 1,
            "page": 1,
            "original_text": "계약 해지는 회사의 재량에 따른다.",
            "issue_summary": "해지 사유가 불명확하여 소비자 보호 관점에서 리스크가 있습니다.",
            "reason": "소비자보호법상 해지 사유는 구체적으로 명시되어야 합니다.",
            "suggested_text": "계약 해지는 제 OO조에 정한 사유에 한하여 가능하다.",
            "revision_detail": "해지 사유, 통지 기간, 이의제기 절차를 명확히 작성해야 합니다.",
        }
    ]
    with _lock:
        review_id = next(_id_counter)
    review = {
        "review_id": review_id,
        "file_id": file_id,
        "file_name": file_name,
        "status": "completed",
        "language": language,
        "regulation_scope": regulation_scope,
        "summary": summary,
        "highlights": highlights,
        "created_at": datetime.now(tz=timezone.utc),
        "report_files": {},
    }
    report_files = create_reports(review)

    review["report_files"] = report_files
    with _lock:
        REVIEWS_DB.append(review)
    
    return review

def analyze_document_with_model(
    file_name: str,
    document_text: str,
    language: str,
    regulation_scope: str,
) -> dict:
    
    """
    AI 모델로 문서를 분석합니다.
    현재는 stub 상태입니다. OpenAI 연동 시 주석을 해제하세요.
    """

# prompt = f"""
    # 당신은 법률 준법 검토 전문가입니다.
    # 아래 문서를 '{regulation_scope}' 규정 범위에 따라 분석하고,
    # 결과를 반드시 JSON 형식으로만 응답하세요.
    #
    # 응답 형식:
    # {{
    #   "summary": {{
    #     "total_issues": 2,
    #     "issue_summary_counts": {{"이슈 제목": 1}}
    #   }},
    #   "highlights": [
    #     {{
    #       "issue_id": 1,
    #       "page": 1,
    #       "original_text": "문제가 되는 원문 텍스트",
    #       "issue_summary": "문제 요약",
    #       "reason": "왜 문제인지 근거",
    #       "suggested_text": "수정 제안 문장",
    #       "revision_detail": "수정 설명"
    #     }}
    #   ]
    # }}
    #
    # 응답 언어: {language}
    # 문서 파일명: {file_name}
    # 문서 내용:
    # {document_text}
    # """
    #
    # response = client.chat.completions.create(
    #     model=MODEL_NAME,
    #     messages=[{"role": "user", "content": prompt}],
    #     response_format={"type": "json_object"},
    # )
    #
    # try:
    #     return json.loads(response.choices[0].message.content)
    # except json.JSONDecodeError as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"AI 모델 응답을 파싱할 수 없습니다: {e}",
    #     )
    
    return {
        "summary": {
            "total_issues": 1,
            "issue_summary_counts": {"해지 사유 불명확": 1},
        },
        "highlights": [
            {
                "issue_id": 1,
                "page": 1,
                "original_text": "계약 해지는 회사의 재량에 따른다.",
                "issue_summary": "해지 사유가 불명확하여 소비자 보호 관점에서 리스크가 있습니다.",
                "reason": "소비자보호법상 해지 사유는 구체적으로 명시되어야 합니다.",
                "suggested_text": "계약 해지는 제 OO조에 정한 사유에 한하여 가능하다.",
                "revision_detail": "해지 사유, 통지 기간, 이의제기 절차를 명확히 작성해야 합니다.",
            }
        ],
    }

def get_reviews() -> list[dict]:
    return REVIEWS_DB

def get_review_by_id(review_id: int) -> dict:
    for review in REVIEWS_DB:
        if review["review_id"] == review_id:
            return review
    raise HTTPException(status_code=404, detail="검토 결과를 찾을 수 없습니다.")

def get_review_highlights(review_id: int) -> list:
    return get_review_by_id(review_id)["highlights"]

def get_review_report_path(review_id: int, file_format: str = "pdf") -> Path:
    review = get_review_by_id(review_id)
    file_format = file_format.lower()
    if file_format not in SUPPORTED_REPORT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"지원하지 않는 보고서 형식입니다. "
                f"{', '.join(sorted(SUPPORTED_REPORT_FORMATS))} 중 하나를 사용하세요."
            ),
        )
    report_files = review.get("report_files")
    if not report_files:
        raise HTTPException(status_code=404, detail="보고서 파일이 없습니다.")
    if file_format not in report_files:
        raise HTTPException(
            status_code=404,
            detail=f"{file_format.upper()} 보고서가 아직 생성되지 않았습니다.",
        )
    report_path = OUTPUT_DIR / report_files[file_format]
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="보고서 파일을 찾을 수 없습니다.")
    return report_path