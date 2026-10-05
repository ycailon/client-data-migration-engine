from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_input_file(path: str | Path, sheet_name: str | int | None = None) -> pd.DataFrame:
    input_path = Path(path)
    suffix = input_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(input_path, dtype=object)

    if suffix in {".xlsx", ".xlsm"}:
        selected_sheet = 0 if sheet_name is None else sheet_name
        return pd.read_excel(input_path, sheet_name=selected_sheet, dtype=object)

    raise ValueError(
        f"Unsupported file type '{suffix}'. Supported formats are .csv, .xlsx and .xlsm."
    )


def normalized_header(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def apply_column_mapping(
    frame: pd.DataFrame,
    column_mapping: dict[str, str],
    required_source_columns: list[str],
) -> pd.DataFrame:
    source_by_normalized = {
        normalized_header(column): column
        for column in frame.columns
    }

    missing_required = [
        column
        for column in required_source_columns
        if normalized_header(column) not in source_by_normalized
    ]
    if missing_required:
        raise ValueError(
            "Required source columns are missing: " + ", ".join(missing_required)
        )

    rename_map: dict[object, str] = {}
    for source_name, target_name in column_mapping.items():
        actual_source = source_by_normalized.get(normalized_header(source_name))
        if actual_source is not None:
            rename_map[actual_source] = target_name

    return frame.rename(columns=rename_map)
