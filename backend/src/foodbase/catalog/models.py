from pydantic import BaseModel, Field


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int


class OrganizationListItem(BaseModel):
    id: int
    slug: str
    name: str
    city: str | None = None
    region: str | None = None
    lat: float | None = None
    lng: float | None = None
    category: str | None = None
    category_label: str | None = None
    subcategory: str | None = None
    description: str | None = None
    short_description: str | None = None
    certifications: list[str] = Field(default_factory=list)
    moq: str | None = None
    lead_time: str | None = None
    capacity: str | None = None
    export_ready: bool = False
    private_label: bool = False
    organic: bool = False
    verified: bool = False
    year_founded: int | None = None
    employees: str | None = None
    export_markets: list[str] = Field(default_factory=list)


class OrganizationListResponse(BaseModel):
    items: list[OrganizationListItem]
    pagination: Pagination


class FacetOption(BaseModel):
    value: str
    label: str
    count: int


class SearchFacetsResponse(BaseModel):
    categories: list[FacetOption]
    regions: list[FacetOption]
    certifications: list[FacetOption]
    designations: list[FacetOption]


class CategorySummary(BaseModel):
    slug: str
    name: str
    parent_slug: str | None = None
    category_type: str
    count: int


class GeographicalIndicationSummary(BaseModel):
    id: int
    name: str
    designation_type: str
    product_category: str | None = None
    source_registry: str
    registry_url: str | None = None
    specification_url: str | None = None
    organization_count: int


class ContactSummary(BaseModel):
    contact_type: str
    label: str | None = None
    value: str
    is_primary: bool


class FacilitySummary(BaseModel):
    facility_type: str
    name: str | None = None
    city: str | None = None
    region: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    temperature_zones: list[str] = Field(default_factory=list)
    notes: str | None = None


class OfferingSummary(BaseModel):
    name: str
    category: str | None = None
    category_label: str | None = None
    subcategory: str | None = None
    variety_or_cultivar: str | None = None
    offering_type: str
    private_label_supported: bool | None = None
    packaging_formats: list[str] = Field(default_factory=list)
    description: str | None = None
    stage_coverage: list[str] = Field(default_factory=list)
    product_tags: list[str] = Field(default_factory=list)


class CertificationSummary(BaseModel):
    name: str
    certification_type: str | None = None
    certified_by: str | None = None
    scope: str | None = None
    status: str
    issued_at: str | None = None
    expires_at: str | None = None


class GeographicalIndicationAuthorization(BaseModel):
    name: str
    designation_type: str
    product_category: str | None = None
    approval_status: str
    approved_by: str | None = None
    approval_reference: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    registry_url: str | None = None
    specification_url: str | None = None
    notes: str | None = None


class CapacityRecordSummary(BaseModel):
    capacity_scope: str
    capacity_kind: str
    scope_name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    available_quantity: float | None = None
    available_unit: str | None = None
    season_start_month: int | None = None
    season_end_month: int | None = None
    lead_time_weeks: float | None = None
    minimum_order_quantity: str | None = None
    notes: str | None = None


class SourceSummary(BaseModel):
    url: str
    source_type: str
    title: str | None = None
    notes: str | None = None


class OrganizationDetail(BaseModel):
    id: int
    slug: str
    name: str
    legal_name: str | None = None
    organization_type: str
    summary: str | None = None
    city: str | None = None
    region: str | None = None
    lat: float | None = None
    lng: float | None = None
    website_url: str | None = None
    supported_languages: list[str] = Field(default_factory=list)
    year_founded: int | None = None
    employees: str | None = None
    export_ready: bool = False
    private_label: bool = False
    organic: bool = False
    verified: bool = False
    moq: str | None = None
    lead_time: str | None = None
    capacity: str | None = None
    export_markets: list[str] = Field(default_factory=list)
    certifications: list[CertificationSummary] = Field(default_factory=list)
    geographical_indications: list[GeographicalIndicationAuthorization] = Field(
        default_factory=list
    )
    contacts: list[ContactSummary] = Field(default_factory=list)
    facilities: list[FacilitySummary] = Field(default_factory=list)
    offerings: list[OfferingSummary] = Field(default_factory=list)
    capacity_records: list[CapacityRecordSummary] = Field(default_factory=list)
    sources: list[SourceSummary] = Field(default_factory=list)
    logo_url: str | None = None
    hero_image_url: str | None = None
    gallery_urls: list[str] = Field(default_factory=list)
    rating: float | None = None
    review_count: int | None = None
    response_rate: int | None = None
    response_time: str | None = None
    sustainability_score: int | None = None
    pricing_tier: str | None = None
