from sqlalchemy.orm import Session
from app.models.goal import Goal
from app.schemas.goal import CreateGoalRequest, UpdateGoalRequest
from fastapi import HTTPException, status

def get_goals(db: Session, user_id: int):
    return (
        db.query(Goal)
        .filter(Goal.user_id == user_id)
        .order_by(Goal.deadline.asc())
        .all()
    )

def create_goal(db: Session, user_id: int, payload: CreateGoalRequest):
    goal = Goal(
        user_id     = user_id,
        title       = payload.title,
        description = payload.description,
        target      = payload.target,
        current     = payload.current,
        unit        = payload.unit,
        color       = payload.color,
        category    = payload.category,
        deadline    = payload.deadline,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

def update_goal(db: Session, user_id: int, goal_id: int, payload: UpdateGoalRequest):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == user_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )

    if payload.title       is not None: goal.title       = payload.title
    if payload.description is not None: goal.description = payload.description
    if payload.current     is not None: goal.current     = payload.current
    if payload.color       is not None: goal.color       = payload.color
    if payload.deadline    is not None: goal.deadline    = payload.deadline

    db.commit()
    db.refresh(goal)
    return goal

def delete_goal(db: Session, user_id: int, goal_id: int):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == user_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )

    db.delete(goal)
    db.commit()
    return True