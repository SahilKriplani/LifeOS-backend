from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.streak import Streak
from app.models.activity_day import ActivityDay

def record_activity(db: Session, user_id: int, day: date) -> None:
    """Idempotently mark a single day as active for this user."""
    exists = db.query(ActivityDay).filter(
        ActivityDay.user_id == user_id,
        ActivityDay.activity_date == day,
    ).first()
    if not exists:
        db.add(ActivityDay(user_id=user_id, activity_date=day))

def backfill_from_streak(db: Session, streak: "Streak") -> None:
    """One-time self-heal for streaks that predate per-day activity tracking.

    A current streak of N days ending on `last_active_date` means those N
    consecutive days were active, so we can safely reconstruct their rows.
    Idempotent: record_activity skips days that already exist.
    """
    if not streak.last_active_date or streak.current_streak < 1:
        return
    for i in range(streak.current_streak):
        record_activity(db, streak.user_id, streak.last_active_date - timedelta(days=i))
    db.commit()

def get_active_dates(db: Session, user_id: int, since: date) -> list[date]:
    """All active dates for this user on or after `since`, newest first."""
    rows = (
        db.query(ActivityDay.activity_date)
        .filter(ActivityDay.user_id == user_id, ActivityDay.activity_date >= since)
        .order_by(ActivityDay.activity_date.desc())
        .all()
    )
    return [r[0] for r in rows]

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

    # Always record today as an active day (idempotent) — this drives the
    # calendar grids independently of the running streak counters.
    record_activity(db, user_id, today)

    # Already checked in today
    if streak.last_active_date == today:
        db.commit()
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