# Suggested API Surface

This is the minimum backend surface to make the first Foodbase product usable.

## Public Read APIs

### `GET /api/organizations`

Search and filter supplier profiles.

Supported query params:

- `q`
- `organization_type`
- `stage`
- `channel`
- `category`
- `subcategory`
- `variety`
- `certification`
- `designation`
- `export_market`
- `private_label`
- `city`
- `region`
- `priority_tier`

### `GET /api/organizations/:slug`

Return a full supplier profile:

- organization core data
- facilities
- contacts
- stage coverage
- offerings
- capacity records
- certifications
- geographical indications
- export markets
- source links
- outreach status

### `GET /api/stages`

Return the canonical supply-chain stage taxonomy for filters and UI rendering.

### `GET /api/categories`

Return normalized product and packaging categories.

### `GET /api/geographical-indications`

Return canonical PDO / PGI / TSG definitions for filters, enrichment, and verification workflows.

## Internal Ops APIs

### `POST /api/intake-profiles`

Accept a payload matching [producer-intake.schema.json](../schemas/producer-intake.schema.json).

Use cases:

- scraper output
- manual research entry
- supplier self-serve intake form
- official-registry enrichment jobs

### `POST /api/organizations/:slug/outreach-events`

Record calls, emails, meetings, form submissions, and notes.

### `PATCH /api/organizations/:slug/outreach-lead`

Update:

- lead status
- owner
- next action
- next action due date
- lead score

### `POST /api/ingestion-runs`

Store scraper execution metadata, raw payloads, extracted payloads, and failure reasons.

### `POST /api/geographical-indication-authorizations`

Store or update an organization’s authorized or verified use of a PDO / PGI / TSG designation.

## First UI Pages Backed By This API

1. supplier search page
2. supplier profile page
3. internal research queue
4. outreach CRM page
5. supplier intake form
