from sqlalchemy.orm import Session
from datetime import date
from app.models.task import Task
from app.schemas.task import CreateTaskRequest, UpdateTaskRequest
from fastapi import HTTPException, status

def get_tasks_by_date(db: Session, user_id: int, scheduled_date: date):
    return (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.scheduled_date == scheduled_date)
        .order_by(Task.created_at.asc())
        .all()
    )

def create_task(db: Session, user_id: int, payload: CreateTaskRequest):
    task = Task(
        user_id        = user_id,
        title          = payload.title,
        scheduled_date = payload.scheduled_date,
        priority       = payload.priority,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task(db: Session, user_id: int, task_id: int, payload: UpdateTaskRequest):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if payload.title    is not None: task.title    = payload.title
    if payload.is_done  is not None: task.is_done  = payload.is_done
    if payload.priority is not None: task.priority = payload.priority

    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, user_id: int, task_id: int):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()
    return True