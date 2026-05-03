from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.fitness import (
    CreateFitnessLogRequest,
    UpdateFitnessLogRequest,
    FitnessLogListResponse,
    FitnessLogSingleResponse,
    FitnessLogResponse,
    FitnessStatsWrapped,
)
from app.services import fitness_service

router = APIRouter(prefix="/fitness", tags=["fitness"])

@router.get("/stats", response_model=FitnessStatsWrapped)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = fitness_service.get_stats(db, current_user.id)
    return FitnessStatsWrapped(success=True, data=stats)

@router.get("/logs", response_model=FitnessLogListResponse)
def get_logs(
    from_date: Optional[date] = Query(None),
    to_date:   Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = fitness_service.get_logs(db, current_user.id, from_date, to_date)
    return FitnessLogListResponse(
        success=True,
        data=[FitnessLogResponse.model_validate(l) for l in logs],
    )

@router.post("/logs", response_model=FitnessLogSingleResponse)
def create_log(
    payload: CreateFitnessLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = fitness_service.create_log(db, current_user.id, payload)
    return FitnessLogSingleResponse(
        success=True,
        data=FitnessLogResponse.model_validate(log),
        message="Fitness log saved",
    )

@router.patch("/logs/{log_id}", response_model=FitnessLogSingleResponse)
def update_log(
    log_id: int,
    payload: UpdateFitnessLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = fitness_service.update_log(db, current_user.id, log_id, payload)
    return FitnessLogSingleResponse(
        success=True,
        data=FitnessLogResponse.model_validate(log),
        message="Log updated",
    )

@router.delete("/logs/{log_id}")
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fitness_service.delete_log(db, current_user.id, log_id)
    return {"success": True, "message": "Log deleted"}