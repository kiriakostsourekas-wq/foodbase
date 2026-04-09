from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import TypeAdapter
from sqlalchemy import text
from sqlalchemy.orm import Session

from foodbase.db.session import get_session_factory
from foodbase.intake.models import IntakeProfile

PROFILE_LIST_ADAPTER = TypeAdapter(list[IntakeProfile])

REPO_ROOT = Path(__file__).resolve().parents[3]

STAGE_SORT_ORDER = [
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


@dataclass
class ImportStats:
    created: int = 0
    updated: int = 0
    matched_by_rule: dict[str, int] = field(default_factory=dict)


@dataclass
class OrganizationMatch:
    organization_id: int | None
    rule: str | None


def load_intake_profiles(path: Path) -> list[IntakeProfile]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return PROFILE_LIST_ADAPTER.validate_python(payload)


class IntakeImporter:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._stage_ids: dict[str, int] = {}
        self._channel_ids: dict[str, int] = {}
        self._category_ids: dict[str, int] = {}
        self._capability_ids: dict[str, int] = {}

    def import_profiles(self, profiles: list[IntakeProfile]) -> ImportStats:
        stats = ImportStats()
        for profile in profiles:
            organization_id, created, match_rule = self._import_profile(profile)
            if created:
                stats.created += 1
            else:
                stats.updated += 1
            if match_rule is not None:
                stats.matched_by_rule[match_rule] = stats.matched_by_rule.get(match_rule, 0) + 1

            self.session.execute(
                text(
                    """
                    insert into ingestion_runs (
                      organization_id,
                      run_status,
                      parser_version,
                      extracted_payload,
                      completed_at
                    )
                    values (
                      :organization_id,
                      'succeeded',
                      'intake_import_v1',
                      cast(:payload as jsonb),
                      now()
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "payload": json.dumps(profile.model_dump(mode="json", exclude_none=True)),
                },
            )

        self.session.commit()
        return stats

    def _import_profile(self, profile: IntakeProfile) -> tuple[int, bool, str | None]:
        match = self._match_organization(profile)
        organization_id, created = self._upsert_organization(profile, match)
        self._replace_child_records(organization_id, profile)
        return organization_id, created, match.rule

    def _match_organization(self, profile: IntakeProfile) -> OrganizationMatch:
        company = profile.company
        if company.vat_number:
            organization_id = self.session.execute(
                text("select id from organizations where vat_number = :vat_number"),
                {"vat_number": company.vat_number},
            ).scalar_one_or_none()
            if organization_id is not None:
                return OrganizationMatch(int(organization_id), "vat_number")

        website_host = normalize_host(company.website_url)
        if website_host:
            organization_id = self.session.execute(
                text("select id from organizations where website_host = :website_host"),
                {"website_host": website_host},
            ).scalar_one_or_none()
            if organization_id is not None:
                return OrganizationMatch(int(organization_id), "website_host")

        organization_slug = slugify(company.display_name)
        organization_id = self.session.execute(
            text("select id from organizations where slug = :slug"),
            {"slug": organization_slug},
        ).scalar_one_or_none()
        if organization_id is not None:
            return OrganizationMatch(int(organization_id), "slug")

        normalized_name = normalize_name(company.legal_name or company.display_name)
        organization_id = self.session.execute(
            text(
                """
                select id
                from organizations
                where regexp_replace(
                  lower(coalesce(legal_name, display_name)),
                  '[^a-z0-9]+',
                  '',
                  'g'
                )
                  = :normalized_name
                limit 1
                """
            ),
            {"normalized_name": normalized_name},
        ).scalar_one_or_none()
        if organization_id is not None:
            return OrganizationMatch(int(organization_id), "normalized_name")

        return OrganizationMatch(None, None)

    def _upsert_organization(
        self, profile: IntakeProfile, match: OrganizationMatch
    ) -> tuple[int, bool]:
        company = profile.company
        market_presence = profile.market_presence
        organization_slug = slugify(company.display_name)
        primary_latitude, primary_longitude = self._derive_primary_coordinates(profile)
        metadata = self._build_organization_metadata(profile)

        params: dict[str, Any] = {
            "slug": organization_slug,
            "legal_name": company.legal_name,
            "display_name": company.display_name,
            "vat_number": company.vat_number,
            "company_registration_number": company.company_registration_number,
            "organization_type": company.organization_type,
            "founded_year": company.founded_year,
            "ownership_model": company.ownership_model,
            "employee_count_range": company.employee_count_range,
            "website_url": company.website_url,
            "country_code": company.country_code,
            "headquarters_city": company.headquarters_city,
            "headquarters_region": company.headquarters_region,
            "primary_latitude": primary_latitude,
            "primary_longitude": primary_longitude,
            "serves_greece": market_presence.serves_greece if market_presence else True,
            "supported_languages": market_presence.supported_languages if market_presence else [],
            "summary": company.summary,
            "export_license_status": (
                market_presence.export_license_status
                if market_presence and market_presence.export_license_status
                else "unknown"
            ),
            "export_license_notes": market_presence.export_license_notes
            if market_presence
            else None,
            "public_profile_status": map_public_profile_status(profile.research_status),
            "priority_tier": company.priority_tier,
            "metadata": json.dumps(metadata),
        }

        if match.organization_id is None:
            organization_id = self.session.execute(
                text(
                    """
                    insert into organizations (
                      slug,
                      legal_name,
                      display_name,
                      vat_number,
                      company_registration_number,
                      organization_type,
                      founded_year,
                      ownership_model,
                      employee_count_range,
                      website_url,
                      country_code,
                      headquarters_city,
                      headquarters_region,
                      primary_latitude,
                      primary_longitude,
                      serves_greece,
                      supported_languages,
                      summary,
                      export_license_status,
                      export_license_notes,
                      public_profile_status,
                      priority_tier,
                      metadata
                    )
                    values (
                      :slug,
                      :legal_name,
                      :display_name,
                      :vat_number,
                      :company_registration_number,
                      :organization_type,
                      :founded_year,
                      :ownership_model,
                      :employee_count_range,
                      :website_url,
                      :country_code,
                      :headquarters_city,
                      :headquarters_region,
                      :primary_latitude,
                      :primary_longitude,
                      :serves_greece,
                      :supported_languages,
                      :summary,
                      :export_license_status,
                      :export_license_notes,
                      :public_profile_status,
                      :priority_tier,
                      cast(:metadata as jsonb)
                    )
                    returning id
                    """
                ),
                params,
            ).scalar_one()
            return int(organization_id), True

        params["organization_id"] = match.organization_id
        self.session.execute(
            text(
                """
                update organizations
                set
                  legal_name = coalesce(:legal_name, legal_name),
                  display_name = :display_name,
                  vat_number = coalesce(:vat_number, vat_number),
                  company_registration_number = coalesce(
                    :company_registration_number,
                    company_registration_number
                  ),
                  organization_type = :organization_type,
                  founded_year = coalesce(:founded_year, founded_year),
                  ownership_model = coalesce(:ownership_model, ownership_model),
                  employee_count_range = coalesce(:employee_count_range, employee_count_range),
                  website_url = coalesce(:website_url, website_url),
                  country_code = :country_code,
                  headquarters_city = coalesce(:headquarters_city, headquarters_city),
                  headquarters_region = coalesce(:headquarters_region, headquarters_region),
                  primary_latitude = coalesce(:primary_latitude, primary_latitude),
                  primary_longitude = coalesce(:primary_longitude, primary_longitude),
                  serves_greece = :serves_greece,
                  supported_languages = :supported_languages,
                  summary = coalesce(:summary, summary),
                  export_license_status = :export_license_status,
                  export_license_notes = coalesce(:export_license_notes, export_license_notes),
                  public_profile_status = :public_profile_status,
                  priority_tier = coalesce(:priority_tier, priority_tier),
                  metadata = coalesce(metadata, '{}'::jsonb) || cast(:metadata as jsonb)
                where id = :organization_id
                """
            ),
            params,
        )
        return match.organization_id, False

    def _replace_child_records(self, organization_id: int, profile: IntakeProfile) -> None:
        self._clear_imported_children(organization_id)
        self._insert_contacts(organization_id, profile)
        self._insert_sources(organization_id, profile)
        self._insert_stage_coverage(organization_id, profile.stage_coverage)
        self._insert_channels_and_regions(organization_id, profile)
        offerings_by_name = self._insert_offerings(organization_id, profile)
        facilities_by_name = self._insert_facilities(organization_id, profile)
        self._insert_capabilities(organization_id, profile)
        self._insert_certifications(organization_id, profile)
        self._insert_geographical_indications(organization_id, profile)
        self._insert_capacity_records(
            organization_id, profile, offerings_by_name, facilities_by_name
        )

    def _clear_imported_children(self, organization_id: int) -> None:
        statements = [
            "delete from capacity_records where organization_id = :organization_id",
            (
                "delete from organization_geographical_indications "
                "where organization_id = :organization_id"
            ),
            "delete from organization_certifications where organization_id = :organization_id",
            "delete from organization_capabilities where organization_id = :organization_id",
            "delete from organization_export_markets where organization_id = :organization_id",
            "delete from organization_service_regions where organization_id = :organization_id",
            "delete from organization_channels where organization_id = :organization_id",
            "delete from organization_stage_coverage where organization_id = :organization_id",
            "delete from contacts where organization_id = :organization_id",
            "delete from organization_sources where organization_id = :organization_id",
            (
                "delete from offering_stage_links "
                "where offering_id in ("
                "select id from offerings where organization_id = :organization_id"
                ")"
            ),
            "delete from offerings where organization_id = :organization_id",
            "delete from facilities where organization_id = :organization_id",
        ]
        for statement in statements:
            self.session.execute(text(statement), {"organization_id": organization_id})

    def _insert_contacts(self, organization_id: int, profile: IntakeProfile) -> None:
        contacts = list(profile.contacts)
        if profile.company.website_url and not any(
            contact.contact_type == "website" for contact in contacts
        ):
            from foodbase.intake.models import Contact

            contacts.append(
                Contact(
                    contact_type="website",
                    label="Website",
                    value=profile.company.website_url,
                    is_primary=True,
                )
            )

        seen_primary_types: set[str] = set()
        for contact in contacts:
            is_primary = contact.is_primary and contact.contact_type not in seen_primary_types
            if is_primary:
                seen_primary_types.add(contact.contact_type)
            self.session.execute(
                text(
                    """
                    insert into contacts (
                      organization_id,
                      contact_type,
                      label,
                      value,
                      is_primary
                    )
                    values (
                      :organization_id,
                      :contact_type,
                      :label,
                      :value,
                      :is_primary
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "contact_type": contact.contact_type,
                    "label": contact.label,
                    "value": contact.value,
                    "is_primary": is_primary,
                },
            )

    def _insert_sources(self, organization_id: int, profile: IntakeProfile) -> None:
        for source in profile.sources:
            source_document_id = self.session.execute(
                text(
                    """
                    insert into source_documents (url, source_type, title, metadata)
                    values (
                      :url,
                      :source_type,
                      :title,
                      cast(:metadata as jsonb)
                    )
                    on conflict (url) do update
                    set
                      source_type = excluded.source_type,
                      title = coalesce(excluded.title, source_documents.title),
                      metadata = (
                        coalesce(source_documents.metadata, '{}'::jsonb)
                        || excluded.metadata
                      )
                    returning id
                    """
                ),
                {
                    "url": source.url,
                    "source_type": source.source_type,
                    "title": source.title,
                    "metadata": json.dumps({"notes": source.notes} if source.notes else {}),
                },
            ).scalar_one()
            self.session.execute(
                text(
                    """
                    insert into organization_sources (
                      organization_id,
                      source_document_id,
                      relevance,
                      notes
                    )
                    values (
                      :organization_id,
                      :source_document_id,
                      'profile',
                      :notes
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "source_document_id": source_document_id,
                    "notes": source.notes,
                },
            )

    def _insert_stage_coverage(self, organization_id: int, stage_codes: Sequence[str]) -> None:
        for stage_code in sorted(set(stage_codes), key=lambda code: STAGE_SORT_ORDER.index(code)):
            self.session.execute(
                text(
                    """
                    insert into organization_stage_coverage (
                      organization_id,
                      stage_id
                    )
                    values (
                      :organization_id,
                      :stage_id
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "stage_id": self._stage_id(stage_code),
                },
            )

    def _insert_channels_and_regions(self, organization_id: int, profile: IntakeProfile) -> None:
        market_presence = profile.market_presence
        if market_presence is None:
            if profile.company.headquarters_region:
                self._insert_service_region(
                    organization_id,
                    profile.company.headquarters_region,
                    "headquarters",
                )
            return

        for channel_code in market_presence.channels:
            self.session.execute(
                text(
                    """
                    insert into organization_channels (
                      organization_id,
                      market_channel_id
                    )
                    values (
                      :organization_id,
                      :market_channel_id
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "market_channel_id": self._channel_id(channel_code),
                },
            )

        if profile.company.headquarters_region:
            self._insert_service_region(
                organization_id, profile.company.headquarters_region, "headquarters"
            )

        for region_name in market_presence.regions_in_greece:
            self._insert_service_region(organization_id, region_name, "served")

        for export_market in market_presence.export_markets:
            self.session.execute(
                text(
                    """
                    insert into organization_export_markets (
                      organization_id,
                      market_name,
                      market_status
                    )
                    values (
                      :organization_id,
                      :market_name,
                      'current'
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "market_name": export_market,
                },
            )

    def _insert_service_region(
        self, organization_id: int, region_name: str, coverage_type: str
    ) -> None:
        self.session.execute(
            text(
                """
                insert into organization_service_regions (
                  organization_id,
                  region_name,
                  coverage_type
                )
                values (
                  :organization_id,
                  :region_name,
                  :coverage_type
                )
                """
            ),
            {
                "organization_id": organization_id,
                "region_name": region_name,
                "coverage_type": coverage_type,
            },
        )

    def _insert_offerings(self, organization_id: int, profile: IntakeProfile) -> dict[str, int]:
        offering_ids: dict[str, int] = {}
        for offering in profile.offerings:
            category_id = None
            if offering.product_category_slug:
                category_id = self._category_id(
                    offering.product_category_slug, offering.offering_type
                )

            offering_id = self.session.execute(
                text(
                    """
                    insert into offerings (
                      organization_id,
                      product_category_id,
                      name,
                      subcategory,
                      variety_or_cultivar,
                      offering_type,
                      private_label_supported,
                      packaging_formats,
                      description,
                      metadata
                    )
                    values (
                      :organization_id,
                      :product_category_id,
                      :name,
                      :subcategory,
                      :variety_or_cultivar,
                      :offering_type,
                      :private_label_supported,
                      :packaging_formats,
                      :description,
                      cast(:metadata as jsonb)
                    )
                    returning id
                    """
                ),
                {
                    "organization_id": organization_id,
                    "product_category_id": category_id,
                    "name": offering.name,
                    "subcategory": offering.subcategory,
                    "variety_or_cultivar": offering.variety_or_cultivar,
                    "offering_type": offering.offering_type,
                    "private_label_supported": offering.private_label_supported,
                    "packaging_formats": offering.packaging_formats,
                    "description": offering.notes,
                    "metadata": json.dumps({"product_tags": offering.product_tags}),
                },
            ).scalar_one()
            offering_ids[offering.name] = int(offering_id)

            stage_codes = offering.stage_coverage or profile.stage_coverage
            for stage_code in sorted(
                set(stage_codes), key=lambda code: STAGE_SORT_ORDER.index(code)
            ):
                self.session.execute(
                    text(
                        """
                        insert into offering_stage_links (
                          offering_id,
                          stage_id
                        )
                        values (
                          :offering_id,
                          :stage_id
                        )
                        """
                    ),
                    {
                        "offering_id": offering_id,
                        "stage_id": self._stage_id(stage_code),
                    },
                )

        return offering_ids

    def _insert_facilities(self, organization_id: int, profile: IntakeProfile) -> dict[str, int]:
        facility_ids: dict[str, int] = {}
        for facility in profile.facilities:
            facility_id = self.session.execute(
                text(
                    """
                    insert into facilities (
                      organization_id,
                      facility_type,
                      name,
                      city,
                      region,
                      address,
                      latitude,
                      longitude,
                      temperature_zones,
                      notes
                    )
                    values (
                      :organization_id,
                      :facility_type,
                      :name,
                      :city,
                      :region,
                      :address,
                      :latitude,
                      :longitude,
                      :temperature_zones,
                      :notes
                    )
                    returning id
                    """
                ),
                {
                    "organization_id": organization_id,
                    "facility_type": facility.facility_type,
                    "name": facility.name,
                    "city": facility.city,
                    "region": facility.region,
                    "address": facility.address,
                    "latitude": facility.latitude,
                    "longitude": facility.longitude,
                    "temperature_zones": facility.temperature_zones,
                    "notes": facility.notes,
                },
            ).scalar_one()

            facility_key = (
                facility.name
                or f"{facility.facility_type}:{facility.city or ''}:{facility.region or ''}"
            )
            facility_ids[facility_key] = int(facility_id)
        return facility_ids

    def _insert_capabilities(self, organization_id: int, profile: IntakeProfile) -> None:
        for capability_code in sorted(set(profile.capabilities)):
            capability_id = self._capability_id(capability_code)
            self.session.execute(
                text(
                    """
                    insert into organization_capabilities (
                      organization_id,
                      capability_tag_id
                    )
                    values (
                      :organization_id,
                      :capability_tag_id
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "capability_tag_id": capability_id,
                },
            )

    def _insert_certifications(self, organization_id: int, profile: IntakeProfile) -> None:
        for certification in profile.certifications:
            certification_id = self.session.execute(
                text(
                    """
                    insert into certifications (name, certification_type, issuing_body)
                    values (:name, :certification_type, :issuing_body)
                    on conflict (name) do update
                    set
                      certification_type = coalesce(
                        excluded.certification_type,
                        certifications.certification_type
                      ),
                      issuing_body = coalesce(excluded.issuing_body, certifications.issuing_body)
                    returning id
                    """
                ),
                {
                    "name": certification.name,
                    "certification_type": certification.certification_type or "other",
                    "issuing_body": certification.certified_by,
                },
            ).scalar_one()
            self.session.execute(
                text(
                    """
                    insert into organization_certifications (
                      organization_id,
                      certification_id,
                      certificate_number,
                      certified_by,
                      scope,
                      status,
                      issued_at,
                      expires_at
                    )
                    values (
                      :organization_id,
                      :certification_id,
                      :certificate_number,
                      :certified_by,
                      :scope,
                      :status,
                      :issued_at,
                      :expires_at
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "certification_id": certification_id,
                    "certificate_number": certification.certificate_number,
                    "certified_by": certification.certified_by,
                    "scope": certification.scope,
                    "status": certification.status or "claimed",
                    "issued_at": certification.issued_at,
                    "expires_at": certification.expires_at,
                },
            )

    def _insert_geographical_indications(
        self, organization_id: int, profile: IntakeProfile
    ) -> None:
        for gi_entry in profile.geographical_indications:
            gi_id = self.session.execute(
                text(
                    """
                    insert into geographical_indications (
                      name,
                      designation_type,
                      product_category,
                      source_registry,
                      registry_url,
                      specification_url
                    )
                    values (
                      :name,
                      :designation_type,
                      :product_category,
                      :source_registry,
                      :registry_url,
                      :specification_url
                    )
                    on conflict (country_code, name, designation_type) do update
                    set
                      product_category = coalesce(
                        excluded.product_category,
                        geographical_indications.product_category
                      ),
                      source_registry = excluded.source_registry,
                      registry_url = coalesce(
                        excluded.registry_url,
                        geographical_indications.registry_url
                      ),
                      specification_url = coalesce(
                        excluded.specification_url,
                        geographical_indications.specification_url
                      )
                    returning id
                    """
                ),
                {
                    "name": gi_entry.name,
                    "designation_type": gi_entry.designation_type,
                    "product_category": gi_entry.product_category,
                    "source_registry": gi_entry.source_registry or "manual",
                    "registry_url": gi_entry.registry_url,
                    "specification_url": gi_entry.specification_url,
                },
            ).scalar_one()
            self.session.execute(
                text(
                    """
                    insert into organization_geographical_indications (
                      organization_id,
                      geographical_indication_id,
                      approval_status,
                      approved_by,
                      approval_reference,
                      valid_from,
                      valid_until,
                      notes
                    )
                    values (
                      :organization_id,
                      :geographical_indication_id,
                      :approval_status,
                      :approved_by,
                      :approval_reference,
                      :valid_from,
                      :valid_until,
                      :notes
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "geographical_indication_id": gi_id,
                    "approval_status": gi_entry.approval_status or "claimed",
                    "approved_by": gi_entry.approved_by,
                    "approval_reference": gi_entry.approval_reference,
                    "valid_from": gi_entry.valid_from,
                    "valid_until": gi_entry.valid_until,
                    "notes": gi_entry.notes,
                },
            )

    def _insert_capacity_records(
        self,
        organization_id: int,
        profile: IntakeProfile,
        offerings_by_name: dict[str, int],
        facilities_by_name: dict[str, int],
    ) -> None:
        capacity_profiles = list(profile.capacity_profiles)
        if profile.commercial_terms and (
            profile.commercial_terms.minimum_order_quantity or profile.commercial_terms.lead_time
        ):
            from foodbase.intake.models import CapacityProfile

            has_organization_commercial_capacity = any(
                capacity_profile.capacity_scope == "organization"
                and capacity_profile.minimum_order_quantity
                == profile.commercial_terms.minimum_order_quantity
                for capacity_profile in capacity_profiles
            )
            if not has_organization_commercial_capacity:
                capacity_profiles.append(
                    CapacityProfile(
                        capacity_scope="organization",
                        capacity_kind="available_capacity",
                        minimum_order_quantity=profile.commercial_terms.minimum_order_quantity,
                        notes=profile.commercial_terms.lead_time,
                    )
                )

        for capacity_profile in capacity_profiles:
            offering_id = None
            facility_id = None
            scope_name = capacity_profile.scope_name
            if (
                capacity_profile.capacity_scope in {"offering", "offering_at_facility"}
                and scope_name
            ):
                offering_id = offerings_by_name.get(scope_name)
            if (
                capacity_profile.capacity_scope in {"facility", "offering_at_facility"}
                and scope_name
            ):
                facility_id = facilities_by_name.get(scope_name)

            self.session.execute(
                text(
                    """
                    insert into capacity_records (
                      organization_id,
                      offering_id,
                      facility_id,
                      capacity_scope,
                      capacity_kind,
                      quantity,
                      unit,
                      available_quantity,
                      available_unit,
                      season_start_month,
                      season_end_month,
                      lead_time_weeks,
                      minimum_order_quantity,
                      notes
                    )
                    values (
                      :organization_id,
                      :offering_id,
                      :facility_id,
                      :capacity_scope,
                      :capacity_kind,
                      :quantity,
                      :unit,
                      :available_quantity,
                      :available_unit,
                      :season_start_month,
                      :season_end_month,
                      :lead_time_weeks,
                      :minimum_order_quantity,
                      :notes
                    )
                    """
                ),
                {
                    "organization_id": organization_id,
                    "offering_id": offering_id,
                    "facility_id": facility_id,
                    "capacity_scope": capacity_profile.capacity_scope,
                    "capacity_kind": capacity_profile.capacity_kind,
                    "quantity": capacity_profile.quantity,
                    "unit": capacity_profile.unit,
                    "available_quantity": capacity_profile.available_quantity,
                    "available_unit": capacity_profile.available_unit,
                    "season_start_month": capacity_profile.season_start_month,
                    "season_end_month": capacity_profile.season_end_month,
                    "lead_time_weeks": capacity_profile.lead_time_weeks,
                    "minimum_order_quantity": capacity_profile.minimum_order_quantity,
                    "notes": capacity_profile.notes,
                },
            )

    def _derive_primary_coordinates(
        self, profile: IntakeProfile
    ) -> tuple[float | None, float | None]:
        if (
            profile.company.headquarters_latitude is not None
            and profile.company.headquarters_longitude is not None
        ):
            return profile.company.headquarters_latitude, profile.company.headquarters_longitude

        for facility in profile.facilities:
            if facility.latitude is not None and facility.longitude is not None:
                return facility.latitude, facility.longitude

        if profile.company.headquarters_region:
            row = (
                self.session.execute(
                    text(
                        """
                    select center_latitude, center_longitude
                    from geographic_regions
                    where name = :region_name
                    limit 1
                    """
                    ),
                    {"region_name": profile.company.headquarters_region},
                )
                .mappings()
                .first()
            )
            if row is not None:
                return row["center_latitude"], row["center_longitude"]

        return None, None

    def _build_organization_metadata(self, profile: IntakeProfile) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "research_status": profile.research_status,
            "public_data_gaps": profile.public_data_gaps,
        }
        if profile.commercial_terms:
            metadata["commercial_terms"] = profile.commercial_terms.model_dump(exclude_none=True)
        if profile.notes:
            metadata["notes"] = profile.notes
        return metadata

    def _stage_id(self, stage_code: str) -> int:
        if stage_code not in self._stage_ids:
            stage_id = self.session.execute(
                text("select id from supply_chain_stages where code = :code"),
                {"code": stage_code},
            ).scalar_one()
            self._stage_ids[stage_code] = int(stage_id)
        return self._stage_ids[stage_code]

    def _channel_id(self, channel_code: str) -> int:
        if channel_code not in self._channel_ids:
            channel_id = self.session.execute(
                text("select id from market_channels where code = :code"),
                {"code": channel_code},
            ).scalar_one()
            self._channel_ids[channel_code] = int(channel_id)
        return self._channel_ids[channel_code]

    def _category_id(self, category_slug: str, offering_type: str) -> int:
        if category_slug not in self._category_ids:
            category_id = self.session.execute(
                text(
                    """
                    insert into product_categories (slug, name, category_type)
                    values (
                      :slug,
                      :name,
                      :category_type
                    )
                    on conflict (slug) do update
                    set
                      name = excluded.name
                    returning id
                    """
                ),
                {
                    "slug": category_slug,
                    "name": humanize_slug(category_slug),
                    "category_type": map_offering_to_category_type(offering_type),
                },
            ).scalar_one()
            self._category_ids[category_slug] = int(category_id)
        return self._category_ids[category_slug]

    def _capability_id(self, capability_code: str) -> int:
        if capability_code not in self._capability_ids:
            capability_id = self.session.execute(
                text(
                    """
                    insert into capability_tags (code, name)
                    values (
                      :code,
                      :name
                    )
                    on conflict (code) do update
                    set
                      name = excluded.name
                    returning id
                    """
                ),
                {
                    "code": capability_code,
                    "name": humanize_slug(capability_code),
                },
            ).scalar_one()
            self._capability_ids[capability_code] = int(capability_id)
        return self._capability_ids[capability_code]


def map_public_profile_status(research_status: str) -> str:
    mapping = {
        "seeded": "seeded",
        "scraped": "researching",
        "manually_reviewed": "seeded",
        "contacted": "contacted",
        "verified": "verified",
        "rejected": "archived",
    }
    return mapping.get(research_status, "researching")


def normalize_host(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    host = parsed.netloc.lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    collapsed = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    return collapsed or "organization"


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def humanize_slug(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").title()


def map_offering_to_category_type(offering_type: str) -> str:
    if offering_type == "packaging":
        return "packaging"
    if offering_type == "ingredient":
        return "ingredient"
    if offering_type in {"service", "logistics_service"}:
        return "service"
    return "finished_product"


def import_profiles_from_path(path: Path) -> ImportStats:
    profiles = load_intake_profiles(path)
    session_factory = get_session_factory()
    with session_factory() as session:
        importer = IntakeImporter(session)
        return importer.import_profiles(profiles)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Foodbase intake JSON into Postgres.")
    parser.add_argument("path", type=Path, help="Path to a JSON file containing intake records.")
    args = parser.parse_args()
    stats = import_profiles_from_path(args.path)
    print(f"created={stats.created}")
    print(f"updated={stats.updated}")
    if stats.matched_by_rule:
        print("matched_by_rule=" + json.dumps(stats.matched_by_rule, sort_keys=True))


if __name__ == "__main__":
    main()
