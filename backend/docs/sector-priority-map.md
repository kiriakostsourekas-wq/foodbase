# Sector Priority Map

This document translates the strategic architecture brief into implementation priorities for Foodbase.

## Priority Sectors

Foodbase should not treat the Greek food market as one flat supplier list. The first useful backend version should cluster suppliers into the sectors that actually drive sourcing demand and export activity:

1. dairy and cheese
2. olive oil and table olives
3. honey and natural sweeteners
4. fresh produce and fruit processing
5. upstream ingredients
6. cold-chain logistics

## Why These Sectors First

These sectors combine the strongest overlap between:

- export activity
- private-label relevance
- certification intensity
- process differentiation
- regional producer density

That makes them the best fit for a Keychain-style search and matching engine.

## Named Targets From The Strategic Survey

### Dairy

- Kri Kri
- Hellenic Dairies / Olympus
- Omiros
- Mystakelli

Critical fields:

- milk sourcing model
- dairy and yogurt line capabilities
- cold-chain requirements
- certifications
- private-label depth

### Olive Oil

- Mediterra Food
- MYST
- Sparta Gourmet
- Medbest

Critical fields:

- grove sourcing
- extraction method
- bottling and packaging formats
- branded versus bulk export
- PDO and PGI status

### Honey

- Attiki-Pittas
- Melinda

Critical fields:

- beekeeper network size
- floral type
- pack formats
- retailer private-label capability
- FSSC / HACCP / export labeling

### Fresh Produce And Fruit Processing

- Zeus Kiwi
- Venus Growers
- Alexander S.A.
- Protofanousis
- Dimi
- Matragos Fruit

Critical fields:

- seasonality
- cold storage
- ripening and canning
- aseptic processing
- GlobalG.A.P.
- export lanes

### Ingredients

- Loulis Food Ingredients
- Falcon Ingredients
- FAMA Food Service
- Grainar

Critical fields:

- ingredient families
- blending and repacking
- technical support
- MOQs
- application areas

### Logistics

- Med Frigo

Critical fields:

- refrigerated capacity
- route network
- certifications
- cross-border coverage
- warehouse footprint

## Backend Implication

The supplier profile model must support:

- sector clusters
- process tags
- capability tags
- certification tags
- logistics requirements
- regional and export coverage

This is why the scraper output now emits:

- `sector_guesses`
- `process_guesses`
- `stage_coverage_guess`
- `capability_guesses`
- `certification_guesses`

Those fields are not the final truth layer, but they are the right bridge from messy public pages into a queryable sourcing graph.
