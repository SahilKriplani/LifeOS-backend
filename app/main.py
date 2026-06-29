from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, tasks, dsa, fitness, streaks, goals, exercises, workouts
from app.models import (
    User, OtpCode, Task, DSALog, FitnessLog, Streak, ActivityDay, Goal,
    Exercise, WorkoutLog, WorkoutSet,
)
from app.services.workout_service import seed_global_exercises

# ─── Create all tables ────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Seed the global exercise library (idempotent) ────────────────────────────
_seed_db = SessionLocal()
try:
    seed_global_exercises(_seed_db)
finally:
    _seed_db.close()

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
        "https://life-os-web-rosy.vercel.app",
    ],
    # Match every Vercel URL for this project (production alias + per-deploy
    # preview URLs), so a deploy on a new preview/alias domain doesn't 500 the
    # browser with a CORS "Network Error" the way a hardcoded list does.
    allow_origin_regex=r"https://life-os-web.*\.vercel\.app",
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
app.include_router(exercises.router, prefix="/api/v1")
app.include_router(workouts.router,  prefix="/api/v1")

# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "LifeOS API is running"}