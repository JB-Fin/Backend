def analyze_document(filename: str, language: str = "ko") -> dict:
    return {
        # 임시 더미데이터 생성
        "review_id": 1,
        "filename": filename,
        "language": language,
        "status": "검토 완료",
        "issue_count": 3,
        "suggestion_count": 5,
        "original_text": [
            "최고 수익률 보장! 100% 안전한 투자!",
            "저희 금융상품에 가입하시면 무조건 수익을 보장해드립니다.",
            "연 10% 이상의 높은 수익률로 여러분의 재산을 불려드립니다.",
        ],
        "revised_text": [
            "금융상품 투자 안내",
            "저희 금융상품은 장기 투자를 통한 자산 증식을 목표로 합니다.",
            "과거 수익률은 미래 수익을 보장하지 않습니다.",
        ],
        "comments": [
            {
                "title": "절대적 표현 사용",
                "category": "광고 표현 리스크",
                "related_rule": "금융소비자보호법 제17조",
                "description": "100% 안전, 무조건 수익 보장 등의 표현은 소비자 오인을 유발할 수 있습니다.",
                "suggestion": "수익률은 보장되지 않으며 원금 손실 가능성이 있음을 명시해야 합니다.",
                "status": "적용 완료",
            },
            {
                "title": "원금 보장 오해 소지",
                "category": "투자 위험 고지",
                "related_rule": "자본시장법 제57조",
                "description": "투자상품은 원금 손실 가능성을 명확히 고지해야 합니다.",
                "suggestion": "투자 전 상품설명서 확인이 필요하다는 문구를 추가합니다.",
                "status": "적용 완료",
            },
        ],
    }


def generate_report(review_id: int) -> dict:
    return {
        "review_id": review_id,
        "report_file": f"review_report_{review_id}.pdf",
        "message": "보고서 생성 완료",
    }