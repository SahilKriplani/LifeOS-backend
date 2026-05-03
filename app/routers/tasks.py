from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.task import (
    CreateTaskRequest,
    UpdateTaskRequest,
    TaskListResponse,
    TaskSingleResponse,
    TaskResponse,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("", response_model=TaskListResponse)
def get_tasks(
    date: date = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = task_service.get_tasks_by_date(db, current_user.id, date)
    return TaskListResponse(
        success=True,
        data=[TaskResponse.model_validate(t) for t in tasks],
    )

@router.post("", response_model=TaskSingleResponse)
def create_task(
    payload: CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_service.create_task(db, current_user.id, payload)
    return TaskSingleResponse(
        success=True,
        data=TaskResponse.model_validate(task),
        message="Task created",
    )

@router.patch("/{task_id}", response_model=TaskSingleResponse)
def update_task(
    task_id: int,
    payload: UpdateTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_service.update_task(db, current_user.id, task_id, payload)
    return TaskSingleResponse(
        success=True,
        data=TaskResponse.model_validate(task),
        message="Task updated",
    )

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_service.delete_task(db, current_user.id, task_id)
    return {"success": True, "message": "Task deleted"}