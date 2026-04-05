from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# ─── Engine ───────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,          # set True to see SQL queries in terminal
    pool_pre_ping=True,  # auto-reconnect if connection drops
)

# ─── Session factory ──────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ─── Base class for all models ────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ─── Dependency — use this in every router ───────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()