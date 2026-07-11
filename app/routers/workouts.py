from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.workout import (
    CreateWorkoutRequest,
    WorkoutListResponse,
    WorkoutSingleResponse,
)
from app.services import workout_service

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("", response_model=WorkoutListResponse)
def get_workouts(
    from_date: Optional[date] = Query(None),
    to_date:   Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = workout_service.get_workouts(db, current_user.id, from_date, to_date)
    return WorkoutListResponse(success=True, data=sessions)


@router.post("", response_model=WorkoutSingleResponse)
def create_workout(
    payload: CreateWorkoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = workout_service.create_workout(db, current_user.id, payload)
    return WorkoutSingleResponse(success=True, data=session, message="Workout saved")


@router.delete("/{log_id}")
def delete_workout(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout_service.delete_workout(db, current_user.id, log_id)
    return {"success": True, "message": "Workout deleted"}
