from __future__ import annotations

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def get_database_url(explicit_url: str | None = None) -> str:
    load_dotenv()
    database_url = explicit_url or os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL is not configured. Set it in .env or pass an explicit URL."
        )
    return database_url


def ensure_table(database_url: str) -> None:
    engine = create_engine(database_url)
    statement = """
    CREATE TABLE IF NOT EXISTS canonical_customers (
        id BIGSERIAL PRIMARY KEY,
        customer_id TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE,
        phone TEXT,
        email TEXT,
        address TEXT,
        city TEXT,
        state_province TEXT,
        postal_code TEXT,
        country TEXT,
        source_system TEXT NOT NULL,
        migrated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """
    with engine.begin() as connection:
        connection.execute(text(statement))


def load_customers(frame: pd.DataFrame, database_url: str) -> int:
    if frame.empty:
        return 0

    ensure_table(database_url)
    engine = create_engine(database_url)

    columns = [
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

    payload = frame.reindex(columns=columns).copy()
    payload["date_of_birth"] = pd.to_datetime(
        payload["date_of_birth"], errors="coerce"
    ).dt.date

    payload.to_sql(
        "canonical_customers",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )
    return len(payload)
