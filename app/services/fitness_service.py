from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
from app.models.fitness_log import FitnessLog
from app.schemas.fitness import CreateFitnessLogRequest, UpdateFitnessLogRequest, FitnessStatsResponse
from fastapi import HTTPException, status

def get_logs(db: Session, user_id: int, from_date: date = None, to_date: date = None):
    query = db.query(FitnessLog).filter(FitnessLog.user_id == user_id)
    if from_date:
        query = query.filter(FitnessLog.log_date >= from_date)
    if to_date:
        query = query.filter(FitnessLog.log_date <= to_date)
    return query.order_by(FitnessLog.log_date.desc()).all()

def create_log(db: Session, user_id: int, payload: CreateFitnessLogRequest):
    log = FitnessLog(
        user_id   = user_id,
        log_date  = payload.log_date,
        weight_kg = payload.weight_kg,
        calories  = payload.calories,
        steps     = payload.steps,
        notes     = payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def update_log(db: Session, user_id: int, log_id: int, payload: UpdateFitnessLogRequest):
    log = db.query(FitnessLog).filter(
        FitnessLog.id == log_id,
        FitnessLog.user_id == user_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )

    if payload.weight_kg is not None: log.weight_kg = payload.weight_kg
    if payload.calories  is not None: log.calories  = payload.calories
    if payload.steps     is not None: log.steps     = payload.steps
    if payload.notes     is not None: log.notes     = payload.notes

    db.commit()
    db.refresh(log)
    return log

def delete_log(db: Session, user_id: int, log_id: int):
    log = db.query(FitnessLog).filter(
        FitnessLog.id == log_id,
        FitnessLog.user_id == user_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )

    db.delete(log)
    db.commit()
    return True

def get_stats(db: Session, user_id: int) -> FitnessStatsResponse:
    logs = db.query(FitnessLog).filter(
        FitnessLog.user_id == user_id
    ).order_by(FitnessLog.log_date.desc()).all()

    if not logs:
        return FitnessStatsResponse(
            current_weight   = None,
            average_calories = None,
            average_steps    = None,
            total_logs       = 0,
            weight_lost      = None,
        )

    weights  = [l.weight_kg for l in logs if l.weight_kg]
    calories = [l.calories  for l in logs if l.calories]
    steps    = [l.steps     for l in logs if l.steps]

    current_weight = weights[0]  if weights else None
    oldest_weight  = weights[-1] if weights else None
    weight_lost    = (oldest_weight - current_weight) if (current_weight and oldest_weight) else None

    return FitnessStatsResponse(
        current_weight   = current_weight,
        average_calories = sum(calories) / len(calories) if calories else None,
        average_steps    = sum(steps)    / len(steps)    if steps    else None,
        total_logs       = len(logs),
        weight_lost      = weight_lost,
    )