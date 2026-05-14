from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, tasks, dsa, fitness, streaks, goals
from app.models import User, Task, DSALog, FitnessLog, Streak,Goal

# ─── Create all tables ────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="LifeOS API",
    description="Backend API for LifeOS personal dashboard",
    version="1.0.0",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://life-os-web-git-main-sahil-kriplani-s-projects.vercel.app",
        "https://life-os-web-rosy.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/api/v1")
app.include_router(tasks.router,    prefix="/api/v1")
app.include_router(dsa.router,      prefix="/api/v1")
app.include_router(fitness.router,  prefix="/api/v1")
app.include_router(streaks.router,  prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")

# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "LifeOS API is running"}