from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from decimal import Decimal


class CatTypeEnum(str, Enum):
    income  = "income"
    expense = "expense"


class CreateCategoryRequest(BaseModel):
    name:   str          = Field(..., min_length=1, max_length=50)
    type:   CatTypeEnum
    budget: Optional[Decimal] = Field(default=None, gt=0)


class UpdateCategoryRequest(BaseModel):
    name:   Optional[str]     = Field(default=None, min_length=1, max_length=50)
    # budget is nullable-clearable: send null to remove the budget. We can't tell
    # "omitted" from "explicit null" here, so the service treats null as "clear".
    budget: Optional[Decimal] = Field(default=None, ge=0)


class CategoryResponse(BaseModel):
    id:        int
    name:      str
    type:      CatTypeEnum
    budget:    Optional[Decimal]
    # Spend against this category in the current calendar month (expense only).
    spent:     Decimal
    remaining: Optional[Decimal]  # budget − spent, or None when no budget set


class CategoryListResponse(BaseModel):
    success: bool
    data:    list[CategoryResponse]
    message: str = "OK"


class CategorySingleResponse(BaseModel):
    success: bool
    data:    CategoryResponse
    message: str = "OK"
