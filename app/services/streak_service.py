from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.streak import Streak

def get_or_create_streak(db: Session, user_id: int) -> Streak:
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    if not streak:
        streak = Streak(user_id=user_id, current_streak=0, best_streak=0)
        db.add(streak)
        db.commit()
        db.refresh(streak)
    return streak

def get_streak(db: Session, user_id: int) -> Streak:
    return get_or_create_streak(db, user_id)

def checkin(db: Session, user_id: int) -> Streak:
    streak = get_or_create_streak(db, user_id)
    today  = date.today()

    # Already checked in today
    if streak.last_active_date == today:
        return streak

    # Consecutive day — increment
    if streak.last_active_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        # Streak broken — reset
        streak.current_streak = 1

    # Update best streak
    if streak.current_streak > streak.best_streak:
        streak.best_streak = streak.current_streak

    streak.last_active_date = today
    db.commit()
    db.refresh(streak)
    return streak