from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Company(StrictModel):
    display_name: str
    legal_name: str | None = None
    vat_number: str | None = None
    company_registration_number: str | None = None
    organization_type: Literal[
        "producer",
        "manufacturer",
        "processor",
        "packaging_supplier",
        "logistics_provider",
        "mixed",
    ]
    founded_year: int | None = Field(default=None, ge=1800, le=2100)
    ownership_model: (
        Literal[
            "private_company",
            "cooperative",
            "producer_group",
            "public_company",
            "other",
        ]
        | None
    ) = None
    employee_count_range: str | None = None
    website_url: str | None = None
    country_code: str = Field(default="GR", min_length=2, max_length=2)
    headquarters_city: str | None = None
    headquarters_region: str | None = None
    headquarters_latitude: float | None = Field(default=None, ge=-90, le=90)
    headquarters_longitude: float | None = Field(default=None, ge=-180, le=180)
    summary: str | None = None
    priority_tier: int | None = Field(default=None, ge=1, le=3)


class MarketPresence(StrictModel):
    serves_greece: bool = True
    regions_in_greece: list[str] = Field(default_factory=list)
    export_markets: list[str] = Field(default_factory=list)
    supported_languages: list[str] = Field(default_factory=list)
    channels: list[
        Literal["retail", "horeca", "wholesale", "distributor", "industrial", "export", "ecommerce"]
    ] = Field(default_factory=list)
    export_license_status: (
        Literal[
            "unknown",
            "not_required",
            "held",
            "not_held",
            "pending",
        ]
        | None
    ) = None
    export_license_notes: str | None = None


class Offering(StrictModel):
    name: str
    product_category_slug: str | None = None
    subcategory: str | None = None
    variety_or_cultivar: str | None = None
    offering_type: Literal[
        "ingredient", "finished_product", "packaging", "logistics_service", "service"
    ]
    product_tags: list[str] = Field(default_factory=list)
    packaging_formats: list[str] = Field(default_factory=list)
    stage_coverage: list[
        Literal[
            "ingredient_sourcing",
            "agricultural_production",
            "primary_processing",
            "product_development",
            "manufacturing",
            "private_label",
            "packaging",
            "warehousing",
            "cold_chain",
            "distribution",
            "export_shipping",
        ]
    ] = Field(default_factory=list)
    private_label_supported: bool | None = None
    notes: str | None = None


class Certification(StrictModel):
    name: str
    certification_type: (
        Literal[
            "food_safety",
            "quality",
            "organic",
            "origin_label",
            "religious",
            "social_compliance",
            "facility_registration",
            "market_access",
            "other",
        ]
        | None
    ) = None
    certificate_number: str | None = None
    certified_by: str | None = None
    scope: str | None = None
    status: Literal["claimed", "requested", "verified", "expired"] | None = None
    issued_at: date | None = None
    expires_at: date | None = None


class GeographicalIndication(StrictModel):
    name: str
    designation_type: Literal["PDO", "PGI", "TSG"]
    product_category: str | None = None
    approval_status: Literal["claimed", "authorized", "verified", "revoked", "expired"] | None = (
        None
    )
    approved_by: str | None = None
    approval_reference: str | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    source_registry: Literal["ministry", "elgo_dimitra", "eambrosia", "manual"] | None = None
    registry_url: str | None = None
    specification_url: str | None = None
    notes: str | None = None


class Facility(StrictModel):
    facility_type: Literal[
        "head_office",
        "factory",
        "warehouse",
        "cold_store",
        "distribution_center",
        "other",
    ]
    name: str | None = None
    city: str | None = None
    region: str | None = None
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    temperature_zones: list[Literal["ambient", "chilled", "frozen", "multi_temperature"]] = Field(
        default_factory=list
    )
    notes: str | None = None


class CapacityProfile(StrictModel):
    capacity_scope: Literal["organization", "offering", "facility", "offering_at_facility"]
    scope_name: str | None = None
    capacity_kind: Literal[
        "annual_production", "available_capacity", "storage_capacity", "throughput"
    ]
    quantity: float | None = None
    unit: str | None = None
    available_quantity: float | None = None
    available_unit: str | None = None
    season_start_month: int | None = Field(default=None, ge=1, le=12)
    season_end_month: int | None = Field(default=None, ge=1, le=12)
    lead_time_weeks: float | None = None
    minimum_order_quantity: str | None = None
    notes: str | None = None


class Contact(StrictModel):
    contact_type: Literal["email", "phone", "website", "linkedin", "contact_form"]
    label: str | None = None
    value: str
    is_primary: bool = False


class Source(StrictModel):
    url: str
    source_type: Literal[
        "official_website", "technical_document", "catalog", "trade_directory", "manual_note"
    ]
    title: str | None = None
    notes: str | None = None


class CommercialTerms(StrictModel):
    minimum_order_quantity: str | None = None
    lead_time: str | None = None
    sample_policy: str | None = None
    incoterms: list[str] = Field(default_factory=list)


class IntakeProfile(StrictModel):
    research_status: Literal[
        "seeded",
        "scraped",
        "manually_reviewed",
        "contacted",
        "verified",
        "rejected",
    ]
    company: Company
    market_presence: MarketPresence | None = None
    stage_coverage: list[
        Literal[
            "ingredient_sourcing",
            "agricultural_production",
            "primary_processing",
            "product_development",
            "manufacturing",
            "private_label",
            "packaging",
            "warehousing",
            "cold_chain",
            "distribution",
            "export_shipping",
        ]
    ]
    offerings: list[Offering]
    capabilities: list[str] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    geographical_indications: list[GeographicalIndication] = Field(default_factory=list)
    facilities: list[Facility] = Field(default_factory=list)
    contacts: list[Contact] = Field(default_factory=list)
    capacity_profiles: list[CapacityProfile] = Field(default_factory=list)
    commercial_terms: CommercialTerms | None = None
    public_data_gaps: list[str] = Field(default_factory=list)
    sources: list[Source]
    notes: str | None = None
