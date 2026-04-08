# Source Priority Map

Status date: `2026-04-08`

Foodbase should not treat all sources as equally trustworthy.

The right ingestion model is:

1. official registries for verification
2. company websites for profile enrichment
3. trade directories for discovery
4. direct outreach for commercial terms and spare capacity

## Tier 1: Official Verification Sources

Use these to verify origin claims, GI authorization, and certification-sensitive data.

### Greek Ministry of Rural Development and Food

- Best use: official PDO / PGI / TSG product definitions and ministry-level GI references
- Typical value: confirms that a designation exists and links to formal product specifications
- Notes: use as a verification source, not just a discovery source

### ELGO-DIMITRA

- Best use: enterprise-level certification and GI authorization evidence when available
- Typical value: supports whether an organization is approved to use specific protected designations
- Notes: higher trust than commercial directories

### eAmbrosia

- Best use: canonical EU GI registry for Greek PDO / PGI / TSG entries
- Typical value: authoritative registry metadata, naming, and specification references
- Notes: Foodbase should eventually store these as canonical GI records and link organizations to them

## Tier 2: Company-Controlled Sources

Use these to enrich profiles with offerings, packaging formats, export claims, and contact routes.

### Official company websites

- Best use: facilities, product ranges, packaging formats, export markets, contact details, private-label claims
- Typical value: richer operational context than registries
- Weakness: claims still need verification for sensitive fields such as certifications and GI authorizations

## Tier 3: Discovery Directories

Use these to find candidate organizations and backfill basic company data.

### Greek Exporters

- Best use: category discovery, product/service descriptions, contact details, profile pages
- Current status: already integrated in the Foodbase scraper pipeline

### Made in Greece

- Best use: broad discovery of Greek food companies with website, phone, email, and location
- Current status: already integrated in the Foodbase scraper pipeline

### Kompass

- Best use: structured B2B discovery and company capability hints
- Current status: relevant but currently blocked in this environment by anti-bot controls

### ACCI / ICAP export directories

- Best use: exporter discovery, sector filtering, contact enrichment
- Notes: useful as secondary discovery sources, but freshness and accessibility should be checked per release cycle

## Tier 4: Sector Aggregators And Associations

Use these for discovery and prioritization, not as the final verification layer.

### Aegean Exports

- Best use: category-led discovery of export-active Greek food and beverage brands

### Greek Products Exports

- Best use: discovery of smaller-scale, regional, and cooperative producers

### Enterprise Greece

- Best use: sector prioritization and exporter-program context

### SEVE

- Best use: exporter-member discovery
- Important: do not confuse `SEVE` with `SEPE`; `SEPE` is the ICT association, not the exporter directory you want here

## What Should Be Collected From Which Source

### Best captured from official registries

- PDO / PGI / TSG designation definitions
- authorized use of GI designations
- certification-sensitive status that requires formal validation

### Best captured from company websites and directories

- company identity
- website, phone, email, city, region
- offering descriptions
- packaging formats
- private-label capability
- export market claims
- business languages

### Usually requires direct outreach

- annual production volume
- spare capacity
- lead times
- MOQ
- commercial terms
- exact line-level availability by season

## Recommended Pilot

Do not scale ingestion horizontally first.

Pick one category and complete it end to end.

Recommended first pilot:

1. olive oil
2. dairy and cheese

Pilot workflow:

1. build the verified starting set from GI registries
2. enrich each organization from its official website
3. backfill missing discovery fields from directories
4. contact the supplier for MOQ, spare capacity, and lead time
5. normalize the result into the Foodbase intake schema and SQL model

That is the fastest way to validate the data model before broadening source coverage.
