from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from app.database import Base

class DSALog(Base):
    __tablename__ = "dsa_logs"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_name = Column(String(255), nullable=False)
    platform     = Column(Enum("leetcode", "codeforces", "gfg", "other"), default="leetcode")
    difficulty   = Column(Enum("easy", "medium", "hard"), nullable=False)
    topic        = Column(String(100))
    solved_at    = Column(Date, nullable=False)

    def __repr__(self):
        return f"<DSALog id={self.id} problem={self.problem_name}>"