from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class CanonicalCustomer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_id: str
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: str | None = None
    source_system: str

    @field_validator("customer_id", "first_name", "last_name", "source_system")
    @classmethod
    def required_text(cls, value: str) -> str:
        if value is None or not str(value).strip():
            raise ValueError("value is required")
        return str(value).strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if value.count("@") != 1:
            raise ValueError("invalid email")

        local, domain = value.split("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("invalid email")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        digits = "".join(character for character in value if character.isdigit())
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("invalid phone")

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("date of birth is in the future")
        return value


def validate_record(record: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    try:
        customer = CanonicalCustomer.model_validate(record)
        return customer.model_dump(mode="json"), None
    except ValidationError as exc:
        reasons: list[str] = []
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"])
            reasons.append(f"{location}: {error['msg']}")
        return None, "; ".join(reasons)
