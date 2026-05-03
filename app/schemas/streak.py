from pydantic import BaseModel
from datetime import date
from typing import Optional

class StreakResponse(BaseModel):
    user_id:          int
    current_streak:   int
    best_streak:      int
    last_active_date: Optional[date]

    model_config = {"from_attributes": True}

class StreakWrapped(BaseModel):
    success: bool
    data:    StreakResponse
    message: str = "OK"

class CheckinResponse(BaseModel):
    success:        bool
    current_streak: int
    message:        str