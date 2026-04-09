from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from foodbase.catalog.models import (
    CapacityRecordSummary,
    CategorySummary,
    CertificationSummary,
    ContactSummary,
    FacetOption,
    FacilitySummary,
    GeographicalIndicationAuthorization,
    GeographicalIndicationSummary,
    OfferingSummary,
    OrganizationDetail,
    OrganizationListItem,
    OrganizationListResponse,
    Pagination,
    SearchFacetsResponse,
    SourceSummary,
)


def list_organizations(
    session: Session,
    *,
    q: str | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    region: str | None = None,
    certification: str | None = None,
    designation: str | None = None,
    private_label: bool | None = None,
    export_market: str | None = None,
    export_ready: bool | None = None,
    organic: bool | None = None,
    verified: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> OrganizationListResponse:
    where_clauses, params = _build_organization_filters(
        q=q,
        category=category,
        subcategory=subcategory,
        region=region,
        certification=certification,
        designation=designation,
        private_label=private_label,
        export_market=export_market,
        export_ready=export_ready,
        organic=organic,
        verified=verified,
    )
    params.update({"limit": limit, "offset": offset})
    where_sql = " and ".join(where_clauses)

    total = session.execute(
        text(f"select count(*) from organizations o where {where_sql}"),
        params,
    ).scalar_one()

    rows = (
        session.execute(
            text(
                f"""
            select
              o.id,
              o.slug,
              o.display_name as name,
              o.headquarters_city as city,
              o.headquarters_region as region,
              o.primary_latitude as lat,
              o.primary_longitude as lng,
              o.summary as description,
              o.founded_year as year_founded,
              o.employee_count_range as employees,
              o.public_profile_status = 'verified' as verified,
              (
                o.export_license_status in ('held', 'not_required')
                or exists (
                  select 1
                  from organization_export_markets oem
                  where oem.organization_id = o.id
                )
              ) as export_ready,
              coalesce(primary_offering.category_slug, null) as category,
              coalesce(primary_offering.category_name, null) as category_label,
              primary_offering.subcategory,
              coalesce(primary_offering.private_label_supported, false) as private_label,
              coalesce(certs.certifications, '{{}}'::text[]) as certifications,
              coalesce(export_markets.markets, '{{}}'::text[]) as export_markets,
              coalesce(
                capacity_info.minimum_order_quantity,
                o.metadata -> 'commercial_terms' ->> 'minimum_order_quantity'
              ) as moq,
              coalesce(
                capacity_info.lead_time,
                o.metadata -> 'commercial_terms' ->> 'lead_time'
              ) as lead_time,
              capacity_info.capacity_summary as capacity,
              exists (
                select 1
                from organization_certifications oc
                join certifications c on c.id = oc.certification_id
                where oc.organization_id = o.id
                  and c.certification_type = 'organic'
              ) as organic
            from organizations o
            left join lateral (
              select
                child.slug as category_slug,
                child.name as category_name,
                off.subcategory,
                off.private_label_supported
              from offerings off
              left join product_categories child on child.id = off.product_category_id
              where off.organization_id = o.id
              order by
                off.private_label_supported desc nulls last,
                off.id
              limit 1
            ) primary_offering on true
            left join lateral (
              select array_agg(distinct c.name order by c.name) as certifications
              from organization_certifications oc
              join certifications c on c.id = oc.certification_id
              where oc.organization_id = o.id
            ) certs on true
            left join lateral (
              select array_agg(distinct market_name order by market_name) as markets
              from organization_export_markets
              where organization_id = o.id
            ) export_markets on true
            left join lateral (
              select
                max(minimum_order_quantity) filter (where minimum_order_quantity is not null)
                  as minimum_order_quantity,
                max(
                  case
                    when lead_time_weeks is not null then
                      trim(to_char(lead_time_weeks, 'FM999990.##')) || ' weeks'
                  end
                ) as lead_time,
                coalesce(
                  max(
                    case
                      when quantity is not null and unit is not null then
                        trim(to_char(quantity, 'FM999999999990.##')) || ' ' || unit
                    end
                  ),
                  max(notes)
                ) as capacity_summary
              from capacity_records cr
              where cr.organization_id = o.id
            ) capacity_info on true
            where {where_sql}
            order by
              (o.public_profile_status = 'verified') desc,
              o.priority_tier asc nulls last,
              o.display_name asc
            limit :limit
            offset :offset
            """
            ),
            params,
        )
        .mappings()
        .all()
    )

    items = [
        OrganizationListItem(
            id=int(row["id"]),
            slug=row["slug"],
            name=row["name"],
            city=row["city"],
            region=row["region"],
            lat=row["lat"],
            lng=row["lng"],
            category=row["category"],
            category_label=row["category_label"],
            subcategory=row["subcategory"],
            description=row["description"],
            short_description=_short_description(row["description"]),
            certifications=list(row["certifications"] or []),
            moq=row["moq"],
            lead_time=row["lead_time"],
            capacity=row["capacity"],
            export_ready=bool(row["export_ready"]),
            private_label=bool(row["private_label"]),
            organic=bool(row["organic"]),
            verified=bool(row["verified"]),
            year_founded=row["year_founded"],
            employees=row["employees"],
            export_markets=list(row["export_markets"] or []),
        )
        for row in rows
    ]

    return OrganizationListResponse(
        items=items,
        pagination=Pagination(total=int(total), limit=limit, offset=offset),
    )


def get_organization_detail(session: Session, slug: str) -> OrganizationDetail:
    row = (
        session.execute(
            text(
                """
            select
              o.id,
              o.slug,
              o.legal_name,
              o.display_name as name,
              o.organization_type,
              o.summary,
              o.website_url,
              o.headquarters_city as city,
              o.headquarters_region as region,
              o.primary_latitude as lat,
              o.primary_longitude as lng,
              o.supported_languages,
              o.founded_year as year_founded,
              o.employee_count_range as employees,
              o.public_profile_status = 'verified' as verified,
              (
                o.export_license_status in ('held', 'not_required')
                or exists (
                  select 1
                  from organization_export_markets oem
                  where oem.organization_id = o.id
                )
              ) as export_ready,
              exists (
                select 1
                from organization_certifications oc
                join certifications c on c.id = oc.certification_id
                where oc.organization_id = o.id
                  and c.certification_type = 'organic'
              ) as organic,
              exists (
                select 1
                from offerings off
                where off.organization_id = o.id
                  and off.private_label_supported = true
              ) as private_label,
              coalesce(
                (
                  select max(minimum_order_quantity)
                  from capacity_records
                  where organization_id = o.id
                    and minimum_order_quantity is not null
                ),
                o.metadata -> 'commercial_terms' ->> 'minimum_order_quantity'
              ) as moq,
              coalesce(
                (
                  select max(
                    case
                      when lead_time_weeks is not null then
                        trim(to_char(lead_time_weeks, 'FM999990.##')) || ' weeks'
                    end
                  )
                  from capacity_records
                  where organization_id = o.id
                ),
                o.metadata -> 'commercial_terms' ->> 'lead_time'
              ) as lead_time,
              (
                select coalesce(
                  max(
                    case
                      when quantity is not null and unit is not null then
                        trim(to_char(quantity, 'FM999999999990.##')) || ' ' || unit
                    end
                  ),
                  max(notes)
                )
                from capacity_records
                where organization_id = o.id
              ) as capacity,
              o.metadata
            from organizations o
            where o.slug = :slug
            """
            ),
            {"slug": slug},
        )
        .mappings()
        .first()
    )

    if row is None:
        raise HTTPException(status_code=404, detail="Organization not found.")

    metadata = row["metadata"] or {}
    commercial_terms = metadata.get("commercial_terms", {})
    detail = OrganizationDetail(
        id=int(row["id"]),
        slug=row["slug"],
        name=row["name"],
        legal_name=row["legal_name"],
        organization_type=row["organization_type"],
        summary=row["summary"],
        city=row["city"],
        region=row["region"],
        lat=row["lat"],
        lng=row["lng"],
        website_url=row["website_url"],
        supported_languages=list(row["supported_languages"] or []),
        year_founded=row["year_founded"],
        employees=row["employees"],
        export_ready=bool(row["export_ready"]),
        private_label=bool(row["private_label"]),
        organic=bool(row["organic"]),
        verified=bool(row["verified"]),
        moq=row["moq"] or commercial_terms.get("minimum_order_quantity"),
        lead_time=row["lead_time"] or commercial_terms.get("lead_time"),
        capacity=row["capacity"],
        logo_url=metadata.get("logo_url"),
        hero_image_url=metadata.get("hero_image_url"),
        gallery_urls=list(metadata.get("gallery_urls", [])),
        rating=metadata.get("rating"),
        review_count=metadata.get("review_count"),
        response_rate=metadata.get("response_rate"),
        response_time=metadata.get("response_time"),
        sustainability_score=metadata.get("sustainability_score"),
        pricing_tier=metadata.get("pricing_tier"),
    )

    detail.export_markets = _fetch_export_markets(session, detail.id)
    detail.contacts = _fetch_contacts(session, detail.id)
    detail.facilities = _fetch_facilities(session, detail.id)
    detail.offerings = _fetch_offerings(session, detail.id)
    detail.certifications = _fetch_certifications(session, detail.id)
    detail.geographical_indications = _fetch_geographical_indications(session, detail.id)
    detail.capacity_records = _fetch_capacity_records(session, detail.id)
    detail.sources = _fetch_sources(session, detail.id)

    return detail


def list_categories(session: Session) -> list[CategorySummary]:
    rows = (
        session.execute(
            text(
                """
            with category_counts as (
              select
                coalesce(parent.slug, child.slug) as root_slug,
                count(distinct off.organization_id) as organization_count
              from product_categories child
              left join product_categories parent on parent.id = child.parent_id
              left join offerings off on off.product_category_id = child.id
              group by coalesce(parent.slug, child.slug)
            )
            select
              child.slug,
              child.name,
              parent.slug as parent_slug,
              child.category_type,
              coalesce(cc.organization_count, 0) as count
            from product_categories child
            left join product_categories parent on parent.id = child.parent_id
            left join category_counts cc on cc.root_slug = child.slug
            where parent.id is null
            order by child.name asc
            """
            )
        )
        .mappings()
        .all()
    )

    return [
        CategorySummary(
            slug=row["slug"],
            name=row["name"],
            parent_slug=row["parent_slug"],
            category_type=row["category_type"],
            count=int(row["count"]),
        )
        for row in rows
    ]


def list_geographical_indications(session: Session) -> list[GeographicalIndicationSummary]:
    rows = (
        session.execute(
            text(
                """
            select
              gi.id,
              gi.name,
              gi.designation_type,
              gi.product_category,
              gi.source_registry,
              gi.registry_url,
              gi.specification_url,
              count(distinct ogi.organization_id) as organization_count
            from geographical_indications gi
            left join organization_geographical_indications ogi
              on ogi.geographical_indication_id = gi.id
            group by
              gi.id,
              gi.name,
              gi.designation_type,
              gi.product_category,
              gi.source_registry,
              gi.registry_url,
              gi.specification_url
            order by gi.designation_type asc, gi.name asc
            """
            )
        )
        .mappings()
        .all()
    )

    return [
        GeographicalIndicationSummary(
            id=int(row["id"]),
            name=row["name"],
            designation_type=row["designation_type"],
            product_category=row["product_category"],
            source_registry=row["source_registry"],
            registry_url=row["registry_url"],
            specification_url=row["specification_url"],
            organization_count=int(row["organization_count"]),
        )
        for row in rows
    ]


def get_search_facets(session: Session) -> SearchFacetsResponse:
    category_rows = (
        session.execute(
            text(
                """
            with category_counts as (
              select
                coalesce(parent.slug, child.slug) as slug,
                count(distinct off.organization_id) as organization_count
              from product_categories child
              left join product_categories parent on parent.id = child.parent_id
              join offerings off on off.product_category_id = child.id
              group by coalesce(parent.slug, child.slug)
            )
            select
              category.slug as value,
              category.name as label,
              coalesce(category_counts.organization_count, 0) as count
            from product_categories category
            left join category_counts on category_counts.slug = category.slug
            where category.parent_id is null
            order by category.name asc
            """
            )
        )
        .mappings()
        .all()
    )

    region_rows = (
        session.execute(
            text(
                """
            select
              headquarters_region as value,
              headquarters_region as label,
              count(*) as count
            from organizations
            where headquarters_region is not null
            group by headquarters_region
            order by count desc, headquarters_region asc
            """
            )
        )
        .mappings()
        .all()
    )

    certification_rows = (
        session.execute(
            text(
                """
            select
              c.name as value,
              c.name as label,
              count(distinct oc.organization_id) as count
            from certifications c
            left join organization_certifications oc on oc.certification_id = c.id
            group by c.name
            order by count desc, c.name asc
            """
            )
        )
        .mappings()
        .all()
    )

    designation_rows = (
        session.execute(
            text(
                """
            with designation_counts as (
              select
                gi.designation_type,
                count(distinct ogi.organization_id) as count
              from geographical_indications gi
              left join organization_geographical_indications ogi
                on ogi.geographical_indication_id = gi.id
              group by gi.designation_type
            )
            select
              designation_type as value,
              designation_type as label,
              count
            from designation_counts
            union all
            select value, value as label, 0 as count
            from (values ('PDO'), ('PGI'), ('TSG')) defaults(value)
            where not exists (
              select 1
              from designation_counts
              where designation_counts.designation_type = defaults.value
            )
            order by label asc
            """
            )
        )
        .mappings()
        .all()
    )

    return SearchFacetsResponse(
        categories=[FacetOption(**row) for row in category_rows],
        regions=[FacetOption(**row) for row in region_rows],
        certifications=[FacetOption(**row) for row in certification_rows],
        designations=[FacetOption(**row) for row in designation_rows],
    )


def _fetch_export_markets(session: Session, organization_id: int) -> list[str]:
    rows = (
        session.execute(
            text(
                """
            select market_name
            from organization_export_markets
            where organization_id = :organization_id
            order by market_name asc
            """
            ),
            {"organization_id": organization_id},
        )
        .scalars()
        .all()
    )
    return [str(row) for row in rows]


def _fetch_contacts(session: Session, organization_id: int) -> list[ContactSummary]:
    rows = (
        session.execute(
            text(
                """
            select contact_type, label, value, is_primary
            from contacts
            where organization_id = :organization_id
            order by is_primary desc, contact_type asc, value asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )
    return [ContactSummary(**row) for row in rows]


def _fetch_facilities(session: Session, organization_id: int) -> list[FacilitySummary]:
    rows = (
        session.execute(
            text(
                """
            select
              facility_type,
              name,
              city,
              region,
              address,
              latitude,
              longitude,
              temperature_zones,
              notes
            from facilities
            where organization_id = :organization_id
            order by id asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )
    return [FacilitySummary(**row) for row in rows]


def _fetch_offerings(session: Session, organization_id: int) -> list[OfferingSummary]:
    rows = (
        session.execute(
            text(
                """
            select
              off.id,
              off.name,
              pc.slug as category,
              pc.name as category_label,
              off.subcategory,
              off.variety_or_cultivar,
              off.offering_type,
              off.private_label_supported,
              off.packaging_formats,
              off.description,
              off.metadata
            from offerings off
            left join product_categories pc on pc.id = off.product_category_id
            where off.organization_id = :organization_id
            order by off.id asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )

    offerings: list[OfferingSummary] = []
    for row in rows:
        stage_rows = (
            session.execute(
                text(
                    """
                select scs.code
                from offering_stage_links osl
                join supply_chain_stages scs on scs.id = osl.stage_id
                where osl.offering_id = :offering_id
                order by scs.sort_order asc
                """
                ),
                {"offering_id": row["id"]},
            )
            .scalars()
            .all()
        )
        metadata = row["metadata"] or {}
        offerings.append(
            OfferingSummary(
                name=row["name"],
                category=row["category"],
                category_label=row["category_label"],
                subcategory=row["subcategory"],
                variety_or_cultivar=row["variety_or_cultivar"],
                offering_type=row["offering_type"],
                private_label_supported=row["private_label_supported"],
                packaging_formats=list(row["packaging_formats"] or []),
                description=row["description"],
                stage_coverage=[str(code) for code in stage_rows],
                product_tags=list(metadata.get("product_tags", [])),
            )
        )
    return offerings


def _fetch_certifications(session: Session, organization_id: int) -> list[CertificationSummary]:
    rows = (
        session.execute(
            text(
                """
            select
              c.name,
              c.certification_type,
              oc.certified_by,
              oc.scope,
              oc.status,
              oc.issued_at::text as issued_at,
              oc.expires_at::text as expires_at
            from organization_certifications oc
            join certifications c on c.id = oc.certification_id
            where oc.organization_id = :organization_id
            order by c.name asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )
    return [CertificationSummary(**row) for row in rows]


def _fetch_geographical_indications(
    session: Session,
    organization_id: int,
) -> list[GeographicalIndicationAuthorization]:
    rows = (
        session.execute(
            text(
                """
            select
              gi.name,
              gi.designation_type,
              gi.product_category,
              ogi.approval_status,
              ogi.approved_by,
              ogi.approval_reference,
              ogi.valid_from::text as valid_from,
              ogi.valid_until::text as valid_until,
              gi.registry_url,
              gi.specification_url,
              ogi.notes
            from organization_geographical_indications ogi
            join geographical_indications gi on gi.id = ogi.geographical_indication_id
            where ogi.organization_id = :organization_id
            order by gi.designation_type asc, gi.name asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )
    return [GeographicalIndicationAuthorization(**row) for row in rows]


def _fetch_capacity_records(session: Session, organization_id: int) -> list[CapacityRecordSummary]:
    rows = (
        session.execute(
            text(
                """
            select
              cr.capacity_scope,
              cr.capacity_kind,
              coalesce(off.name, fac.name) as scope_name,
              cr.quantity,
              cr.unit,
              cr.available_quantity,
              cr.available_unit,
              cr.season_start_month,
              cr.season_end_month,
              cr.lead_time_weeks,
              cr.minimum_order_quantity,
              cr.notes
            from capacity_records cr
            left join offerings off on off.id = cr.offering_id
            left join facilities fac on fac.id = cr.facility_id
            where cr.organization_id = :organization_id
            order by cr.id asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )
    return [CapacityRecordSummary(**row) for row in rows]


def _fetch_sources(session: Session, organization_id: int) -> list[SourceSummary]:
    rows = (
        session.execute(
            text(
                """
            select
              sd.url,
              sd.source_type,
              sd.title,
              os.notes
            from organization_sources os
            join source_documents sd on sd.id = os.source_document_id
            where os.organization_id = :organization_id
            order by sd.created_at asc
            """
            ),
            {"organization_id": organization_id},
        )
        .mappings()
        .all()
    )
    return [SourceSummary(**row) for row in rows]


def _build_organization_filters(
    *,
    q: str | None,
    category: str | None,
    subcategory: str | None,
    region: str | None,
    certification: str | None,
    designation: str | None,
    private_label: bool | None,
    export_market: str | None,
    export_ready: bool | None,
    organic: bool | None,
    verified: bool | None,
) -> tuple[list[str], dict[str, Any]]:
    where_clauses = ["1 = 1"]
    params: dict[str, Any] = {}

    if q:
        params["q_like"] = f"%{q}%"
        where_clauses.append(
            """
            (
              o.display_name ilike :q_like
              or coalesce(o.summary, '') ilike :q_like
              or coalesce(o.headquarters_city, '') ilike :q_like
              or coalesce(o.headquarters_region, '') ilike :q_like
              or exists (
                select 1
                from offerings off
                where off.organization_id = o.id
                  and (
                    off.name ilike :q_like
                    or coalesce(off.subcategory, '') ilike :q_like
                    or coalesce(off.variety_or_cultivar, '') ilike :q_like
                  )
              )
            )
            """
        )

    if category:
        params["category"] = category
        where_clauses.append(
            """
            exists (
              select 1
              from offerings off
              join product_categories child on child.id = off.product_category_id
              left join product_categories parent on parent.id = child.parent_id
              where off.organization_id = o.id
                and :category in (child.slug, parent.slug)
            )
            """
        )

    if subcategory:
        params["subcategory"] = subcategory
        where_clauses.append(
            """
            exists (
              select 1
              from offerings off
              where off.organization_id = o.id
                and off.subcategory ilike :subcategory
            )
            """
        )
        params["subcategory"] = f"%{subcategory}%"

    if region:
        params["region"] = region
        where_clauses.append("o.headquarters_region = :region")

    if certification:
        params["certification"] = certification
        where_clauses.append(
            """
            exists (
              select 1
              from organization_certifications oc
              join certifications c on c.id = oc.certification_id
              where oc.organization_id = o.id
                and c.name = :certification
            )
            """
        )

    if designation:
        params["designation"] = designation
        where_clauses.append(
            """
            exists (
              select 1
              from organization_geographical_indications ogi
              join geographical_indications gi on gi.id = ogi.geographical_indication_id
              where ogi.organization_id = o.id
                and gi.designation_type = :designation
            )
            """
        )

    if private_label:
        where_clauses.append(
            """
            exists (
              select 1
              from offerings off
              where off.organization_id = o.id
                and off.private_label_supported = true
            )
            """
        )

    if export_market:
        params["export_market"] = export_market
        where_clauses.append(
            """
            exists (
              select 1
              from organization_export_markets oem
              where oem.organization_id = o.id
                and oem.market_name = :export_market
            )
            """
        )

    if export_ready:
        where_clauses.append(
            """
            (
              o.export_license_status in ('held', 'not_required')
              or exists (
                select 1
                from organization_export_markets oem
                where oem.organization_id = o.id
              )
            )
            """
        )

    if organic:
        where_clauses.append(
            """
            exists (
              select 1
              from organization_certifications oc
              join certifications c on c.id = oc.certification_id
              where oc.organization_id = o.id
                and c.certification_type = 'organic'
            )
            """
        )

    if verified:
        where_clauses.append("o.public_profile_status = 'verified'")

    return where_clauses, params


def _short_description(description: str | None) -> str | None:
    if description is None:
        return None
    if len(description) <= 120:
        return description
    return description[:117].rstrip() + "..."
