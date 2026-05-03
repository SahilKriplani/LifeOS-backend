from sqlalchemy.orm import Session
from datetime import date
from app.models.dsa_log import DSALog
from app.schemas.dsa import CreateDSALogRequest
from app.schemas.dsa import DSAStatsResponse
from fastapi import HTTPException, status

def get_logs(db: Session, user_id: int, from_date: date = None, to_date: date = None):
    query = db.query(DSALog).filter(DSALog.user_id == user_id)
    if from_date:
        query = query.filter(DSALog.solved_at >= from_date)
    if to_date:
        query = query.filter(DSALog.solved_at <= to_date)
    return query.order_by(DSALog.solved_at.desc()).all()

def create_log(db: Session, user_id: int, payload: CreateDSALogRequest):
    log = DSALog(
        user_id      = user_id,
        problem_name = payload.problem_name,
        platform     = payload.platform,
        difficulty   = payload.difficulty,
        topic        = payload.topic,
        solved_at    = payload.solved_at,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def delete_log(db: Session, user_id: int, log_id: int):
    log = db.query(DSALog).filter(
        DSALog.id == log_id,
        DSALog.user_id == user_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )

    db.delete(log)
    db.commit()
    return True

def get_stats(db: Session, user_id: int) -> DSAStatsResponse:
    logs = db.query(DSALog).filter(DSALog.user_id == user_id).all()

    by_topic: dict[str, int] = {}
    easy = medium = hard = 0

    for log in logs:
        if log.difficulty == "easy":   easy   += 1
        if log.difficulty == "medium": medium += 1
        if log.difficulty == "hard":   hard   += 1
        if log.topic:
            by_topic[log.topic] = by_topic.get(log.topic, 0) + 1

    return DSAStatsResponse(
        total    = len(logs),
        easy     = easy,
        medium   = medium,
        hard     = hard,
        by_topic = by_topic,
    )