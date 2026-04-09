# Foodbase

This repository is now organized as a multi-app workspace.

## Layout

- `backend/`
  Python/FastAPI backend, data model, scrapers, tests, importer, and DB-backed read APIs.
- `frontend/`
  Vite frontend wired to the Foodbase backend for discovery, profile, compare, and AI sourcing flows.
- `base44-export-2026-04-08T19-54-02-833Z/`
  Untouched Base44 export kept only as the original design reference and ignored from git.

## Local Run

1. Start the backend from [`backend/`](backend/README.md)
2. Start the frontend from [`frontend/README.md`](frontend/README.md)
3. Add `FOODBASE_GROQ_API_KEY` to `backend/.env` if you want the AI routes to generate live product briefs and supplier teams

## Current Backend Capabilities

The backend now includes:

- password-only Supabase/Postgres configuration support
- DB connectivity check and schema bootstrap commands
- seeded categories, certifications, Greek regions, and olive-oil GI definitions
- a curated 20-profile olive-oil pilot intake file and importer
- public read APIs for supplier search, supplier detail, categories, GI definitions, and search facets
- Groq-backed AI APIs for product-brief generation and supplier-team selection

## Current Frontend Capabilities

The frontend now runs locally against the backend and supports:

- landing page
- live discover page backed by `GET /api/organizations`
- live supplier profiles backed by `GET /api/organizations/:slug`
- live compare page backed by supplier list data
- AI product creator backed by `POST /api/ai/product-profile`
- AI supplier-team page backed by `POST /api/ai/supplier-team`
