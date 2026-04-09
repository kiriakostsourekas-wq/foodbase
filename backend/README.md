# Foodbase

Foodbase is a Keychain-style supplier discovery platform focused on the Greek food market.

This first pass builds the data foundation needed before the website can become operational:

- a Postgres schema for supplier discovery, sourcing evidence, and outreach
- a machine-readable seed dataset of Greek-market food producers and adjacent supply-chain operators
- a producer intake schema and questionnaire so scraping and manual outreach collect the same fields
- a discovery-first public API for supplier search, profiles, categories, GI definitions, and search facets
- an olive-oil pilot import flow that writes curated intake JSON into Postgres

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
3. Copy env vars: `cp .env.example .env`
4. Fill `FOODBASE_DB_PASSWORD` in `.env`
5. Fill `FOODBASE_GROQ_API_KEY` in `.env` if you want the AI endpoints to call Groq
6. Leave `FOODBASE_DATABASE_URL` blank unless you have a fully URL-encoded connection string
7. Check the database connection: `make db-check`
8. Apply the schema and seed reference data: `make db-init`
9. Generate and import the olive-oil pilot: `make pilot-import`
10. Run the API: `.venv/bin/uvicorn foodbase.main:app --reload`

Run backend commands from the `backend/` directory.

You can also use the helper targets in [Makefile](Makefile).

Useful targets:

- `make db-check` to verify the configured Postgres connection with `select 1`
- `make db-init` to apply [db/schema.sql](db/schema.sql) and seed categories, certifications, GI definitions, and Greek regions
- `make pilot-build` to generate [data/pilots/olive-oil-pilot.intake.json](data/pilots/olive-oil-pilot.intake.json)
- `make pilot-import` to generate and import the curated 20-profile olive-oil pilot
- `make scrape` for the currently reliable sources (`madeingreece` and `greekexporters`)
- `make scrape-all` to attempt all configured sources, including `kompass`
- `make combine` to merge the generated scrape files into one dataset
- `make verify` to run linting, typing, and tests

## Password-Only Supabase Setup

The default local workflow is now password-first:

- `FOODBASE_DATABASE_URL` remains supported as a full override
- if `FOODBASE_DATABASE_URL` is blank, the backend composes the SQLAlchemy URL from:
  - `FOODBASE_DB_PASSWORD`
  - `FOODBASE_DB_HOST`
  - `FOODBASE_DB_PORT`
  - `FOODBASE_DB_NAME`
  - `FOODBASE_DB_USER`
  - `FOODBASE_DB_SSLMODE`

For the common case, you only need to fill the password. If Supabase gives you a different direct or pooler hostname in the dashboard, override the host, port, or user fields as needed.

## Database Bootstrap

The backend now includes a non-mutating DB health check and a bootstrap script:

```bash
.venv/bin/python -m foodbase.db.bootstrap --check
.venv/bin/python -m foodbase.db.bootstrap
```

The bootstrap flow:

1. verifies database connectivity
2. applies [db/schema.sql](db/schema.sql)
3. seeds:
   - canonical product categories
   - certification taxonomy
   - Greek administrative regions with centroids
   - official olive-oil PDO/PGI definitions from the ministry registry

## Olive-Oil Pilot

The first official category lane is an olive-oil pilot:

- curated from [data/scrapes/greek-food-sources.combined.json](data/scrapes/greek-food-sources.combined.json)
- normalized into [data/pilots/olive-oil-pilot.intake.json](data/pilots/olive-oil-pilot.intake.json)
- imported via `foodbase.intake.importer` into the relational schema

The pilot currently targets 20 profiles with:

- normalized geography and map coordinates
- olive-oil category assignment
- contact/source traceability
- basic certification claims where source evidence exists
- placeholder MOQ / lead-time strings where public data is absent

## Public Read APIs

The backend now exposes the first DB-backed read surface:

- `GET /api/health`
- `GET /api/health/db`
- `GET /api/organizations`
- `GET /api/organizations/:slug`
- `GET /api/categories`
- `GET /api/geographical-indications`
- `GET /api/search-facets`
- `POST /api/ai/product-profile`
- `POST /api/ai/supplier-team`

## Vercel Services Deployment

The repository now includes a root [vercel.json](../vercel.json) configured for Vercel Services:

- `web` serves the Vite frontend from `frontend/`
- `api` serves FastAPI from `backend/main.py` under `/api`

For the deployed backend service, set:

- `FOODBASE_API_PREFIX=`
- `FOODBASE_DB_PASSWORD=...`
- `FOODBASE_GROQ_API_KEY=...`

Keep the frontend `VITE_API_BASE_URL` at `/api` so browser requests stay same-origin on Vercel.

These endpoints are intentionally shaped around the current supplier-facing frontend pages:

- `Discover`
- `SupplierProfile`
- `Compare`

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

## Current Boundaries

Still deferred in phase 1:

1. authenticated write/admin APIs
2. shortlist ownership and inquiry persistence
3. richer non-olive-oil supplier coverage for AI team assembly
4. verified official GI authorization per organization
