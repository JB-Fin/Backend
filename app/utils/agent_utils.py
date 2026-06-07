import re, json, html

from typing import Any, Dict, List

MAX_EVIDENCE_CONTENT_CHARS = 500

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_json_from_text(text: str):
    text = text.strip()

    if "```" in text:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    decoder = json.JSONDecoder()

    for idx, char in enumerate(text):
        if char not in ["[", "{"]:
            continue

        try:
            parsed, _ = decoder.raw_decode(text[idx:])
            return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError("JSON 파싱 실패:\n" + text)


def safe_parse_json(text: str, default):
    try:
        return extract_json_from_text(text)
    except Exception as e:
        print("=== JSON PARSE ERROR ===")
        print(e)
        print("=== RAW TEXT ===")
        print(text)
        return default


def normalize_key(value: Any) -> str:
    text = clean_text(value)
    text = re.sub(r"[\s\"'“”‘’`·.,;:!?()\[\]{}<>/\\|-]+", "", text)
    return text.lower()


def dedupe_by_highlight_text(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped = []
    seen = set()

    for item in items:
        key = normalize_key(item.get("highlight_text", ""))

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        deduped.append(item)

    for idx, item in enumerate(deduped, start=1):
        item["issue_id"] = idx

    return deduped


def compact_evidence(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    compacted = []

    for ev in evidence:
        compacted.append(
            {
                "source": ev.get("source", ""),
                "page": ev.get("page"),
                "article": ev.get("article", ""),
                "content": clean_text(ev.get("content", ""))[:MAX_EVIDENCE_CONTENT_CHARS],
                "retrieval_score": ev.get("retrieval_score"),
            }
        )

    return compacted

def clean_json_response(text):

    text = text.strip()

    text = re.sub(
        r"^```json",
        "",
        text,
    )

    text = re.sub(
        r"^```",
        "",
        text,
    )

    text = re.sub(
        r"```$",
        "",
        text,
    )

    return text.strip()


def safe_json_loads(text):

    try:
        return json.loads(
            clean_json_response(text)
        )

    except Exception:
        return []