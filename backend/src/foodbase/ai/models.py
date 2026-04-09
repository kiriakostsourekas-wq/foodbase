from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProductProfileRequest(BaseModel):
    prompt: str = Field(min_length=10, max_length=4000)
    answers: dict[str, Any] = Field(default_factory=dict)


class ProductProfileResponse(StrictModel):
    name: str
    summary: str
    description: str
    category_slug: str
    category_label: str
    subcategory: str
    positioning: list[str]
    target_audience: list[str]
    channels: list[str]
    packaging: str
    ingredients: list[str]
    certifications: list[str]
    moq: str
    lead_time: str
    price_tier: str
    sales_estimate: str
    readiness_score: int = Field(ge=0, le=100)
    confidence: str
    rationale: str
    organic_required: bool
    private_label_required: bool
    export_ready_required: bool
    preferred_regions: list[str]


class SupplierTeamRequest(BaseModel):
    product_profile: ProductProfileResponse
    max_suppliers: int = Field(default=5, ge=1, le=6)


class StructuredSupplierSelection(StrictModel):
    slug: str
    role: str
    reason: str
    fit_score: int = Field(ge=0, le=100)


class StructuredSupplierTeamResponse(StrictModel):
    summary: str
    estimated_lead_time: str
    selections: list[StructuredSupplierSelection]


class SupplierTeamItem(BaseModel):
    id: int
    slug: str
    name: str
    city: str | None = None
    region: str | None = None
    role: str
    reason: str
    fit_score: int
    certifications: list[str] = Field(default_factory=list)
    verified: bool = False
    organic: bool = False
    private_label: bool = False
    export_ready: bool = False
    lead_time: str | None = None
    moq: str | None = None
    short_description: str | None = None
    website_url: str | None = None


class SupplierTeamResponse(BaseModel):
    summary: str
    average_fit_score: int
    estimated_lead_time: str
    candidate_count: int
    dataset_note: str
    suppliers: list[SupplierTeamItem]
