from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.streak import StreakWrapped, StreakResponse, CheckinResponse
from app.services import streak_service

router = APIRouter(prefix="/streaks", tags=["streaks"])

@router.get("/me", response_model=StreakWrapped)
def get_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    streak = streak_service.get_streak(db, current_user.id)
    return StreakWrapped(
        success=True,
        data=StreakResponse.model_validate(streak),
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