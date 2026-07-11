from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.streak import StreakWrapped, StreakResponse, CheckinResponse
from app.services import streak_service

router = APIRouter(prefix="/streaks", tags=["streaks"])

# How far back the calendar grids reach (5 weeks covers week + month views).
ACTIVITY_WINDOW_DAYS = 35

@router.get("/me", response_model=StreakWrapped)
def get_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    streak = streak_service.get_streak(db, current_user.id)
    # Self-heal calendars for streaks created before per-day tracking existed.
    streak_service.backfill_from_streak(db, streak)
    since = date.today() - timedelta(days=ACTIVITY_WINDOW_DAYS)
    active_dates = streak_service.get_active_dates(db, current_user.id, since)
    return StreakWrapped(
        success=True,
        data=StreakResponse(
            user_id=streak.user_id,
            current_streak=streak.current_streak,
            best_streak=streak.best_streak,
            last_active_date=streak.last_active_date,
            active_dates=active_dates,
        ),
    )

@router.post("/checkin", response_model=CheckinResponse)
def checkin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    streak = streak_service.checkin(db, current_user.id)
    return CheckinResponse(
        success=True,
        current_streak=streak.current_streak,
        message=f"Day {streak.current_streak} streak! Keep going 🔥",
    )