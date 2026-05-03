from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title          = Column(String(255), nullable=False)
    is_done        = Column(Boolean, default=False)
    scheduled_date = Column(Date, nullable=False)
    priority       = Column(Enum("low", "medium", "high"), default="medium")
    created_at     = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Task id={self.id} title={self.title}>"