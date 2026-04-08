# Foodbase

Foodbase is a Keychain-style supplier discovery platform focused on the Greek food market.

This first pass builds the data foundation needed before the website can become operational:

- a Postgres schema for supplier discovery, sourcing evidence, and outreach
- a machine-readable seed dataset of Greek-market food producers and adjacent supply-chain operators
- a producer intake schema and questionnaire so scraping and manual outreach collect the same fields

## What Is In This Repo

- [db/schema.sql](db/schema.sql)
  Initial relational model for organizations, offerings, stage coverage, certifications, contacts, sources, and outreach.
- [data/greek-market-suppliers.seed.json](data/greek-market-suppliers.seed.json)
  Starter supplier graph with real Greek-market companies and public-source coverage.
- [schemas/producer-intake.schema.json](schemas/producer-intake.schema.json)
  Validation contract for scraped or manually collected producer profiles.
- [docs/greek-market-supplier-shortlist.md](docs/greek-market-supplier-shortlist.md)
  Human-readable research summary and outreach priorities.
- [docs/keychain-model.md](docs/keychain-model.md)
  Product teardown of the Keychain patterns worth copying.
- [docs/producer-intake-questionnaire.md](docs/producer-intake-questionnaire.md)
  Standardized questionnaire for supplier onboarding.
- [docs/api-surface.md](docs/api-surface.md)
  Minimum backend API surface for search, profiles, intake, and outreach.
- [docs/sector-priority-map.md](docs/sector-priority-map.md)
  Sector-first implementation priorities derived from the Greek market survey.
- [docs/source-ingestion-status.md](docs/source-ingestion-status.md)
  Current scrape status, source counts, and ingestion blockers.
- [docs/source-priority-map.md](docs/source-priority-map.md)
  Ranked source strategy covering official GI registries, trade directories, and category-first ingestion.

## Practical Model

Foodbase needs to model more than just "producers". In practice, the platform must connect:

1. ingredient suppliers and agricultural producers
2. private-label and contract manufacturers
3. packaging suppliers
4. cold storage, warehousing, and shipping partners

That is why the schema centers on `organizations` plus many-to-many stage coverage and offering records, instead of assuming one company fits one bucket.

It also now separates:

- organization certifications from GI authorizations
- directory evidence from official registry evidence
- organization-level records from offering-level and facility-level capacity data

## First Backend Recommendation

The fastest path is:

1. use Postgres as the system of record
2. ingest official registries, company websites, and trade directories into the intake JSON shape
3. normalize accepted records into the SQL model with source-level traceability
4. expose read APIs for search, supplier profiles, and outreach queues

## Backend Stack

The repository now includes a professional Python backend starter:

- FastAPI for the API layer
- SQLAlchemy and Alembic for persistence and migrations
- Pydantic Settings for configuration
- Ruff, Mypy, Pytest, and coverage for development quality
- dedicated scrapers for `madeingreece`, `greekexporters`, and `kompass`
- a combine step that merges successful scrape outputs into one supplier dataset

## Environment Setup

1. Create the environment: `python3 -m venv .venv`
2. Install dependencies: `.venv/bin/pip install -e ".[dev]"`
3. Copy env vars if needed: `cp .env.example .env`
4. Run the API: `.venv/bin/uvicorn foodbase.main:app --reload`

Run backend commands from the `backend/` directory.

You can also use the helper targets in [Makefile](Makefile).

Useful targets:

- `make scrape` for the currently reliable sources (`madeingreece` and `greekexporters`)
- `make scrape-all` to attempt all configured sources, including `kompass`
- `make combine` to merge the generated scrape files into one dataset
- `make verify` to run linting, typing, and tests

## Scraping

Run the current source ingestion with:

```bash
.venv/bin/python -m foodbase.scrapers.run \
  --sources madeingreece greekexporters \
  --greekexporters-page-limit 1 \
  --output data/scrapes/greek-food-sources.available.json
```

Then combine the outputs into one working dataset:

```bash
.venv/bin/python -m foodbase.scrapers.combine \
  --inputs data/scrapes/madeingreece.json data/scrapes/greekexporters.json data/scrapes/kompass.json \
  --output data/scrapes/greek-food-sources.combined.json
```

Current results generated in this workspace:

- [data/scrapes/madeingreece.json](data/scrapes/madeingreece.json)
- [data/scrapes/greekexporters.json](data/scrapes/greekexporters.json)
- [data/scrapes/kompass.json](data/scrapes/kompass.json)
- [data/scrapes/greek-food-sources.combined.json](data/scrapes/greek-food-sources.combined.json)

`Kompass` currently returns `403 Forbidden` to direct scraping in this environment, so it is kept in the workflow as best-effort input while the reliable merged dataset is built from the successful sources.

## Recommended Next Build Steps

1. Stand up Postgres and apply [db/schema.sql](db/schema.sql).
2. Write an importer that maps [data/greek-market-suppliers.seed.json](data/greek-market-suppliers.seed.json) and future official-registry extracts into the normalized tables.
3. Add official-source ingestion for GI and certification verification, starting with one category pilot.
4. Build the first real read APIs for supplier search, supplier profiles, and outreach queues.
