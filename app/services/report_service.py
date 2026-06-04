from pathlib import Path
from datetime import datetime

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def create_txt_report(review: dict) -> Path:
    report_file_name = f"review_{review['review_id']}_report.txt"
    report_path = OUTPUT_DIR / report_file_name

    highlights_text = ""

    for idx, item in enumerate(review.get("highlights", []), start=1):
        highlights_text += f"""
{idx}. 수정 필요 사항
- 페이지: {item.get("page", "-")}
- 위험도: {item.get("risk_level", "-")}
- 원문: {item.get("original_text", "-")}
- 이슈: {item.get("issue", "-")}
- 제안: {item.get("suggestion", "-")}
"""

    report_path.write_text(
        f"""준법 리스크 검토 보고서

생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

문서 ID: {review.get("file_id")}
파일명: {review.get("file_name", "-")}
검토 언어: {review.get("language")}
규정 범위: {review.get("regulation_scope", "-")}
위험도: {review.get("risk_level")}

[요약]
{review.get("summary")}

[수정 필요 사항]
{highlights_text}
""",
        encoding="utf-8",
    )

    return report_path


def create_docx_report(review: dict) -> Path:
    report_file_name = f"review_{review['review_id']}_report.docx"
    report_path = OUTPUT_DIR / report_file_name

    doc = Document()

    doc.add_heading("준법 리스크 검토 보고서", level=0)

    doc.add_paragraph(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph(f"문서 ID: {review.get('file_id')}")
    doc.add_paragraph(f"파일명: {review.get('file_name', '-')}")
    doc.add_paragraph(f"검토 언어: {review.get('language')}")
    doc.add_paragraph(f"규정 범위: {review.get('regulation_scope', '-')}")
    doc.add_paragraph(f"위험도: {review.get('risk_level')}")

    doc.add_heading("1. 검토 요약", level=1)
    doc.add_paragraph(review.get("summary", "-"))

    doc.add_heading("2. 수정 필요 사항", level=1)

    highlights = review.get("highlights", [])

    if not highlights:
        doc.add_paragraph("수정 필요 사항이 없습니다.")
    else:
        table = doc.add_table(rows=1, cols=5)
        table.style = "Table Grid"

        header_cells = table.rows[0].cells
        header_cells[0].text = "페이지"
        header_cells[1].text = "위험도"
        header_cells[2].text = "원문"
        header_cells[3].text = "이슈"
        header_cells[4].text = "수정 제안"

        for item in highlights:
            row_cells = table.add_row().cells
            row_cells[0].text = str(item.get("page", "-"))
            row_cells[1].text = item.get("risk_level", "-")
            row_cells[2].text = item.get("original_text", "-")
            row_cells[3].text = item.get("issue", "-")
            row_cells[4].text = item.get("suggestion", "-")

    doc.add_heading("3. 종합 의견", level=1)
    doc.add_paragraph(
        "본 보고서는 업로드된 문서의 준법 리스크를 자동 검토한 결과입니다. "
        "실제 법률 판단이 필요한 경우 담당자의 추가 검토가 필요합니다."
    )

    doc.save(report_path)

    return report_path


def create_pdf_report(review: dict) -> Path:
    report_file_name = f"review_{review['review_id']}_report.pdf"
    report_path = OUTPUT_DIR / report_file_name

    c = canvas.Canvas(str(report_path), pagesize=A4)
    width, height = A4

    x = 50
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Compliance Risk Review Report")

    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Created At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 25
    c.drawString(x, y, f"Review ID: {review.get('review_id')}")
    y -= 20
    c.drawString(x, y, f"File ID: {review.get('file_id')}")
    y -= 20
    c.drawString(x, y, f"File Name: {review.get('file_name', '-')}")
    y -= 20
    c.drawString(x, y, f"Language: {review.get('language')}")
    y -= 20
    c.drawString(x, y, f"Regulation Scope: {review.get('regulation_scope', '-')}")
    y -= 20
    c.drawString(x, y, f"Risk Level: {review.get('risk_level')}")

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, y, "Summary")

    y -= 20
    c.setFont("Helvetica", 10)
    summary = review.get("summary", "-")
    c.drawString(x, y, summary[:90])

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, y, "Highlights")

    y -= 25
    c.setFont("Helvetica", 9)

    for idx, item in enumerate(review.get("highlights", []), start=1):
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)

        c.drawString(x, y, f"{idx}. Risk: {item.get('risk_level', '-')}")
        y -= 15
        c.drawString(x, y, f"Original: {item.get('original_text', '-')[:90]}")
        y -= 15
        c.drawString(x, y, f"Issue: {item.get('issue', '-')[:90]}")
        y -= 15
        c.drawString(x, y, f"Suggestion: {item.get('suggestion', '-')[:90]}")
        y -= 25

    c.save()

    return report_path


def create_reports(review: dict) -> dict:
    txt_path = create_txt_report(review)
    docx_path = create_docx_report(review)
    pdf_path = create_pdf_report(review)

    return {
        "txt": txt_path.name,
        "docx": docx_path.name,
        "pdf": pdf_path.name,
    }