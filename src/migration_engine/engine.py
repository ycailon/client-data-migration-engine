from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from migration_engine.config import ClientConfig
from migration_engine.db import load_customers
from migration_engine.io import apply_column_mapping, read_input_file
from migration_engine.normalizers import normalize_record
from migration_engine.validation import validate_record


CANONICAL_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "date_of_birth",
    "phone",
    "email",
    "address",
    "city",
    "state_province",
    "postal_code",
    "country",
    "source_system",
]


@dataclass
class MigrationResult:
    valid: pd.DataFrame
    rejected: pd.DataFrame
    duplicates: pd.DataFrame
    summary: dict[str, Any]


def _apply_defaults(frame: pd.DataFrame, defaults: dict[str, Any]) -> pd.DataFrame:
    result = frame.copy()

    for column, default_value in defaults.items():
        if column not in result.columns:
            result[column] = default_value
        else:
            empty = result[column].isna() | result[column].astype(str).str.strip().eq("")
            result.loc[empty, column] = default_value

    return result


def _duplicate_mask(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype=bool, index=frame.index)

    email_key = frame.get("email", pd.Series(index=frame.index, dtype=object)).fillna("")
    phone_key = frame.get("phone", pd.Series(index=frame.index, dtype=object)).fillna("")

    email_duplicate = email_key.ne("") & email_key.duplicated(keep="first")
    phone_duplicate = phone_key.ne("") & phone_key.duplicated(keep="first")
    return email_duplicate | phone_duplicate


def run_migration(
    input_path: str | Path,
    client_config: ClientConfig,
    output_dir: str | Path,
    database_url: str | None = None,
) -> MigrationResult:
    source = read_input_file(input_path, client_config.sheet_name)
    mapped = apply_column_mapping(
        source,
        client_config.column_mapping,
        client_config.required_source_columns,
    )
    mapped = _apply_defaults(mapped, client_config.defaults)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    valid_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []

    default_country = client_config.defaults.get("country")

    for row_number, (_, row) in enumerate(mapped.iterrows(), start=2):
        raw = row.to_dict()
        raw["source_system"] = client_config.client_name

        normalized = normalize_record(raw, default_country=default_country)
        normalized["source_system"] = client_config.client_name

        validated, error = validate_record(normalized)
        if error:
            rejected = dict(normalized)
            rejected["_source_row"] = row_number
            rejected["_rejection_reason"] = error
            rejected_records.append(rejected)
            continue

        valid_records.append(validated or {})

    valid = pd.DataFrame(valid_records, columns=CANONICAL_COLUMNS)
    rejected = pd.DataFrame(rejected_records)

    duplicate_mask = _duplicate_mask(valid)
    duplicates = valid.loc[duplicate_mask].copy()
    valid = valid.loc[~duplicate_mask].copy()

    valid.to_csv(output_path / "valid_records.csv", index=False)
    rejected.to_csv(output_path / "rejected_records.csv", index=False)
    duplicates.to_csv(output_path / "duplicates.csv", index=False)

    loaded_to_database = 0
    if database_url:
        loaded_to_database = load_customers(valid, database_url)

    summary = {
        "source_rows": int(len(source)),
        "valid_rows": int(len(valid)),
        "rejected_rows": int(len(rejected)),
        "duplicate_rows": int(len(duplicates)),
        "loaded_to_database": int(loaded_to_database),
        "client_name": client_config.client_name,
        "input_file": str(Path(input_path)),
    }

    with (output_path / "migration_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    return MigrationResult(
        valid=valid,
        rejected=rejected,
        duplicates=duplicates,
        summary=summary,
    )
