from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ClientConfig:
    client_name: str
    column_mapping: dict[str, str]
    required_source_columns: list[str] = field(default_factory=list)
    defaults: dict[str, Any] = field(default_factory=dict)
    sheet_name: str | int | None = None


def load_client_config(path: str | Path) -> ClientConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}

    required = {"client_name", "column_mapping"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Config is missing required keys: {sorted(missing)}")

    if not isinstance(raw["column_mapping"], dict) or not raw["column_mapping"]:
        raise ValueError("column_mapping must be a non-empty mapping")

    return ClientConfig(
        client_name=str(raw["client_name"]),
        column_mapping={str(k): str(v) for k, v in raw["column_mapping"].items()},
        required_source_columns=[str(v) for v in raw.get("required_source_columns", [])],
        defaults=raw.get("defaults", {}) or {},
        sheet_name=raw.get("sheet_name"),
    )
