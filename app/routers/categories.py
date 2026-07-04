from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.category import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
    CategoryListResponse,
    CategorySingleResponse,
    CategoryResponse,
    CatTypeEnum,
)
from app.services import category_service
from app.services.finance_defaults import ensure_finance_defaults

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryListResponse)
def list_categories(
    type: Optional[CatTypeEnum] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_finance_defaults(db, current_user.id)
    cats = category_service.get_categories(
        db, current_user.id, type.value if type else None
    )
    return CategoryListResponse(
        success=True,
        data=[CategoryResponse.model_validate(c) for c in cats],
    )


@router.post("", response_model=CategorySingleResponse)
def create_category(
    payload: CreateCategoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = category_service.create_category(db, current_user.id, payload)
    return CategorySingleResponse(
        success=True,
        data=CategoryResponse.model_validate(cat),
        message="Category created",
    )


@router.patch("/{category_id}", response_model=CategorySingleResponse)
def update_category(
    category_id: int,
    payload: UpdateCategoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = category_service.update_category(db, current_user.id, category_id, payload)
    return CategorySingleResponse(
        success=True,
        data=CategoryResponse.model_validate(cat),
        message="Category updated",
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category_service.delete_category(db, current_user.id, category_id)
    return {"success": True, "message": "Category deleted"}
