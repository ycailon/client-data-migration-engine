from pathlib import Path

import pandas as pd
import yaml

from migration_engine.config import load_client_config
from migration_engine.engine import run_migration


def test_migration_separates_valid_rejected_and_duplicates(tmp_path: Path):
    source = pd.DataFrame(
        [
            {
                "Customer ID": "1",
                "First Name": "Juan",
                "Last Name": "Cruz",
                "DOB": "1990-01-01",
                "Mobile": "09171234567",
                "Email Address": "juan@example.com",
            },
            {
                "Customer ID": "2",
                "First Name": "",
                "Last Name": "Santos",
                "DOB": "1991-01-01",
                "Mobile": "09181234567",
                "Email Address": "maria@example.com",
            },
            {
                "Customer ID": "3",
                "First Name": "Juan",
                "Last Name": "Duplicate",
                "DOB": "1992-01-01",
                "Mobile": "09991234567",
                "Email Address": "juan@example.com",
            },
        ]
    )

    input_path = tmp_path / "client.csv"
    source.to_csv(input_path, index=False)

    config = {
        "client_name": "test_client",
        "required_source_columns": ["Customer ID", "First Name", "Last Name"],
        "column_mapping": {
            "Customer ID": "customer_id",
            "First Name": "first_name",
            "Last Name": "last_name",
            "DOB": "date_of_birth",
            "Mobile": "phone",
            "Email Address": "email",
        },
        "defaults": {"country": "Philippines"},
    }

    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    result = run_migration(
        input_path=input_path,
        client_config=load_client_config(config_path),
        output_dir=tmp_path / "output",
    )

    assert result.summary["source_rows"] == 3
    assert result.summary["valid_rows"] == 1
    assert result.summary["rejected_rows"] == 1
    assert result.summary["duplicate_rows"] == 1

    assert (tmp_path / "output" / "valid_records.csv").exists()
    assert (tmp_path / "output" / "rejected_records.csv").exists()
    assert (tmp_path / "output" / "duplicates.csv").exists()
    assert (tmp_path / "output" / "migration_summary.json").exists()


def test_required_source_columns_are_case_insensitive(tmp_path: Path):
    source = pd.DataFrame(
        [
            {
                " customer id ": "1",
                "first name": "Ana",
                "LAST NAME": "Reyes",
            }
        ]
    )

    input_path = tmp_path / "client.csv"
    source.to_csv(input_path, index=False)

    config = {
        "client_name": "test_client",
        "required_source_columns": ["Customer ID", "First Name", "Last Name"],
        "column_mapping": {
            "Customer ID": "customer_id",
            "First Name": "first_name",
            "Last Name": "last_name",
        },
        "defaults": {},
    }

    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    result = run_migration(
        input_path=input_path,
        client_config=load_client_config(config_path),
        output_dir=tmp_path / "output",
    )

    assert result.summary["valid_rows"] == 1
