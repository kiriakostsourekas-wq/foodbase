# Source Ingestion Status

Status date: `2026-04-06`

The current Foodbase ingestion pipeline covers three external directories:

- `madeingreece`
- `greekexporters`
- `kompass`

These are discovery sources, not the final truth layer.

## Current Output

Successful scrape outputs in this workspace:

- [madeingreece.json](../data/scrapes/madeingreece.json)
- [greekexporters.json](../data/scrapes/greekexporters.json)
- [kompass.json](../data/scrapes/kompass.json)
- [greek-food-sources.combined.json](../data/scrapes/greek-food-sources.combined.json)

Current counts:

- `madeingreece`: `1070` source records
- `greekexporters`: `208` source records
- combined successful inputs: `1278` source records and `1078` merged organization records

## Coverage Snapshot

Top merged organization types:

- `manufacturer`: `1032`
- `producer`: `32`
- `packaging_supplier`: `9`
- `logistics_provider`: `5`

Top inferred sectors:

- `honey`: `140`
- `fresh_produce`: `135`
- `olive_oil`: `133`
- `beverages`: `58`
- `seafood`: `47`

Top inferred stages:

- `agricultural_production`: `317`
- `primary_processing`: `235`
- `cold_chain`: `119`
- `manufacturing`: `107`
- `ingredient_sourcing`: `75`

## Source Constraints

`Kompass` is currently blocked in this environment. As of `2026-04-06`, direct requests to `https://gr.kompass.com/s/agriculture-food/01/` return `403 Forbidden`, so the source remains in the pipeline as best-effort only.

The working dataset is therefore built from `madeingreece` and `greekexporters`, while `kompass` is preserved as an explicit blocked input instead of being silently dropped.

## What Is Missing Today

The current automated pipeline is still directory-first. It does not yet ingest the higher-trust official verification layers that Foodbase should use for:

- PDO / PGI / TSG product definitions
- organization authorization to use a GI designation
- organic and market-access certification evidence
- offering-level or facility-level capacity and seasonality

Those sources are now tracked separately in [source-priority-map.md](source-priority-map.md).

## Recommended Next Ingestion Move

Do not broaden directory scraping first.

Start one category pilot, preferably olive oil or dairy, and combine:

1. official GI registry data
2. official company websites
3. trade-directory discovery data
4. direct outreach for MOQ, spare capacity, and lead times

That sequence gives Foodbase one verified, operational slice of the market instead of a larger but lower-trust directory dump.
