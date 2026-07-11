from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    """A user-owned income or expense category. Users keep only the categories
    they care about. An expense category may carry an optional monthly `budget`;
    spend against it is computed on the fly (current calendar month) for the
    progress-bar tracking on the finance page."""

    __tablename__ = "categories"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name       = Column(String(50), nullable=False)
    type       = Column(Enum("income", "expense"), nullable=False)
    # Optional monthly budget (expense categories). NULL = untracked.
    budget     = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Category id={self.id} name={self.name} type={self.type}>"
