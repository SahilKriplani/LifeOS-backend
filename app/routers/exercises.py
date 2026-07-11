from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.workout import (
    CreateExerciseRequest,
    ExerciseListResponse,
    ExerciseSingleResponse,
    ExerciseResponse,
)
from app.services import workout_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=ExerciseListResponse)
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exercises = workout_service.get_exercises(db, current_user.id)
    return ExerciseListResponse(
        success=True,
        data=[ExerciseResponse.model_validate(e) for e in exercises],
    )


@router.post("", response_model=ExerciseSingleResponse)
def create_exercise(
    payload: CreateExerciseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exercise = workout_service.create_exercise(db, current_user.id, payload)
    return ExerciseSingleResponse(
        success=True,
        data=ExerciseResponse.model_validate(exercise),
        message="Exercise added",
    )


@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout_service.delete_exercise(db, current_user.id, exercise_id)
    return {"success": True, "message": "Exercise deleted"}
