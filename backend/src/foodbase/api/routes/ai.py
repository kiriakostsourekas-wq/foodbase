from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from foodbase.ai.models import (
    ProductProfileRequest,
    ProductProfileResponse,
    SupplierTeamRequest,
    SupplierTeamResponse,
)
from foodbase.ai.service import generate_product_profile, generate_supplier_team
from foodbase.db.session import get_db_session

router = APIRouter(prefix="/ai", tags=["ai"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/product-profile", response_model=ProductProfileResponse)
def post_product_profile(
    payload: ProductProfileRequest,
    session: DbSession,
) -> ProductProfileResponse:
    return generate_product_profile(session, payload)


@router.post("/supplier-team", response_model=SupplierTeamResponse)
def post_supplier_team(
    payload: SupplierTeamRequest,
    session: DbSession,
) -> SupplierTeamResponse:
    return generate_supplier_team(session, payload)
