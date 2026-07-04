from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class CreateAccountRequest(BaseModel):
    name:            str     = Field(..., min_length=1, max_length=50)
    opening_balance: Decimal = Field(default=Decimal("0"), ge=0)


class UpdateAccountRequest(BaseModel):
    name:            Optional[str]     = Field(default=None, min_length=1, max_length=50)
    opening_balance: Optional[Decimal] = Field(default=None, ge=0)


class AccountResponse(BaseModel):
    id:              int
    name:            str
    opening_balance: Decimal
    is_default:      bool
    # Derived live balance = opening_balance + income − expense on this account.
    balance:         Decimal


class AccountListResponse(BaseModel):
    success: bool
    data:    list[AccountResponse]
    message: str = "OK"


class AccountSingleResponse(BaseModel):
    success: bool
    data:    AccountResponse
    message: str = "OK"
