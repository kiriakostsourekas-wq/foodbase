from __future__ import annotations

import re
import time
from collections import Counter
from collections.abc import Iterable
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4.element import Tag

from foodbase.scrapers.models import SourceRecord

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    )
}

IGNORED_CONTEXT_VALUES = {
    "food",
    "food_products",
    "agricultural_food_beverages",
    "food products",
    "agricultural food beverages",
}

MANUFACTURER_HINTS = [
    "factory",
    "manufactur",
    "processing",
    "production",
    "private label",
    "contract manufacturing",
    "bottling",
    "packaging line",
]

PRODUCER_HINTS = [
    "farm",
    "grower",
    "cooperative",
    "agricultural",
    "orchard",
    "beekeep",
    "olive grove",
]

LOGISTICS_HINTS = [
    "logistics",
    "transport",
    "transit",
    "warehouse",
    "warehousing",
    "distribution center",
    "distribution centres",
    "distribution centre",
    "refrigerated truck",
    "3pl",
]

PACKAGING_HINTS = [
    "packaging",
    "bottle",
    "jar",
    "tray",
    "labeling",
    "carton",
]

STAGE_PATTERNS: dict[str, list[str]] = {
    "agricultural_production": ["fruit", "vegetable", "olive", "honey", "farm", "beekeep", "kiwi"],
    "primary_processing": ["olive oil", "cheese", "dairy", "frozen", "seafood", "meat"],
    "manufacturing": [
        "biscuit",
        "cookie",
        "pasta",
        "bread",
        "bakery",
        "confectionery",
        "dairy",
        "cheese",
        "snack",
        "drink",
        "beverage",
        "prepared",
    ],
    "private_label": ["private label"],
    "packaging": ["packag", "vacuum", "tupper", "tray", "jar", "bottle"],
    "cold_chain": ["frozen", "chilled", "dairy", "cheese", "seafood", "meat"],
    "distribution": ["export", "wholesale", "retailer", "horeca", "distribution", "direct sales"],
    "warehousing": ["warehouse", "storage", "logistics"],
    "ingredient_sourcing": ["herbs", "spices", "nuts", "rice", "legume", "flour", "superfood"],
}

SECTOR_PATTERNS: dict[str, list[str]] = {
    "dairy": ["dairy", "yogurt", "feta", "halloumi", "cheese", "milk"],
    "olive_oil": ["olive oil", "olives", "pickles", "koroneiki"],
    "honey": ["honey", "royal jelly", "bee", "beekeep"],
    "fresh_produce": ["fruit", "vegetable", "kiwi", "grape", "peach", "citrus", "cherry"],
    "ingredients": ["ingredient", "flour", "starch", "sweetener", "extract", "enzyme"],
    "seafood": ["seafood", "fish", "octopus", "cuttlefish"],
    "bakery": ["bakery", "bread", "biscuit", "cookie", "pita", "confectionery"],
    "beverages": ["beverage", "drink", "ouzo", "wine", "juice", "spirits", "soft drink"],
    "logistics": ["logistics", "cold chain", "warehouse", "distribution", "transit", "3pl"],
}

PROCESS_PATTERNS: dict[str, list[str]] = {
    "aseptic_filling": ["aseptic filling", "aseptic"],
    "iqf": ["iqf", "individual quick freezing"],
    "cold_pressed_extraction": ["cold pressed", "cold-pressed"],
    "xray_inspection": ["x-ray inspection", "x ray inspection", "x-ray"],
    "centrifugal_extraction": ["centrifug", "decanter", "malax"],
    "blending_repacking": ["blending", "repacking"],
    "ripening": ["ripening"],
}

CAPABILITY_PATTERNS: dict[str, list[str]] = {
    "private_label": ["private label"],
    "export_shipping": ["export", "international market", "direct sales"],
    "traceability": ["traceability", "quality management"],
    "gluten_free_facility": ["gluten free", "gluten-free"],
    "packaging_design_support": ["packaging", "packaged", "available packages"],
    "cold_chain": ["frozen", "chilled", "cold"],
    "contract_manufacturing": ["contract manufacturing"],
    "aseptic_filling": ["aseptic filling"],
    "iqf": ["iqf", "individual quick freezing"],
    "xray_inspection": ["x-ray inspection", "x-ray"],
    "blending_repacking": ["blending", "repacking"],
}

CERTIFICATION_PATTERNS: dict[str, list[str]] = {
    "BRC": ["brc"],
    "BRCGS": ["brcgs"],
    "FSSC 22000": ["fssc 22000"],
    "IFS": ["ifs"],
    "ISO 22000": ["iso 22000"],
    "ISO 9001": ["iso 9001"],
    "PDO": ["p.d.o", "pdo"],
    "PGI": ["pgi"],
    "Organic": ["organic", "bio"],
    "VLOG": ["vlog"],
    "HACCP": ["haccp"],
    "GlobalG.A.P.": ["globalg.a.p", "globalgap"],
    "AGRO 10": ["agro10", "agro 10"],
}


class HtmlFetcher:
    def __init__(self, delay_seconds: float = 0.15, timeout_seconds: float = 30.0) -> None:
        self.delay_seconds = delay_seconds
        self.client = httpx.Client(
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
            timeout=timeout_seconds,
        )

    def get(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        return response.text

    def close(self) -> None:
        self.client.close()


def compact_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.replace("\xa0", " ").replace("\ufeff", "")
    cleaned = re.sub(r"\s+", " ", normalized).strip()
    return cleaned or None


def attr_value_as_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def normalize_list(values: Iterable[str | None]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = compact_text(value)
        if cleaned and cleaned not in seen:
            unique.append(cleaned)
            seen.add(cleaned)
    return unique


def normalize_url(base_url: str, maybe_relative: str | None) -> str | None:
    if not maybe_relative:
        return None
    cleaned = maybe_relative.strip()
    if cleaned.startswith("www."):
        cleaned = f"https://{cleaned}"
    normalized = urljoin(base_url, cleaned)
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return normalized


def split_product_text(text: str | None) -> list[str]:
    if not text:
        return []
    parts = re.split(r"[;,]\s*|\.\s+", text)
    return normalize_list(re.sub(r"[.;,:]+$", "", part) for part in parts)


def tag_text(node: Tag | None) -> str | None:
    if node is None:
        return None
    return compact_text(node.get_text(" ", strip=True))


def normalize_context_value(value: str | None) -> str | None:
    cleaned = compact_text(value)
    if not cleaned:
        return None
    normalized = cleaned.replace("_", " ").replace("-", " ")
    if normalized.lower() in IGNORED_CONTEXT_VALUES:
        return None
    return normalized


def has_any_keyword(text_blob: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text_blob for keyword in keywords)


def guess_organization_type(text_blob: str) -> str:
    lowered = text_blob.lower()

    has_packaging = has_any_keyword(lowered, PACKAGING_HINTS)
    has_logistics = has_any_keyword(lowered, LOGISTICS_HINTS)
    has_manufacturing = has_any_keyword(lowered, MANUFACTURER_HINTS)
    has_producer = has_any_keyword(lowered, PRODUCER_HINTS)

    if has_packaging and not (has_manufacturing or has_producer):
        return "packaging_supplier"
    if has_logistics and not (has_manufacturing or has_producer):
        return "logistics_provider"
    if has_producer and not has_manufacturing:
        return "producer"
    return "manufacturer"


def infer_tags(record: SourceRecord) -> None:
    raw_values = [
        value
        for value in record.raw.values()
        if isinstance(value, str) and compact_text(value)
    ]
    context_values = normalize_list(
        normalize_context_value(value)
        for value in [record.category, record.subcategory]
    )
    text_blob = " ".join(
        value
        for value in [
            *context_values,
            record.description,
            " ".join(record.products_or_services),
            " ".join(record.notes),
            " ".join(raw_values),
        ]
        if value
    )
    lowered = text_blob.lower()

    record.organization_type_guess = guess_organization_type(text_blob)
    record.sector_guesses = normalize_list(
        sector
        for sector, patterns in SECTOR_PATTERNS.items()
        if any(pattern in lowered for pattern in patterns)
    )
    record.process_guesses = normalize_list(
        process
        for process, patterns in PROCESS_PATTERNS.items()
        if any(pattern in lowered for pattern in patterns)
    )
    record.stage_coverage_guess = normalize_list(
        stage
        for stage, patterns in STAGE_PATTERNS.items()
        if any(pattern in lowered for pattern in patterns)
    )
    record.capability_guesses = normalize_list(
        capability
        for capability, patterns in CAPABILITY_PATTERNS.items()
        if any(pattern in lowered for pattern in patterns)
    )
    record.certification_guesses = normalize_list(
        certification
        for certification, patterns in CERTIFICATION_PATTERNS.items()
        if any(pattern in lowered for pattern in patterns)
    )


def merge_records(records: list[SourceRecord]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for record in records:
        website_host = None
        if record.website_url:
            website_host = urlparse(record.website_url).netloc.lower()
        key = website_host or record.company_name.lower()

        if key not in grouped:
            grouped[key] = {
                "company_name": record.company_name,
                "brand_names": [],
                "website_urls": [],
                "phones": [],
                "emails": [],
                "locations": [],
                "addresses": [],
                "source_sites": [],
                "source_sections": [],
                "listing_urls": [],
                "detail_urls": [],
                "categories": [],
                "subcategories": [],
                "descriptions": [],
                "products_or_services": [],
                "sector_guesses": [],
                "process_guesses": [],
                "stage_coverage_guess": [],
                "capability_guesses": [],
                "certification_guesses": [],
                "organization_type_guesses": [],
                "notes": [],
            }

        target = grouped[key]
        target["brand_names"].append(record.brand_name)
        target["website_urls"].append(record.website_url)
        target["phones"].append(record.phone)
        target["emails"].append(record.email)
        target["locations"].append(record.location)
        target["addresses"].append(record.address)
        target["source_sites"].append(record.source_site)
        target["source_sections"].extend(record.source_sections)
        target["listing_urls"].append(record.listing_url)
        target["detail_urls"].append(record.detail_url)
        target["categories"].append(record.category)
        target["subcategories"].append(record.subcategory)
        target["descriptions"].append(record.description)
        target["products_or_services"].extend(record.products_or_services)
        target["sector_guesses"].extend(record.sector_guesses)
        target["process_guesses"].extend(record.process_guesses)
        target["stage_coverage_guess"].extend(record.stage_coverage_guess)
        target["capability_guesses"].extend(record.capability_guesses)
        target["certification_guesses"].extend(record.certification_guesses)
        target["organization_type_guesses"].append(record.organization_type_guess)
        target["notes"].extend(record.notes)

    merged: list[dict[str, Any]] = []
    for item in grouped.values():
        type_counter = Counter(
            guessed_type
            for guessed_type in item["organization_type_guesses"]
            if guessed_type
        )
        organization_type = (
            type_counter.most_common(1)[0][0] if type_counter else "manufacturer"
        )

        merged.append(
            {
                "company_name": item["company_name"],
                "brand_names": normalize_list(item["brand_names"]),
                "website_urls": normalize_list(item["website_urls"]),
                "phones": normalize_list(item["phones"]),
                "emails": normalize_list(item["emails"]),
                "locations": normalize_list(item["locations"]),
                "addresses": normalize_list(item["addresses"]),
                "source_sites": normalize_list(item["source_sites"]),
                "source_sections": normalize_list(item["source_sections"]),
                "listing_urls": normalize_list(item["listing_urls"]),
                "detail_urls": normalize_list(item["detail_urls"]),
                "categories": normalize_list(item["categories"]),
                "subcategories": normalize_list(item["subcategories"]),
                "descriptions": normalize_list(item["descriptions"]),
                "products_or_services": normalize_list(item["products_or_services"]),
                "sector_guesses": normalize_list(item["sector_guesses"]),
                "process_guesses": normalize_list(item["process_guesses"]),
                "stage_coverage_guess": normalize_list(item["stage_coverage_guess"]),
                "capability_guesses": normalize_list(item["capability_guesses"]),
                "certification_guesses": normalize_list(item["certification_guesses"]),
                "organization_type_guess": organization_type,
                "notes": normalize_list(item["notes"]),
            }
        )

    merged.sort(key=lambda item: item["company_name"])
    return merged
