from foodbase.ai.models import (
    ProductProfileResponse,
    SupplierTeamItem,
    SupplierTeamResponse,
)
from foodbase.api.routes import ai as ai_route


def test_product_profile_endpoint_returns_structured_payload(client, monkeypatch) -> None:
    monkeypatch.setattr(
        ai_route,
        "generate_product_profile",
        lambda *args, **kwargs: ProductProfileResponse(
            name="Aegean Gold",
            summary="Premium Greek olive oil concept",
            description="A premium extra virgin olive oil positioned for export.",
            category_slug="olive-oil",
            category_label="Olive Oil",
            subcategory="Extra Virgin Olive Oil",
            positioning=["Premium", "Export-first"],
            target_audience=["Premium retail buyers"],
            channels=["Export distributors"],
            packaging="500ml dark glass bottle",
            ingredients=["Extra virgin olive oil"],
            certifications=["Organic EU", "ISO 22000"],
            moq="500 units",
            lead_time="3-5 weeks",
            price_tier="Premium",
            sales_estimate="EUR 180k-320k ARR",
            readiness_score=89,
            confidence="high",
            rationale="Strong Greek origin story and supplier base.",
            organic_required=True,
            private_label_required=False,
            export_ready_required=True,
            preferred_regions=["Peloponnese"],
        ),
    )

    response = client.post(
        "/api/ai/product-profile",
        json={"prompt": "Premium olive oil for export", "answers": {}},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["category_slug"] == "olive-oil"
    assert payload["readiness_score"] == 89


def test_supplier_team_endpoint_returns_database_backed_team(client, monkeypatch) -> None:
    monkeypatch.setattr(
        ai_route,
        "generate_supplier_team",
        lambda *args, **kwargs: SupplierTeamResponse(
            summary="Strong producer shortlist for the olive-oil pilot.",
            average_fit_score=92,
            estimated_lead_time="3-5 weeks",
            candidate_count=12,
            dataset_note="Pilot dataset note",
            suppliers=[
                SupplierTeamItem(
                    id=1,
                    slug="olive-test",
                    name="Olive Test",
                    city="Kalamata",
                    region="Peloponnese",
                    role="Primary producer",
                    reason="Strong verified export-ready fit.",
                    fit_score=94,
                    certifications=["ISO 22000"],
                    verified=True,
                    organic=False,
                    private_label=True,
                    export_ready=True,
                    lead_time="3-5 weeks",
                    moq="500 units",
                    short_description="Pilot supplier",
                    website_url="https://example.com",
                )
            ],
        ),
    )

    response = client.post(
        "/api/ai/supplier-team",
        json={
            "product_profile": {
                "name": "Aegean Gold",
                "summary": "Premium Greek olive oil concept",
                "description": "A premium extra virgin olive oil positioned for export.",
                "category_slug": "olive-oil",
                "category_label": "Olive Oil",
                "subcategory": "Extra Virgin Olive Oil",
                "positioning": ["Premium", "Export-first"],
                "target_audience": ["Premium retail buyers"],
                "channels": ["Export distributors"],
                "packaging": "500ml dark glass bottle",
                "ingredients": ["Extra virgin olive oil"],
                "certifications": ["Organic EU", "ISO 22000"],
                "moq": "500 units",
                "lead_time": "3-5 weeks",
                "price_tier": "Premium",
                "sales_estimate": "EUR 180k-320k ARR",
                "readiness_score": 89,
                "confidence": "high",
                "rationale": "Strong Greek origin story and supplier base.",
                "organic_required": True,
                "private_label_required": True,
                "export_ready_required": True,
                "preferred_regions": ["Peloponnese"]
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["average_fit_score"] == 92
    assert payload["suppliers"][0]["slug"] == "olive-test"
