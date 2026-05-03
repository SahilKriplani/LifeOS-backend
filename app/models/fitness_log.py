from sqlalchemy import Column, Integer, Date, Numeric, Text, ForeignKey
from app.database import Base

class FitnessLog(Base):
    __tablename__ = "fitness_logs"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    log_date  = Column(Date, nullable=False)
    weight_kg = Column(Numeric(5, 2))
    calories  = Column(Integer)
    steps     = Column(Integer)
    notes     = Column(Text)

    def __repr__(self):
        return f"<FitnessLog id={self.id} date={self.log_date}>"