from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class SourceRecord:
    source_site: str
    source_sections: list[str]
    listing_url: str
    detail_url: str | None
    company_name: str
    brand_name: str | None = None
    website_url: str | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None
    location: str | None = None
    address: str | None = None
    category: str | None = None
    subcategory: str | None = None
    description: str | None = None
    products_or_services: list[str] = field(default_factory=list)
    sector_guesses: list[str] = field(default_factory=list)
    process_guesses: list[str] = field(default_factory=list)
    stage_coverage_guess: list[str] = field(default_factory=list)
    capability_guesses: list[str] = field(default_factory=list)
    certification_guesses: list[str] = field(default_factory=list)
    organization_type_guess: str = "manufacturer"
    notes: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SourceRecord:
        return cls(**payload)
