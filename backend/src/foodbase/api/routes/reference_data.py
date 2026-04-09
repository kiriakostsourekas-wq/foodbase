from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from foodbase.catalog.models import (
    CategorySummary,
    GeographicalIndicationSummary,
    SearchFacetsResponse,
)
from foodbase.catalog.service import (
    get_search_facets,
    list_categories,
    list_geographical_indications,
)
from foodbase.db.session import get_db_session

router = APIRouter(tags=["reference-data"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/categories", response_model=list[CategorySummary])
def get_categories(session: DbSession) -> list[CategorySummary]:
    return list_categories(session)


@router.get("/geographical-indications", response_model=list[GeographicalIndicationSummary])
def get_geographical_indications(
    session: DbSession,
) -> list[GeographicalIndicationSummary]:
    return list_geographical_indications(session)


@router.get("/search-facets", response_model=SearchFacetsResponse)
def get_facets(session: DbSession) -> SearchFacetsResponse:
    return get_search_facets(session)
