from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from foodbase.catalog.models import OrganizationDetail, OrganizationListResponse
from foodbase.catalog.service import get_organization_detail, list_organizations
from foodbase.db.session import get_db_session

router = APIRouter(prefix="/organizations", tags=["organizations"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=OrganizationListResponse)
def get_organizations(
    session: DbSession,
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    subcategory: str | None = Query(default=None),
    region: str | None = Query(default=None),
    certification: str | None = Query(default=None),
    designation: str | None = Query(default=None),
    private_label: bool | None = Query(default=None),
    export_market: str | None = Query(default=None),
    export_ready: bool | None = Query(default=None),
    organic: bool | None = Query(default=None),
    verified: bool | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> OrganizationListResponse:
    return list_organizations(
        session,
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
        limit=limit,
        offset=offset,
    )


@router.get("/{slug}", response_model=OrganizationDetail)
def get_organization(
    slug: str,
    session: DbSession,
) -> OrganizationDetail:
    return get_organization_detail(session, slug)
