from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.transaction import (
    CreateTransactionRequest,
    UpdateTransactionRequest,
    TransactionListResponse,
    TransactionSingleResponse,
    TransactionResponse,
    FinanceSummaryResponse,
    FinanceSummary,
)
from app.services import transaction_service
from app.services.finance_defaults import ensure_finance_defaults

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=TransactionListResponse)
def get_transactions(
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_finance_defaults(db, current_user.id)
    txns = transaction_service.get_transactions(db, current_user.id, start, end)
    return TransactionListResponse(
        success=True,
        data=[TransactionResponse.model_validate(t) for t in txns],
    )

@router.get("/summary", response_model=FinanceSummaryResponse)
def get_summary(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_finance_defaults(db, current_user.id)
    summary = transaction_service.get_summary(db, current_user.id, days)
    return FinanceSummaryResponse(
        success=True,
        data=FinanceSummary.model_validate(summary),
    )

@router.post("", response_model=TransactionSingleResponse)
def create_transaction(
    payload: CreateTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txn = transaction_service.create_transaction(db, current_user.id, payload)
    return TransactionSingleResponse(
        success=True,
        data=TransactionResponse.model_validate(txn),
        message="Transaction created",
    )

@router.patch("/{txn_id}", response_model=TransactionSingleResponse)
def update_transaction(
    txn_id: int,
    payload: UpdateTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txn = transaction_service.update_transaction(db, current_user.id, txn_id, payload)
    return TransactionSingleResponse(
        success=True,
        data=TransactionResponse.model_validate(txn),
        message="Transaction updated",
    )

@router.delete("/{txn_id}")
def delete_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction_service.delete_transaction(db, current_user.id, txn_id)
    return {"success": True, "message": "Transaction deleted"}
