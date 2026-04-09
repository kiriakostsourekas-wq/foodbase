from foodbase.api.routes import organizations as organizations_route
from foodbase.api.routes import reference_data as reference_data_route
from foodbase.catalog.models import (
    CategorySummary,
    GeographicalIndicationSummary,
    OrganizationDetail,
    OrganizationListItem,
    OrganizationListResponse,
    Pagination,
    SearchFacetsResponse,
)


def test_get_organizations_endpoint_returns_paginated_payload(client, monkeypatch) -> None:
    response_payload = OrganizationListResponse(
        items=[
            OrganizationListItem(
                id=1,
                slug="olive-test",
                name="Olive Test",
                city="Kalamata",
                region="Peloponnese",
                lat=37.0389,
                lng=22.1142,
                category="olive-oil",
                category_label="Olive Oil",
                subcategory="Extra Virgin Olive Oil",
                description="Pilot supplier",
                short_description="Pilot supplier",
                certifications=["ISO 22000"],
                moq="On request",
                lead_time="On request",
                capacity="Public capacity not disclosed",
                export_ready=True,
                private_label=False,
                organic=False,
                verified=True,
                export_markets=["Europe"],
            )
        ],
        pagination=Pagination(total=1, limit=20, offset=0),
    )
    monkeypatch.setattr(
        organizations_route,
        "list_organizations",
        lambda *args, **kwargs: response_payload,
    )

    response = client.get("/api/organizations?category=olive-oil")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["slug"] == "olive-test"
    assert payload["items"][0]["category"] == "olive-oil"


def test_get_organization_detail_endpoint_returns_profile(client, monkeypatch) -> None:
    detail_payload = OrganizationDetail(
        id=1,
        slug="olive-test",
        name="Olive Test",
        legal_name="Olive Test S.A.",
        organization_type="producer",
        summary="Pilot supplier",
        city="Kalamata",
        region="Peloponnese",
        lat=37.0389,
        lng=22.1142,
        website_url="https://example.com",
        export_ready=True,
        verified=True,
        organic=False,
        private_label=False,
    )
    monkeypatch.setattr(
        organizations_route,
        "get_organization_detail",
        lambda *args, **kwargs: detail_payload,
    )

    response = client.get("/api/organizations/olive-test")

    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "olive-test"
    assert payload["name"] == "Olive Test"


def test_reference_data_endpoints_return_expected_shapes(client, monkeypatch) -> None:
    monkeypatch.setattr(
        reference_data_route,
        "list_categories",
        lambda *args, **kwargs: [
            CategorySummary(
                slug="olive-oil",
                name="Olive Oil",
                parent_slug=None,
                category_type="finished_product",
                count=20,
            )
        ],
    )
    monkeypatch.setattr(
        reference_data_route,
        "list_geographical_indications",
        lambda *args, **kwargs: [
            GeographicalIndicationSummary(
                id=1,
                name="Kalamata",
                designation_type="PDO",
                product_category="Olive Oil",
                source_registry="ministry",
                registry_url="https://example.com",
                specification_url=None,
                organization_count=0,
            )
        ],
    )
    monkeypatch.setattr(
        reference_data_route,
        "get_search_facets",
        lambda *args, **kwargs: SearchFacetsResponse(
            categories=[],
            regions=[],
            certifications=[],
            designations=[],
        ),
    )

    categories_response = client.get("/api/categories")
    gi_response = client.get("/api/geographical-indications")
    facets_response = client.get("/api/search-facets")

    assert categories_response.status_code == 200
    assert categories_response.json()[0]["slug"] == "olive-oil"
    assert gi_response.status_code == 200
    assert gi_response.json()[0]["designation_type"] == "PDO"
    assert facets_response.status_code == 200
    assert facets_response.json() == {
        "categories": [],
        "regions": [],
        "certifications": [],
        "designations": [],
    }
