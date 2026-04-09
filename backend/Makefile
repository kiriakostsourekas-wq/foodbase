PYTHON := .venv/bin/python
PIP := .venv/bin/pip
UVICORN := .venv/bin/uvicorn
PYTEST := .venv/bin/pytest
RUFF := .venv/bin/ruff
MYPY := .venv/bin/mypy

.PHONY: install run test lint format typecheck scrape scrape-all combine verify db-check db-init pilot-build pilot-import

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

run:
	$(UVICORN) foodbase.main:app --reload

test:
	$(PYTEST)

lint:
	$(RUFF) check src tests

format:
	$(RUFF) format src tests

typecheck:
	$(MYPY) src

scrape:
	$(PYTHON) -m foodbase.scrapers.run --sources madeingreece greekexporters --greekexporters-page-limit 1 --output data/scrapes/greek-food-sources.available.json

scrape-all:
	$(PYTHON) -m foodbase.scrapers.run --sources madeingreece greekexporters kompass --greekexporters-page-limit 1

combine:
	$(PYTHON) -m foodbase.scrapers.combine

db-check:
	$(PYTHON) -m foodbase.db.bootstrap --check

db-init:
	$(PYTHON) -m foodbase.db.bootstrap

pilot-build:
	$(PYTHON) -m foodbase.intake.olive_oil_pilot --output data/pilots/olive-oil-pilot.intake.json

pilot-import:
	$(PYTHON) -m foodbase.intake.olive_oil_pilot --output data/pilots/olive-oil-pilot.intake.json --import-db

verify:
	$(RUFF) check src tests
	$(MYPY) src
	$(PYTEST)
