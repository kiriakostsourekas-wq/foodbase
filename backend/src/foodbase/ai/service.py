from __future__ import annotations

import json
from typing import Any, cast

from fastapi import HTTPException
from groq import Groq
from sqlalchemy.orm import Session

from foodbase.ai.models import (
    ProductProfileRequest,
    ProductProfileResponse,
    StructuredSupplierSelection,
    StructuredSupplierTeamResponse,
    SupplierTeamItem,
    SupplierTeamRequest,
    SupplierTeamResponse,
)
from foodbase.catalog.models import CategorySummary, OrganizationListItem
from foodbase.catalog.service import list_categories, list_organizations
from foodbase.config import get_settings
from foodbase.intake.importer import slugify


def generate_product_profile(
    session: Session,
    payload: ProductProfileRequest,
) -> ProductProfileResponse:
    settings = get_settings()
    categories = list_categories(session)
    category_map = {category.slug: category for category in categories}
    client = _get_groq_client()

    response_params: dict[str, Any] = {
        "model": settings.ai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Foodbase AI, a sourcing strategist for Greek food and ingredient "
                    "production. Convert the user's concept into a structured sourcing brief. "
                    "Choose category_slug from the provided Foodbase categories only. Keep the "
                    "output commercially plausible for an early supplier-discovery phase. "
                    "Use short, concrete phrases instead of marketing copy."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "product_prompt": payload.prompt,
                        "refinement_answers": payload.answers,
                        "available_categories": [
                            {"slug": category.slug, "label": category.name}
                            for category in categories
                        ],
                    },
                    ensure_ascii=True,
                ),
            },
        ],
        "response_format": _json_schema_response_format(
            ProductProfileResponse,
            schema_name="foodbase_product_profile",
        ),
        "temperature": 0.2,
        "max_completion_tokens": 1200,
    }
    try:
        response = client.chat.completions.create(**response_params)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider request failed while generating the product profile.",
        ) from exc
    parsed = _parse_structured_response(response.choices[0].message.content, ProductProfileResponse)

    normalized_category = _normalize_category(parsed.category_slug, categories, payload.prompt)
    category = category_map.get(normalized_category)
    if category is None and categories:
        category = categories[0]
        normalized_category = category.slug

    return parsed.model_copy(
        update={
            "category_slug": normalized_category,
            "category_label": category.name if category is not None else parsed.category_label,
        }
    )


def generate_supplier_team(
    session: Session,
    payload: SupplierTeamRequest,
) -> SupplierTeamResponse:
    settings = get_settings()
    category_slug = payload.product_profile.category_slug

    candidates = _load_team_candidates(
        session,
        category_slug=category_slug,
        payload=payload,
    )
    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No supplier candidates were found for the current product profile.",
        )

    selections: list[StructuredSupplierSelection]
    summary: str
    estimated_lead_time: str

    try:
        client = _get_groq_client()
        response_params: dict[str, Any] = {
            "model": settings.ai_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Foodbase AI. Build the best current supplier shortlist from the "
                        "provided Foodbase database candidates. Only use suppliers that appear in "
                        "the candidate list. Do not invent new companies. Because the current "
                        "pilot database is producer-heavy, roles may be sourcing roles such as "
                        "'Primary producer', 'Organic option', 'Export-ready backup', or "
                        "'Private-label capable producer'."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "product_profile": payload.product_profile.model_dump(),
                            "max_suppliers": payload.max_suppliers,
                            "candidate_suppliers": [
                                _candidate_prompt_record(candidate) for candidate in candidates
                            ],
                        },
                        ensure_ascii=True,
                    ),
                },
            ],
            "response_format": _json_schema_response_format(
                StructuredSupplierTeamResponse,
                schema_name="foodbase_supplier_team",
            ),
            "temperature": 0.2,
            "max_completion_tokens": 1500,
        }
        response = client.chat.completions.create(**response_params)
        structured = _parse_structured_response(
            response.choices[0].message.content,
            StructuredSupplierTeamResponse,
        )
        selections = _normalize_selections(
            structured.selections,
            candidates,
            payload.max_suppliers,
        )
        if not selections:
            selections = _fallback_selections(candidates, payload)
        summary = structured.summary
        estimated_lead_time = structured.estimated_lead_time
    except HTTPException:
        raise
    except Exception:
        selections = _fallback_selections(candidates, payload)
        summary = (
            "Foodbase selected the strongest currently available supplier matches from the "
            "olive-oil pilot dataset."
        )
        estimated_lead_time = _estimate_lead_time_from_candidates(candidates)

    suppliers = [
        _team_item_from_candidate(candidate_by_slug(candidates)[selection.slug], selection)
        for selection in selections
    ]
    average_fit = round(
        sum(supplier.fit_score for supplier in suppliers) / len(suppliers)
    )

    return SupplierTeamResponse(
        summary=summary,
        average_fit_score=average_fit,
        estimated_lead_time=estimated_lead_time,
        candidate_count=len(candidates),
        dataset_note=(
            "This phase-1 pilot uses the live Foodbase olive-oil dataset, so the current team "
            "is composed of real producer matches rather than a full packaging/logistics network."
        ),
        suppliers=suppliers,
    )


def _load_team_candidates(
    session: Session,
    *,
    category_slug: str,
    payload: SupplierTeamRequest,
) -> list[OrganizationListItem]:
    strict_candidates = list_organizations(
        session,
        category=category_slug or None,
        private_label=payload.product_profile.private_label_required or None,
        export_ready=payload.product_profile.export_ready_required or None,
        organic=payload.product_profile.organic_required or None,
        limit=20,
        offset=0,
    ).items
    if len(strict_candidates) >= min(payload.max_suppliers, 3):
        return strict_candidates

    relaxed_candidates = list_organizations(
        session,
        category=category_slug or None,
        limit=20,
        offset=0,
    ).items
    if relaxed_candidates:
        return relaxed_candidates

    return list_organizations(session, limit=20, offset=0).items


def _candidate_prompt_record(candidate: OrganizationListItem) -> dict[str, Any]:
    return {
        "slug": candidate.slug,
        "name": candidate.name,
        "city": candidate.city,
        "region": candidate.region,
        "category": candidate.category,
        "subcategory": candidate.subcategory,
        "short_description": candidate.short_description,
        "certifications": candidate.certifications,
        "moq": candidate.moq,
        "lead_time": candidate.lead_time,
        "capacity": candidate.capacity,
        "export_ready": candidate.export_ready,
        "private_label": candidate.private_label,
        "organic": candidate.organic,
        "verified": candidate.verified,
        "export_markets": candidate.export_markets,
    }


def _normalize_selections(
    selections: list[StructuredSupplierSelection],
    candidates: list[OrganizationListItem],
    max_suppliers: int,
) -> list[StructuredSupplierSelection]:
    candidates_by_slug = candidate_by_slug(candidates)
    normalized: list[StructuredSupplierSelection] = []
    seen_slugs: set[str] = set()

    for selection in selections:
        slug = selection.slug.strip()
        if slug not in candidates_by_slug or slug in seen_slugs:
            continue
        normalized.append(selection.model_copy(update={"slug": slug}))
        seen_slugs.add(slug)
        if len(normalized) >= max_suppliers:
            break

    return normalized


def _fallback_selections(
    candidates: list[OrganizationListItem],
    payload: SupplierTeamRequest,
) -> list[StructuredSupplierSelection]:
    scored_candidates = sorted(
        candidates,
        key=lambda candidate: (
            _heuristic_fit(candidate, payload),
            1 if candidate.verified else 0,
            candidate.name.lower(),
        ),
        reverse=True,
    )
    roles = [
        "Primary producer",
        "Verified backup producer",
        "Export-ready option",
        "Private-label option",
        "Organic option",
        "Additional candidate",
    ]
    selections: list[StructuredSupplierSelection] = []
    for index, candidate in enumerate(scored_candidates[: payload.max_suppliers]):
        selections.append(
            StructuredSupplierSelection(
                slug=candidate.slug,
                role=roles[min(index, len(roles) - 1)],
                reason=_heuristic_reason(candidate, payload),
                fit_score=_heuristic_fit(candidate, payload),
            )
        )
    return selections


def _heuristic_fit(candidate: OrganizationListItem, payload: SupplierTeamRequest) -> int:
    score = 55
    if candidate.verified:
        score += 10
    if candidate.export_ready:
        score += 10
    if candidate.private_label and payload.product_profile.private_label_required:
        score += 10
    if candidate.organic and payload.product_profile.organic_required:
        score += 10
    if payload.product_profile.export_ready_required and candidate.export_ready:
        score += 5
    if candidate.certifications:
        score += min(10, len(candidate.certifications) * 2)
    if candidate.export_markets:
        score += 5
    return min(score, 99)


def _heuristic_reason(candidate: OrganizationListItem, payload: SupplierTeamRequest) -> str:
    strengths: list[str] = []
    if candidate.verified:
        strengths.append("verified profile")
    if candidate.export_ready:
        strengths.append("export-ready")
    if candidate.private_label:
        strengths.append("private label capability")
    if candidate.organic:
        strengths.append("organic positioning")
    if candidate.certifications:
        strengths.append(f"certifications: {', '.join(candidate.certifications[:3])}")
    if not strengths:
        strengths.append("strong fit within the current pilot dataset")
    return (
        f"{candidate.name} matches the product brief through "
        f"{'; '.join(strengths)}."
    )


def _team_item_from_candidate(
    candidate: OrganizationListItem,
    selection: StructuredSupplierSelection,
) -> SupplierTeamItem:
    return SupplierTeamItem(
        id=candidate.id,
        slug=candidate.slug,
        name=candidate.name,
        city=candidate.city,
        region=candidate.region,
        role=selection.role,
        reason=selection.reason,
        fit_score=selection.fit_score,
        certifications=candidate.certifications,
        verified=candidate.verified,
        organic=candidate.organic,
        private_label=candidate.private_label,
        export_ready=candidate.export_ready,
        lead_time=candidate.lead_time,
        moq=candidate.moq,
        short_description=candidate.short_description,
        website_url=None,
    )


def _estimate_lead_time_from_candidates(candidates: list[OrganizationListItem]) -> str:
    lead_times = [candidate.lead_time for candidate in candidates if candidate.lead_time]
    return lead_times[0] if lead_times else "On request"


def candidate_by_slug(candidates: list[OrganizationListItem]) -> dict[str, OrganizationListItem]:
    return {candidate.slug: candidate for candidate in candidates}


def _parse_structured_response[
    T: ProductProfileResponse | StructuredSupplierTeamResponse
](
    raw_content: str | None,
    model_class: type[T],
) -> T:
    if not raw_content:
        raise HTTPException(status_code=502, detail="The AI provider returned an empty response.")
    try:
        return cast(T, model_class.model_validate_json(raw_content))
    except Exception as exc:  # pragma: no cover - defensive integration guard
        raise HTTPException(
            status_code=502,
            detail=f"The AI provider returned invalid structured data: {exc}",
        ) from exc


def _normalize_category(
    category_slug: str,
    categories: list[CategorySummary],
    prompt: str,
) -> str:
    available = {category.slug: category for category in categories}
    if category_slug in available:
        return category_slug

    candidate_slug = slugify(category_slug)
    if candidate_slug in available:
        return candidate_slug

    prompt_slug = slugify(prompt)
    for slug in available:
        if slug in prompt_slug:
            return slug

    return categories[0].slug if categories else candidate_slug


def _get_groq_client() -> Groq:
    settings = get_settings()
    api_key = settings.groq_api_key.get_secret_value().strip() if settings.groq_api_key else ""
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "FOODBASE_GROQ_API_KEY is not configured. Add it to backend/.env to enable "
                "AI features."
            ),
        )
    return Groq(api_key=api_key)


def _json_schema_response_format(
    model_class: type[ProductProfileResponse] | type[StructuredSupplierTeamResponse],
    *,
    schema_name: str,
) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": True,
            "schema": model_class.model_json_schema(),
        },
    }
