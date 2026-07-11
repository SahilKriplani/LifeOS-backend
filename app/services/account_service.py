from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.account import CreateAccountRequest, UpdateAccountRequest


def _sum(db: Session, account_id: int, txn_type: str) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.account_id == account_id, Transaction.type == txn_type)
        .scalar()
    )
    return Decimal(total or 0)


def serialize_account(db: Session, acc: Account) -> dict:
    """Attach the derived live balance = opening + income − expense."""
    income = _sum(db, acc.id, "income")
    expense = _sum(db, acc.id, "expense")
    return {
        "id":              acc.id,
        "name":            acc.name,
        "opening_balance": Decimal(acc.opening_balance),
        "is_default":      acc.is_default,
        "balance":         Decimal(acc.opening_balance) + income - expense,
    }


def get_accounts(db: Session, user_id: int) -> list[dict]:
    accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        # Default (Cash) first, then oldest → newest.
        .order_by(Account.is_default.desc(), Account.id.asc())
        .all()
    )
    return [serialize_account(db, a) for a in accounts]


def _get_owned(db: Session, user_id: int, account_id: int) -> Account:
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


def create_account(db: Session, user_id: int, payload: CreateAccountRequest) -> dict:
    acc = Account(
        user_id=user_id,
        name=payload.name.strip(),
        opening_balance=payload.opening_balance,
        is_default=False,
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return serialize_account(db, acc)


def update_account(
    db: Session, user_id: int, account_id: int, payload: UpdateAccountRequest
) -> dict:
    acc = _get_owned(db, user_id, account_id)
    fields = payload.model_fields_set
    if "name" in fields and payload.name is not None:
        acc.name = payload.name.strip()
    if "opening_balance" in fields and payload.opening_balance is not None:
        acc.opening_balance = payload.opening_balance
    db.commit()
    db.refresh(acc)
    return serialize_account(db, acc)


def delete_account(db: Session, user_id: int, account_id: int) -> bool:
    acc = _get_owned(db, user_id, account_id)
    if acc.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The default Cash account can't be deleted",
        )

    # Reassign this account's transactions to the default account rather than
    # destroying history, then remove the account.
    default = (
        db.query(Account)
        .filter(Account.user_id == user_id, Account.is_default == True)  # noqa: E712
        .first()
    )
    if default:
        db.query(Transaction).filter(
            Transaction.account_id == acc.id
        ).update({Transaction.account_id: default.id}, synchronize_session=False)

    db.delete(acc)
    db.commit()
    return True
