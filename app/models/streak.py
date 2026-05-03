from sqlalchemy import Column, Integer, Date, ForeignKey
from app.database import Base

class Streak(Base):
    __tablename__ = "streaks"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_streak   = Column(Integer, default=0)
    best_streak      = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)

    def __repr__(self):
        return f"<Streak user_id={self.user_id} current={self.current_streak}>"