from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from app.database import Base

class ActivityDay(Base):
    """One row per day the user was active (checked in).

    The `streaks` table only tracks the running counters, so it can't tell us
    *which* days were active — that's what powers the calendar's week/month
    grids. We keep one row per (user, date) and read a recent window of them.
    """
    __tablename__ = "activity_days"
    __table_args__ = (
        UniqueConstraint("user_id", "activity_date", name="uq_activity_user_date"),
    )

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_date = Column(Date, nullable=False)

    def __repr__(self):
        return f"<ActivityDay user_id={self.user_id} date={self.activity_date}>"
