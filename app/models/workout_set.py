from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WorkoutSet(Base):
    """One row per set — the true Liftoff model (weight + reps per set)."""

    __tablename__ = "workout_sets"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id", ondelete="CASCADE"), nullable=False)
    exercise_id    = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number     = Column(Integer, nullable=False)
    weight_kg      = Column(Numeric(6, 2))  # nullable — bodyweight moves have no load
    reps           = Column(Integer, nullable=False)

    workout_log = relationship("WorkoutLog", back_populates="sets")
    exercise    = relationship("Exercise")

    def __repr__(self):
        return f"<WorkoutSet id={self.id} ex={self.exercise_id} #{self.set_number}>"
