from foodbase.scrapers.models import SourceRecord
from foodbase.scrapers.utils import guess_organization_type, merge_records


def test_guess_organization_type_prefers_manufacturer_when_processing_is_present() -> None:
    text_blob = (
        "Factory for processing fresh and frozen fish with refrigerated trucks "
        "and distribution across Europe."
    )

    assert guess_organization_type(text_blob) == "manufacturer"


def test_merge_records_deduplicates_by_website_host() -> None:
    first = SourceRecord(
        source_site="madeingreece",
        source_sections=["dairy"],
        listing_url="https://example.com/listing-a",
        detail_url=None,
        company_name="Sample Dairy",
        website_url="https://sampledairy.gr",
        products_or_services=["Greek yogurt"],
        sector_guesses=["dairy"],
        capability_guesses=["private_label"],
    )
    second = SourceRecord(
        source_site="greekexporters",
        source_sections=["private_label"],
        listing_url="https://example.com/listing-b",
        detail_url="https://example.com/detail-b",
        company_name="Sample Dairy SA",
        website_url="https://sampledairy.gr/private-label",
        products_or_services=["Private label yogurt"],
        sector_guesses=["dairy"],
        capability_guesses=["private_label"],
    )

    merged = merge_records([first, second])

    assert len(merged) == 1
    assert merged[0]["company_name"] == "Sample Dairy"
    assert merged[0]["source_sites"] == ["madeingreece", "greekexporters"]
    assert merged[0]["capability_guesses"] == ["private_label"]
