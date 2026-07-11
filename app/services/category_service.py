from decimal import Decimal
from datetime import date
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CreateCategoryRequest, UpdateCategoryRequest


def _spent_this_month(db: Session, category_id: int) -> Decimal:
    """Expense logged against this category in the current calendar month —
    the denominator's numerator for budget progress bars."""
    today = date.today()
    first = today.replace(day=1)
    total = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.category_id == category_id,
            Transaction.type == "expense",
            Transaction.date >= first,
            Transaction.date <= today,
        )
        .scalar()
    )
    return Decimal(total or 0)


def serialize_category(db: Session, cat: Category) -> dict:
    spent = _spent_this_month(db, cat.id)
    budget = Decimal(cat.budget) if cat.budget is not None else None
    remaining = (budget - spent) if budget is not None else None
    return {
        "id":        cat.id,
        "name":      cat.name,
        "type":      cat.type,
        "budget":    budget,
        "spent":     spent,
        "remaining": remaining,
    }


def get_categories(
    db: Session, user_id: int, type: Optional[str] = None
) -> list[dict]:
    q = db.query(Category).filter(Category.user_id == user_id)
    if type is not None:
        q = q.filter(Category.type == type)
    cats = q.order_by(Category.type.asc(), Category.name.asc()).all()
    return [serialize_category(db, c) for c in cats]


def _get_owned(db: Session, user_id: int, category_id: int) -> Category:
    cat = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return cat


def create_category(
    db: Session, user_id: int, payload: CreateCategoryRequest
) -> dict:
    name = payload.name.strip()
    exists = (
        db.query(Category)
        .filter(
            Category.user_id == user_id,
            Category.type == payload.type.value,
            func.lower(Category.name) == name.lower(),
        )
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A {payload.type.value} category '{name}' already exists",
        )
    cat = Category(
        user_id=user_id,
        name=name,
        type=payload.type.value,
        budget=payload.budget,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return serialize_category(db, cat)


def update_category(
    db: Session, user_id: int, category_id: int, payload: UpdateCategoryRequest
) -> dict:
    cat = _get_owned(db, user_id, category_id)
    fields = payload.model_fields_set
    if "name" in fields and payload.name is not None:
        cat.name = payload.name.strip()
    # budget is explicitly clearable: sending null removes the budget.
    if "budget" in fields:
        cat.budget = payload.budget
    db.commit()
    db.refresh(cat)
    return serialize_category(db, cat)


def delete_category(db: Session, user_id: int, category_id: int) -> bool:
    cat = _get_owned(db, user_id, category_id)
    # Transactions referencing this category fall back to NULL (Uncategorized)
    # via the ON DELETE SET NULL foreign key — no history is lost.
    db.delete(cat)
    db.commit()
    return True
