from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum
from decimal import Decimal

class CategoryEnum(str, Enum):
    dsa      = "dsa"
    fitness  = "fitness"
    career   = "career"
    personal = "personal"

class CreateGoalRequest(BaseModel):
    title:       str
    description: Optional[str] = None
    target:      Decimal
    current:     Decimal       = Decimal("0")
    unit:        str
    color:       str           = "#14B8A6"
    category:    CategoryEnum  = CategoryEnum.personal
    deadline:    date

class UpdateGoalRequest(BaseModel):
    title:       Optional[str]          = None
    description: Optional[str]          = None
    current:     Optional[Decimal]      = None
    color:       Optional[str]          = None
    deadline:    Optional[date]         = None

class GoalResponse(BaseModel):
    id:          int
    user_id:     int
    title:       str
    description: Optional[str]
    target:      Decimal
    current:     Decimal
    unit:        str
    color:       str
    category:    CategoryEnum
    deadline:    date

    model_config = {"from_attributes": True}

class GoalListResponse(BaseModel):
    success: bool
    data:    list[GoalResponse]
    message: str = "OK"

class GoalSingleResponse(BaseModel):
    success: bool
    data:    GoalResponse
    message: str = "OK"