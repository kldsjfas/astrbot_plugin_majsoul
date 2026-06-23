import re
from urllib.parse import parse_qs, urlparse

PAIPU_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{10,100}$")


def extract_paipu_id(text: str) -> str:
    if not isinstance(text, str):
        return ""
    value = text.strip().strip("<>")
    if PAIPU_ID_PATTERN.fullmatch(value):
        return value

    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"}:
        query_value = parse_qs(parsed.query).get("paipu", [""])[0]
        if PAIPU_ID_PATTERN.fullmatch(query_value):
            return query_value

    match = re.search(
        r"(?:[?&#]paipu=|/paipu/)([A-Za-z0-9_-]{10,100})", value, re.IGNORECASE
    )
    return match.group(1) if match else ""


def bounded_int(value: object, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def clean_persona(value: object, default: str) -> str:
    if not isinstance(value, str):
        return default
    cleaned = " ".join(value.split())[:80]
    return cleaned or default
