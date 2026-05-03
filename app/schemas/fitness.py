from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class CreateFitnessLogRequest(BaseModel):
    log_date:  date
    weight_kg: Optional[Decimal] = None
    calories:  Optional[int]     = None
    steps:     Optional[int]     = None
    notes:     Optional[str]     = None

class UpdateFitnessLogRequest(BaseModel):
    weight_kg: Optional[Decimal] = None
    calories:  Optional[int]     = None
    steps:     Optional[int]     = None
    notes:     Optional[str]     = None

class FitnessLogResponse(BaseModel):
    id:        int
    user_id:   int
    log_date:  date
    weight_kg: Optional[Decimal]
    calories:  Optional[int]
    steps:     Optional[int]
    notes:     Optional[str]

    model_config = {"from_attributes": True}

class FitnessStatsResponse(BaseModel):
    current_weight:   Optional[Decimal]
    average_calories: Optional[float]
    average_steps:    Optional[float]
    total_logs:       int
    weight_lost:      Optional[Decimal]

class FitnessLogListResponse(BaseModel):
    success: bool
    data:    list[FitnessLogResponse]
    message: str = "OK"

class FitnessLogSingleResponse(BaseModel):
    success: bool
    data:    FitnessLogResponse
    message: str = "OK"

class FitnessStatsWrapped(BaseModel):
    success: bool
    data:    FitnessStatsResponse
    message: str = "OK"