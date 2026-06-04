from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

from app.services.file_service import get_file_by_id
from app.services.report_service import create_reports

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

REVIEWS_DB = []
REVIEW_ID_SEQ = 1


def analyze_review(file_id: int, language: str, regulation_scope: str):
    global REVIEW_ID_SEQ

    file_info = get_file_by_id(file_id)

    file_name = (
        file_info.get("file_name")
        or file_info.get("original_filename")
        or file_info.get("filename")
        or file_info.get("saved_filename")
        or "unknown_file"
    )

    review = {
        "review_id": REVIEW_ID_SEQ,
        "file_id": file_id,
        "status": "COMPLETED",
        "language": language,
        "summary": f"{file_name} 문서에 대한 준법 리스크 검토가 완료되었습니다.",
        "risk_level": "MEDIUM",
        "highlights": [
            {
                "page": 1,
                "original_text": "계약 해지는 회사의 재량에 따른다.",
                "issue": "해지 사유가 불명확하여 소비자 보호 관점에서 리스크가 있습니다.",
                "suggestion": "해지 사유, 통지 기간, 이의제기 절차를 명확히 작성해야 합니다.",
                "risk_level": "HIGH",
            }
        ],
        "created_at": datetime.now(),
        "report_file_name": f"review_{REVIEW_ID_SEQ}_report.txt",
    }

    report_path = OUTPUT_DIR / review["report_file_name"]
    report_path.write_text(
        f"""준법 리스크 검토 보고서

문서 ID: {file_id}
파일명: {file_name}
검토 언어: {language}
규정 범위: {regulation_scope}
위험도: {review['risk_level']}

요약:
{review['summary']}

수정 필요 사항:
- 원문: {review['highlights'][0]['original_text']}
- 이슈: {review['highlights'][0]['issue']}
- 제안: {review['highlights'][0]['suggestion']}
""",
        encoding="utf-8",
    )

    REVIEWS_DB.append(review)
    REVIEW_ID_SEQ += 1

    return review


def get_reviews():
    return REVIEWS_DB


def get_review_by_id(review_id: int):
    for review in REVIEWS_DB:
        if review["review_id"] == review_id:
            return review

    raise HTTPException(status_code=404, detail="검토 결과를 찾을 수 없습니다.")


def get_review_highlights(review_id: int):
    review = get_review_by_id(review_id)
    return review["highlights"]


def get_review_report_path(review_id: int, file_format: str = "pdf"):
    review = get_review_by_id(review_id)

    report_files = review.get("report_files")
    if not report_files:
        raise HTTPException(status_code=404, detail="보고서 파일이 없습니다.")

    if file_format not in report_files:
        raise HTTPException(status_code=400, detail="지원하지 않는 보고서 형식입니다.")

    report_file_name = report_files[file_format]
    report_path = OUTPUT_DIR / report_file_name

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="보고서 파일을 찾을 수 없습니다.")

    return report_path