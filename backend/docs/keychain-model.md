# Keychain Patterns To Reuse

Keychain is not just a directory. It combines search, qualification, and supplier matching across multiple supply-chain layers.

## The Useful Product Ideas

### 1. Search by supply-chain stage

Keychain exposes separate entry points for:

- ingredient suppliers
- processing/manufacturing capabilities
- packaging suppliers

Foodbase should keep the same idea, but adapt it to the Greek food market with an explicit stage model:

- ingredient sourcing
- agricultural production
- primary processing
- formulation and product development
- manufacturing and private label
- packaging
- warehousing and cold chain
- distribution and export shipping

### 2. Supplier profiles are capability graphs, not plain company cards

The useful fields visible on Keychain pages are not only name and website. They include:

- geography
- product or ingredient categories
- packaging formats
- manufacturing or process capabilities
- whether the company is open to new projects
- contacts
- high-level qualification signals

Foodbase should store these as structured rows, not as one large blob of scraped text.

### 3. Matching starts from a project brief

Keychain’s flow is:

1. brand describes what it wants
2. platform searches vetted suppliers
3. team connects both sides directly

Foodbase should eventually support the same workflow:

- a buyer creates a request
- the request maps to required stages, product categories, certifications, and logistics needs
- Foodbase ranks and shortlists suppliers already active in or serving Greece

### 4. Evidence matters

A supplier graph is only useful if every claim can be traced back to a source.

That is why the schema includes:

- `source_documents`
- `organization_sources`
- `ingestion_runs`

This lets you distinguish:

- public website claims
- scraped facts
- manual notes from outreach
- verified commercial data received directly from the supplier

## Greece-Specific Additions Foodbase Needs

Keychain is US-centric. Foodbase should add fields that matter in Greece from day one:

- Greek and English company names
- service coverage across Greece and export markets
- HORECA versus retail versus wholesale focus
- cold-chain and traceability capabilities
- PDO/PGI and food-safety certifications where relevant
- packaging and logistics operators alongside food manufacturers

## Resulting Data Design Principles

1. One organization can cover multiple stages.
2. One organization can have multiple facilities.
3. Offerings must be modeled separately from capabilities.
4. Every important fact should have a source trail.
5. Outreach status belongs in the same system as supplier research.
