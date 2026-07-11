from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from enum import Enum
from decimal import Decimal

class TxnTypeEnum(str, Enum):
    income  = "income"
    expense = "expense"

class CreateTransactionRequest(BaseModel):
    type:        TxnTypeEnum
    amount:      Decimal = Field(..., gt=0)
    account_id:  int
    category_id: Optional[int] = None
    note:        Optional[str] = None
    date:        date

class UpdateTransactionRequest(BaseModel):
    type:        Optional[TxnTypeEnum] = None
    amount:      Optional[Decimal]     = Field(default=None, gt=0)
    account_id:  Optional[int]         = None
    category_id: Optional[int]         = None
    note:        Optional[str]         = None
    date:        Optional[date]        = None

class TransactionResponse(BaseModel):
    id:            int
    user_id:       int
    type:          TxnTypeEnum
    amount:        Decimal
    account_id:    int
    account_name:  Optional[str]
    category_id:   Optional[int]
    category_name: Optional[str]
    note:          Optional[str]
    date:          date

class TransactionListResponse(BaseModel):
    success: bool
    data:    list[TransactionResponse]
    message: str = "OK"

class TransactionSingleResponse(BaseModel):
    success: bool
    data:    TransactionResponse
    message: str = "OK"

# ─── Summary (dashboard aggregates) ───────────────────────────────────────────
class CategoryBreakdown(BaseModel):
    category: str
    total:    Decimal

class DailyPoint(BaseModel):
    date:    date
    income:  Decimal
    expense: Decimal

class FinanceSummary(BaseModel):
    total_income:  Decimal
    total_expense: Decimal
    balance:       Decimal
    by_category:   list[CategoryBreakdown]
    daily:         list[DailyPoint]

class FinanceSummaryResponse(BaseModel):
    success: bool
    data:    FinanceSummary
    message: str = "OK"
