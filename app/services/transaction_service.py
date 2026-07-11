from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category
from app.schemas.transaction import (
    CreateTransactionRequest,
    UpdateTransactionRequest,
)


# ─── Ownership + integrity helpers ────────────────────────────────────────────
def _require_account(db: Session, user_id: int, account_id: int) -> Account:
    acc = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    return acc


def _validate_category(
    db: Session, user_id: int, category_id: Optional[int], txn_type: str
) -> None:
    """A category is optional, but if given it must belong to the user and match
    the transaction's income/expense type."""
    if category_id is None:
        return
    cat = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    if cat.type != txn_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{cat.name}' is not an {txn_type} category",
        )


# ─── Serialization ────────────────────────────────────────────────────────────
def _serialize(db: Session, txn: Transaction) -> dict:
    account = db.get(Account, txn.account_id) if txn.account_id else None
    category = db.get(Category, txn.category_id) if txn.category_id else None
    return {
        "id":            txn.id,
        "user_id":       txn.user_id,
        "type":          txn.type,
        "amount":        txn.amount,
        "account_id":    txn.account_id,
        "account_name":  account.name if account else None,
        "category_id":   txn.category_id,
        "category_name": category.name if category else None,
        "note":          txn.note,
        "date":          txn.date,
    }


# ─── CRUD ─────────────────────────────────────────────────────────────────────
def get_transactions(
    db: Session,
    user_id: int,
    start: Optional[date] = None,
    end: Optional[date] = None,
):
    q = (
        db.query(Transaction, Account.name, Category.name)
        .outerjoin(Account, Account.id == Transaction.account_id)
        .outerjoin(Category, Category.id == Transaction.category_id)
        .filter(Transaction.user_id == user_id)
    )
    if start is not None:
        q = q.filter(Transaction.date >= start)
    if end is not None:
        q = q.filter(Transaction.date <= end)
    rows = q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    return [
        {
            "id":            txn.id,
            "user_id":       txn.user_id,
            "type":          txn.type,
            "amount":        txn.amount,
            "account_id":    txn.account_id,
            "account_name":  acc_name,
            "category_id":   txn.category_id,
            "category_name": cat_name,
            "note":          txn.note,
            "date":          txn.date,
        }
        for txn, acc_name, cat_name in rows
    ]


def create_transaction(db: Session, user_id: int, payload: CreateTransactionRequest):
    _require_account(db, user_id, payload.account_id)
    _validate_category(db, user_id, payload.category_id, payload.type.value)

    txn = Transaction(
        user_id     = user_id,
        type        = payload.type.value,
        amount      = payload.amount,
        account_id  = payload.account_id,
        category_id = payload.category_id,
        note        = payload.note,
        date        = payload.date,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return _serialize(db, txn)


def update_transaction(
    db: Session, user_id: int, txn_id: int, payload: UpdateTransactionRequest
):
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == user_id,
    ).first()

    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    fields = payload.model_fields_set
    new_type = payload.type.value if payload.type is not None else txn.type

    if payload.account_id is not None:
        _require_account(db, user_id, payload.account_id)
        txn.account_id = payload.account_id
    if "category_id" in fields:
        _validate_category(db, user_id, payload.category_id, new_type)
        txn.category_id = payload.category_id
    if payload.type   is not None: txn.type   = new_type
    if payload.amount is not None: txn.amount = payload.amount
    if "note" in fields:           txn.note   = payload.note
    if payload.date   is not None: txn.date   = payload.date

    db.commit()
    db.refresh(txn)
    return _serialize(db, txn)


def delete_transaction(db: Session, user_id: int, txn_id: int):
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == user_id,
    ).first()

    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    db.delete(txn)
    db.commit()
    return True


# ─── Summary (dashboard aggregates) ───────────────────────────────────────────
def get_summary(db: Session, user_id: int, days: int = 30):
    """Aggregate the trailing `days` window into dashboard-ready numbers:
    totals, per-category expense breakdown (by category name), and a per-day
    income/expense series (zero-filled so the chart has a continuous x-axis)."""
    today = date.today()
    start = today - timedelta(days=days - 1)

    txns = get_transactions(db, user_id, start=start, end=today)

    total_income  = Decimal("0")
    total_expense = Decimal("0")
    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    per_day_income: dict[date, Decimal] = defaultdict(lambda: Decimal("0"))
    per_day_expense: dict[date, Decimal] = defaultdict(lambda: Decimal("0"))

    for t in txns:
        amount = Decimal(t["amount"])
        if t["type"] == "income":
            total_income += amount
            per_day_income[t["date"]] += amount
        else:
            total_expense += amount
            per_day_expense[t["date"]] += amount
            label = t["category_name"] or "Uncategorized"
            by_category[label] += amount

    breakdown = [
        {"category": cat, "total": amt}
        for cat, amt in sorted(by_category.items(), key=lambda kv: kv[1], reverse=True)
    ]

    daily = []
    for i in range(days):
        d = start + timedelta(days=i)
        daily.append({
            "date":    d,
            "income":  per_day_income[d],
            "expense": per_day_expense[d],
        })

    return {
        "total_income":  total_income,
        "total_expense": total_expense,
        "balance":       total_income - total_expense,
        "by_category":   breakdown,
        "daily":         daily,
    }
