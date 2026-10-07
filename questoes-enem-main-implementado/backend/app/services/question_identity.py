import hashlib
import json
import re
import unicodedata
from typing import Any

IDENTITY_FIELDS = (
    "year",
    "area",
    "number",
    "context",
    "statement",
    "options",
)


def normalize(value: Any) -> str:
    """Normaliza texto sem alterar capitalização ou pontuação."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def canonical_payload(
    *,
    year: int,
    area: str,
    number: int,
    context: Any,
    statement: Any,
    options: list[Any],
) -> dict[str, Any]:
    if len(options) != 5:
        raise ValueError("A identidade do ENEM exige exatamente 5 alternativas.")
    return {
        "area": normalize(area),
        "context": normalize(context),
        "number": int(number),
        "options": [normalize(option) for option in options],
        "statement": normalize(statement),
        "year": int(year),
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def generate_external_id(
    *,
    year: int,
    area: str,
    number: int,
    context: Any,
    statement: Any,
    options: list[Any],
) -> str:
    payload = canonical_payload(
        year=year,
        area=area,
        number=number,
        context=context,
        statement=statement,
        options=options,
    )
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
