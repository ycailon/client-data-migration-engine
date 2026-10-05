from __future__ import annotations

import re
from typing import Any

import pandas as pd


NULL_LIKE = {"", "nan", "none", "null", "nat", "<na>"}


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    cleaned = " ".join(str(value).strip().split())
    if cleaned.lower() in NULL_LIKE:
        return None
    return cleaned


def normalize_name(value: Any) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return cleaned.title()


def normalize_email(value: Any) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return cleaned.lower().replace(" ", "")


def normalize_phone(value: Any, default_country: str | None = None) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None

    raw = cleaned
    digits = re.sub(r"\D", "", raw)

    if not digits:
        return None

    country = (default_country or "").strip().lower()

    if country == "philippines":
        if digits.startswith("63") and len(digits) == 12:
            return f"+{digits}"
        if digits.startswith("0") and len(digits) == 11:
            return f"+63{digits[1:]}"
        if digits.startswith("9") and len(digits) == 10:
            return f"+63{digits}"

    if raw.strip().startswith("+"):
        return f"+{digits}"

    return digits


def normalize_date(value: Any) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None

    parsed = pd.to_datetime(cleaned, errors="coerce")
    if pd.isna(parsed):
        return None

    return parsed.date().isoformat()


def normalize_record(record: dict[str, Any], default_country: str | None = None) -> dict[str, Any]:
    normalized = dict(record)

    normalized["customer_id"] = clean_text(record.get("customer_id"))
    normalized["first_name"] = normalize_name(record.get("first_name"))
    normalized["last_name"] = normalize_name(record.get("last_name"))
    normalized["date_of_birth"] = normalize_date(record.get("date_of_birth"))
    normalized["phone"] = normalize_phone(record.get("phone"), default_country)
    normalized["email"] = normalize_email(record.get("email"))

    for field in ["address", "city", "state_province", "postal_code", "country"]:
        normalized[field] = clean_text(record.get(field))

    return normalized
