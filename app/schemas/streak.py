from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class StreakResponse(BaseModel):
    user_id:          int
    current_streak:   int
    best_streak:      int
    last_active_date: Optional[date]
    # Recent active days (last ~35) so the dashboard can draw real week/month
    # grids instead of mock data.
    active_dates:     List[date] = []

    model_config = {"from_attributes": True}

class StreakWrapped(BaseModel):
    success: bool
    data:    StreakResponse
    message: str = "OK"

class CheckinResponse(BaseModel):
    success:        bool
    current_streak: int
    message:        str