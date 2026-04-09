from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from foodbase.intake.importer import import_profiles_from_path

REPO_ROOT = Path(__file__).resolve().parents[3]
COMBINED_SCRAPE_PATH = REPO_ROOT / "data" / "scrapes" / "greek-food-sources.combined.json"
OUTPUT_PATH = REPO_ROOT / "data" / "pilots" / "olive-oil-pilot.intake.json"

SELECTED_COMPANIES = [
    "ABEA ANATOLI",
    "AFOI I FOUFA AE",
    "AFOI I KALOGIROU AE",
    "AFOI KARGAKI AE",
    "AFOI KIDONAKI OE",
    "AGROELEOURGIKI MONOPROSSOPI IKE",
    "AGROSPARTA SA",
    "AGROTIKOS SYNETAIRISMOS ELEOPARAGOGON THRAPSANOU",
    "AGROTIKOS SYNETAIRISMOS PALAIOPANAGIAS",
    "ALEA ABE",
    "ANGELOS DOUKAS MARGARET DOUKA OE",
    "APOSTOLAKIS KYRIAKOS",
    "APOSTOLOS DANIILIDIS",
    "ASKRA OLIVE OIL - KTIMA LYMPERI",
    "BIO CRETAN OLIVE OIL LTD",
    "CHELIOTIS AE",
    "DEAS AE",
    "DROUSIAS AEBE",
    "ELEIA EMPORIA ELLINIKOU ELEOLADOU AE",
    "ERMILIA OLIVES AE",
]

LOCATION_OVERRIDES: dict[str, dict[str, Any]] = {
    "XANIA": {"city": "Chania", "region": "Crete", "lat": 35.5138, "lng": 24.0180},
    "ARKADIA": {"city": "Tripoli", "region": "Peloponnese", "lat": 37.5089, "lng": 22.3794},
    "MAGNISIA": {"city": "Volos", "region": "Thessaly", "lat": 39.3610, "lng": 22.9422},
    "IRAKLIO": {"city": "Heraklion", "region": "Crete", "lat": 35.3387, "lng": 25.1442},
    "MESSINIA": {"city": "Kalamata", "region": "Peloponnese", "lat": 37.0389, "lng": 22.1142},
    "LAKONIA": {"city": "Sparta", "region": "Peloponnese", "lat": 37.0731, "lng": 22.4297},
    "XALKIDIKI": {
        "city": "Polygyros",
        "region": "Central Macedonia",
        "lat": 40.3770,
        "lng": 23.4410,
    },
    "VIOTIA": {"city": "Livadeia", "region": "Central Greece", "lat": 38.4354, "lng": 22.8739},
    "HLEIA": {"city": "Pyrgos", "region": "Western Greece", "lat": 37.6751, "lng": 21.4410},
    "KORINTHIA": {"city": "Corinth", "region": "Peloponnese", "lat": 37.9386, "lng": 22.9322},
    "71500, Heraklion, Crete": {
        "city": "Heraklion",
        "region": "Crete",
        "lat": 35.3387,
        "lng": 25.1442,
    },
}

SUBCATEGORY_OVERRIDES = {
    "ABEA ANATOLI": "Cretan Olive Oil",
    "AGROSPARTA SA": "Laconian Olive Oil",
    "ASKRA OLIVE OIL - KTIMA LYMPERI": "Single Estate Olive Oil",
    "BIO CRETAN OLIVE OIL LTD": "Organic Extra Virgin Olive Oil",
}

VARIETY_OVERRIDES = {
    "AGROSPARTA SA": "Koroneiki",
    "AGROELEOURGIKI MONOPROSSOPI IKE": "Koroneiki",
    "ANGELOS DOUKAS MARGARET DOUKA OE": "Koroneiki",
}


def build_pilot_records() -> list[dict[str, Any]]:
    with COMBINED_SCRAPE_PATH.open("r", encoding="utf-8") as handle:
        combined_payload = json.load(handle)

    merged_records = combined_payload["merged_records"]
    records_by_name = {record["company_name"]: record for record in merged_records}
    pilot_records: list[dict[str, Any]] = []

    for company_name in SELECTED_COMPANIES:
        record = records_by_name[company_name]
        location = LOCATION_OVERRIDES[record["locations"][0]]
        website_url = first_value(record.get("website_urls"))
        certification_guesses = record.get("certification_guesses", [])
        capability_guesses = record.get("capability_guesses", [])
        stage_guesses = record.get("stage_coverage_guess", [])

        stage_coverage = normalize_stage_coverage(stage_guesses, record.get("source_sites", []))
        offering_notes = "Curated from local scrape evidence for the Foodbase olive-oil pilot."
        certifications = [
            to_certification_entry(guess)
            for guess in certification_guesses
            if guess not in {"PDO", "PGI", "TSG"}
        ]

        pilot_records.append(
            {
                "research_status": "verified",
                "company": {
                    "display_name": company_name.title()
                    if company_name.isupper()
                    else company_name,
                    "legal_name": company_name.title() if company_name.isupper() else company_name,
                    "organization_type": infer_organization_type(company_name),
                    "founded_year": None,
                    "ownership_model": infer_ownership_model(company_name),
                    "employee_count_range": None,
                    "website_url": website_url,
                    "country_code": "GR",
                    "headquarters_city": location["city"],
                    "headquarters_region": location["region"],
                    "headquarters_latitude": location["lat"],
                    "headquarters_longitude": location["lng"],
                    "summary": build_summary(company_name, location),
                    "priority_tier": 1,
                },
                "market_presence": {
                    "serves_greece": True,
                    "regions_in_greece": [location["region"]],
                    "export_markets": ["Europe"]
                    if "greekexporters" in record.get("source_sites", [])
                    else [],
                    "supported_languages": [],
                    "channels": ["export"]
                    if "greekexporters" in record.get("source_sites", [])
                    else [],
                    "export_license_status": "unknown",
                    "export_license_notes": None,
                },
                "stage_coverage": stage_coverage,
                "offerings": [
                    {
                        "name": "Olive Oil",
                        "product_category_slug": "olive-oil",
                        "subcategory": SUBCATEGORY_OVERRIDES.get(
                            company_name, "Extra Virgin Olive Oil"
                        ),
                        "variety_or_cultivar": VARIETY_OVERRIDES.get(company_name),
                        "offering_type": "finished_product",
                        "product_tags": ["olive oil"],
                        "packaging_formats": [],
                        "stage_coverage": stage_coverage,
                        "private_label_supported": "private_label" in capability_guesses or None,
                        "notes": offering_notes,
                    }
                ],
                "capabilities": capability_guesses,
                "certifications": certifications,
                "geographical_indications": [],
                "facilities": [
                    {
                        "facility_type": "head_office",
                        "name": (
                            f"{company_name.title() if company_name.isupper() else company_name} "
                            "headquarters"
                        ),
                        "city": location["city"],
                        "region": location["region"],
                        "address": None,
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                        "temperature_zones": [],
                        "notes": None,
                    }
                ],
                "contacts": build_contacts(record, website_url),
                "capacity_profiles": [
                    {
                        "capacity_scope": "organization",
                        "capacity_kind": "available_capacity",
                        "minimum_order_quantity": "On request",
                        "notes": (
                            "Public capacity figures were not disclosed in the source material."
                        ),
                    }
                ],
                "commercial_terms": {
                    "minimum_order_quantity": "On request",
                    "lead_time": "On request",
                    "sample_policy": None,
                    "incoterms": [],
                },
                "public_data_gaps": [
                    "Exact production volume",
                    "Spare capacity by harvest year",
                    "Lead time by packaging format",
                    "Minimum order quantity by SKU",
                ],
                "sources": build_sources(record, website_url),
                "notes": "Olive-oil pilot record generated from the merged scrape dataset.",
            }
        )

    return pilot_records


def normalize_stage_coverage(stage_guesses: list[str], source_sites: list[str]) -> list[str]:
    ordered = [stage for stage in stage_guesses if stage]
    if "packaging" not in ordered:
        ordered.append("packaging")
    if "greekexporters" in source_sites and "export_shipping" not in ordered:
        ordered.append("export_shipping")
    if not ordered:
        ordered = ["agricultural_production", "primary_processing", "packaging"]
    return ordered


def infer_organization_type(company_name: str) -> str:
    if "SYNETAIRISMOS" in company_name or "COOPERATIVE" in company_name:
        return "producer"
    return "mixed"


def infer_ownership_model(company_name: str) -> str | None:
    if "SYNETAIRISMOS" in company_name or "COOPERATIVE" in company_name:
        return "cooperative"
    return "private_company"


def build_summary(company_name: str, location: dict[str, Any]) -> str:
    normalized_name = company_name.title() if company_name.isupper() else company_name
    return (
        f"{normalized_name} is a curated Greek olive oil supplier based in "
        f"{location['city']}, {location['region']}. The profile combines company website "
        "evidence with local directory ingestion for the first Foodbase olive-oil pilot."
    )


def build_contacts(record: dict[str, Any], website_url: str | None) -> list[dict[str, Any]]:
    contacts: list[dict[str, Any]] = []
    email = first_value(record.get("emails"))
    phone = first_value(record.get("phones"))
    if email:
        contacts.append(
            {
                "contact_type": "email",
                "label": "General",
                "value": email,
                "is_primary": True,
            }
        )
    if phone:
        contacts.append(
            {
                "contact_type": "phone",
                "label": "Main",
                "value": phone,
                "is_primary": True,
            }
        )
    if website_url:
        contacts.append(
            {
                "contact_type": "website",
                "label": "Website",
                "value": website_url,
                "is_primary": True,
            }
        )
    return contacts


def build_sources(record: dict[str, Any], website_url: str | None) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    if website_url:
        sources.append(
            {
                "url": website_url,
                "source_type": "official_website",
                "title": None,
                "notes": "Primary company website.",
            }
        )

    listing_url = first_value(record.get("listing_urls"))
    if listing_url:
        sources.append(
            {
                "url": listing_url,
                "source_type": "trade_directory",
                "title": None,
                "notes": f"Directory evidence from {', '.join(record.get('source_sites', []))}.",
            }
        )
    return sources


def to_certification_entry(certification_guess: str) -> dict[str, Any]:
    if certification_guess == "Organic":
        return {
            "name": "Organic EU",
            "certification_type": "organic",
            "certificate_number": None,
            "certified_by": None,
            "scope": "Olive oil production",
            "status": "claimed",
            "issued_at": None,
            "expires_at": None,
        }

    certification_type = "food_safety"
    if certification_guess in {"ISO 9001", "GMP"}:
        certification_type = "quality"

    return {
        "name": certification_guess,
        "certification_type": certification_type,
        "certificate_number": None,
        "certified_by": None,
        "scope": "Olive oil production",
        "status": "claimed",
        "issued_at": None,
        "expires_at": None,
    }


def first_value(values: list[Any] | None) -> Any | None:
    if not values:
        return None
    return values[0]


def write_pilot_file(output_path: Path = OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_pilot_records()
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and optionally import the Foodbase olive-oil pilot."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Where to write the generated olive-oil intake JSON.",
    )
    parser.add_argument(
        "--import-db",
        action="store_true",
        help="Import the generated intake JSON into the configured Postgres database.",
    )
    args = parser.parse_args()

    output_path = write_pilot_file(args.output)
    print(f"generated={output_path}")

    if args.import_db:
        stats = import_profiles_from_path(output_path)
        print(f"created={stats.created}")
        print(f"updated={stats.updated}")


if __name__ == "__main__":
    main()
