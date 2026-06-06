from app.graphs.review_graph import review_graph


def main():
    dummy_state = {
        "file_id": 1,
        "file_name": "dummy_contract.txt",
        "language": "ko",
        "regulation_scope": "금융소비자보호법",
        "target_text": """
ABC투자상품은 원금 보장 상품입니다.
가입 후 연 30% 확정 수익을 제공합니다.
중도 해지 시 불이익은 없습니다.
""",
        "vectorstore": None,
    }

    result = review_graph.invoke(dummy_state)

    print("\n=== highlighted_issues ===")
    print(result.get("highlighted_issues"))

    print("\n=== revised_issues ===")
    print(result.get("revised_issues"))

    print("\n=== report ===")
    print(result.get("report"))


if __name__ == "__main__":
    main()