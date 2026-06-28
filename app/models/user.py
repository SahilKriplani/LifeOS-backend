from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False, index=True)
    # Nullable: Google-only accounts have no local password.
    password   = Column(String(255), nullable=True)
    # Google "sub" claim — set when the account is linked to Google sign-in.
    google_id  = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"