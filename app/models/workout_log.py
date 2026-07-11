from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WorkoutLog(Base):
    """A workout session — one per user per day (Liftoff-style)."""

    __tablename__ = "workout_logs"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    user_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False)
    notes    = Column(Text)

    # Deleting a session removes all of its sets.
    sets = relationship(
        "WorkoutSet",
        back_populates="workout_log",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.id",
    )

    def __repr__(self):
        return f"<WorkoutLog id={self.id} user={self.user_id} date={self.log_date}>"
