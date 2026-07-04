from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.account import (
    CreateAccountRequest,
    UpdateAccountRequest,
    AccountListResponse,
    AccountSingleResponse,
    AccountResponse,
)
from app.services import account_service
from app.services.finance_defaults import ensure_finance_defaults

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=AccountListResponse)
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_finance_defaults(db, current_user.id)
    accounts = account_service.get_accounts(db, current_user.id)
    return AccountListResponse(
        success=True,
        data=[AccountResponse.model_validate(a) for a in accounts],
    )


@router.post("", response_model=AccountSingleResponse)
def create_account(
    payload: CreateAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acc = account_service.create_account(db, current_user.id, payload)
    return AccountSingleResponse(
        success=True,
        data=AccountResponse.model_validate(acc),
        message="Account created",
    )


@router.patch("/{account_id}", response_model=AccountSingleResponse)
def update_account(
    account_id: int,
    payload: UpdateAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acc = account_service.update_account(db, current_user.id, account_id, payload)
    return AccountSingleResponse(
        success=True,
        data=AccountResponse.model_validate(acc),
        message="Account updated",
    )


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account_service.delete_account(db, current_user.id, account_id)
    return {"success": True, "message": "Account deleted"}
