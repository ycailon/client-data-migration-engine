from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from migration_engine.config import load_client_config
from migration_engine.db import get_database_url
from migration_engine.engine import run_migration


app = typer.Typer(help="Config-driven client data migration engine.")
console = Console()


@app.callback()
def main() -> None:
    """Client data migration commands."""
    pass


@app.command()
def run(
    input_path: Annotated[
        Path,
        typer.Option("--input", exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    config_path: Annotated[
        Path,
        typer.Option("--config", exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    output_dir: Annotated[
        Path,
        typer.Option("--output"),
    ] = Path("output"),
    load_to_db: Annotated[
        bool,
        typer.Option("--load-to-db", help="Append valid rows to PostgreSQL."),
    ] = False,
    database_url: Annotated[
        str | None,
        typer.Option("--database-url", help="Optional SQLAlchemy PostgreSQL URL."),
    ] = None,
) -> None:
    """Run one client migration."""
    client_config = load_client_config(config_path)

    resolved_database_url = None
    if load_to_db:
        resolved_database_url = get_database_url(database_url)

    result = run_migration(
        input_path=input_path,
        client_config=client_config,
        output_dir=output_dir,
        database_url=resolved_database_url,
    )

    table = Table(title=f"Migration complete - {client_config.client_name}")
    table.add_column("Metric")
    table.add_column("Rows", justify="right")

    table.add_row("Source", str(result.summary["source_rows"]))
    table.add_row("Valid", str(result.summary["valid_rows"]))
    table.add_row("Rejected", str(result.summary["rejected_rows"]))
    table.add_row("Duplicates", str(result.summary["duplicate_rows"]))
    table.add_row("Loaded to database", str(result.summary["loaded_to_database"]))

    console.print(table)
    console.print(f"Output: {output_dir.resolve()}")


if __name__ == "__main__":
    app()
