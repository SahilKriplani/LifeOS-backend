from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(120), nullable=False)
    muscle_group = Column(String(40), nullable=False)
    is_custom    = Column(Boolean, default=False, nullable=False)
    # user_id NULL  -> global seed exercise (visible to everyone)
    # user_id set   -> custom exercise owned by that user
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name} group={self.muscle_group}>"
