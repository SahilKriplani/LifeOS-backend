from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.dsa import (
    CreateDSALogRequest,
    DSALogListResponse,
    DSALogSingleResponse,
    DSALogResponse,
    DSAStatsWrapped,
)
from app.services import dsa_service

router = APIRouter(prefix="/dsa", tags=["dsa"])

@router.get("/stats", response_model=DSAStatsWrapped)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = dsa_service.get_stats(db, current_user.id)
    return DSAStatsWrapped(success=True, data=stats)

@router.get("/logs", response_model=DSALogListResponse)
def get_logs(
    from_date: Optional[date] = Query(None),
    to_date:   Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = dsa_service.get_logs(db, current_user.id, from_date, to_date)
    return DSALogListResponse(
        success=True,
        data=[DSALogResponse.model_validate(l) for l in logs],
    )

@router.post("/logs", response_model=DSALogSingleResponse)
def create_log(
    payload: CreateDSALogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = dsa_service.create_log(db, current_user.id, payload)
    return DSALogSingleResponse(
        success=True,
        data=DSALogResponse.model_validate(log),
        message="Problem logged",
    )

@router.delete("/logs/{log_id}")
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dsa_service.delete_log(db, current_user.id, log_id)
    return {"success": True, "message": "Log deleted"}