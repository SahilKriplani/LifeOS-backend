from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, Enum
from app.database import Base

class Goal(Base):
    __tablename__ = "goals"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title       = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target      = Column(Numeric(10, 2), nullable=False)
    current     = Column(Numeric(10, 2), default=0)
    unit        = Column(String(50), nullable=False)
    color       = Column(String(20), default="#14B8A6")
    category    = Column(Enum("dsa", "fitness", "career", "personal"), default="personal")
    deadline    = Column(Date, nullable=False)

    def __repr__(self):
        return f"<Goal id={self.id} title={self.title}>"