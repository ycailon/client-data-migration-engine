.PHONY: install test lint sample postgres

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests scripts

sample:
	python scripts/generate_sample_data.py --rows 1000

postgres:
	docker compose up -d postgres
