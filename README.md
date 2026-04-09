# Foodbase

This repository is now organized as a multi-app workspace.

## Layout

- `backend/`
  Python/FastAPI backend, data model, scrapers, tests, importer, and DB-backed read APIs.
- `frontend/`
  Reserved for the future frontend application.
- `base44-export-2026-04-08T19-54-02-833Z/`
  Untouched Base44 frontend export kept as the current UI reference.

## Current App

The active codebase today is the backend.

Start there:

- [backend/README.md](backend/README.md)

## Current Backend Capabilities

The backend now includes:

- password-only Supabase/Postgres configuration support
- DB connectivity check and schema bootstrap commands
- seeded categories, certifications, Greek regions, and olive-oil GI definitions
- a curated 20-profile olive-oil pilot intake file and importer
- public read APIs for supplier search, supplier detail, categories, GI definitions, and search facets
