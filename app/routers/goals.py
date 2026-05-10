from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.goal import (
    CreateGoalRequest,
    UpdateGoalRequest,
    GoalListResponse,
    GoalSingleResponse,
    GoalResponse,
)
from app.services import goal_service

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("", response_model=GoalListResponse)
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goals = goal_service.get_goals(db, current_user.id)
    return GoalListResponse(
        success=True,
        data=[GoalResponse.model_validate(g) for g in goals],
    )

@router.post("", response_model=GoalSingleResponse)
def create_goal(
    payload: CreateGoalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = goal_service.create_goal(db, current_user.id, payload)
    return GoalSingleResponse(
        success=True,
        data=GoalResponse.model_validate(goal),
        message="Goal created",
    )

@router.patch("/{goal_id}", response_model=GoalSingleResponse)
def update_goal(
    goal_id: int,
    payload: UpdateGoalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = goal_service.update_goal(db, current_user.id, goal_id, payload)
    return GoalSingleResponse(
        success=True,
        data=GoalResponse.model_validate(goal),
        message="Goal updated",
    )

@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal_service.delete_goal(db, current_user.id, goal_id)
    return {"success": True, "message": "Goal deleted"}