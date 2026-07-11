from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException, status

from app.models.exercise import Exercise
from app.models.workout_log import WorkoutLog
from app.models.workout_set import WorkoutSet
from app.schemas.workout import (
    MUSCLE_GROUPS,
    CreateExerciseRequest,
    CreateWorkoutRequest,
    WorkoutSessionResponse,
)

# ─── Global seed library (~50 exercises, grouped by muscle) ─────────────────────
GLOBAL_EXERCISES = {
    "chest":      ["Barbell Bench Press", "Incline Dumbbell Press", "Dumbbell Fly",
                   "Push-Up", "Cable Crossover", "Chest Dip"],
    "back":       ["Deadlift", "Pull-Up", "Lat Pulldown", "Barbell Row",
                   "Seated Cable Row", "T-Bar Row", "Face Pull"],
    "shoulders":  ["Overhead Press", "Dumbbell Shoulder Press", "Lateral Raise",
                   "Front Raise", "Rear Delt Fly", "Arnold Press"],
    "biceps":     ["Barbell Curl", "Dumbbell Curl", "Hammer Curl",
                   "Preacher Curl", "Concentration Curl"],
    "triceps":    ["Tricep Pushdown", "Overhead Tricep Extension", "Skull Crusher",
                   "Close-Grip Bench Press", "Tricep Dip"],
    "quads":      ["Back Squat", "Front Squat", "Leg Press", "Leg Extension",
                   "Walking Lunge", "Bulgarian Split Squat"],
    "hamstrings": ["Romanian Deadlift", "Leg Curl", "Good Morning"],
    "glutes":     ["Hip Thrust", "Glute Bridge", "Cable Kickback"],
    "calves":     ["Standing Calf Raise", "Seated Calf Raise"],
    "core":       ["Plank", "Crunch", "Hanging Leg Raise", "Russian Twist", "Cable Crunch"],
    "forearms":   ["Wrist Curl", "Farmer's Walk"],
    "cardio":     ["Treadmill Run", "Cycling", "Rowing Machine", "Jump Rope"],
}


def seed_global_exercises(db: Session):
    """Idempotent — only inserts the global library if it's empty."""
    existing = db.query(Exercise).filter(Exercise.user_id.is_(None)).count()
    if existing > 0:
        return
    for muscle, names in GLOBAL_EXERCISES.items():
        for name in names:
            db.add(Exercise(name=name, muscle_group=muscle, is_custom=False, user_id=None))
    db.commit()


# ─── Exercise library ──────────────────────────────────────────────────────────
def get_exercises(db: Session, user_id: int):
    """Global seeds + this user's custom exercises."""
    return (
        db.query(Exercise)
        .filter((Exercise.user_id.is_(None)) | (Exercise.user_id == user_id))
        .order_by(Exercise.muscle_group.asc(), Exercise.name.asc())
        .all()
    )


def create_exercise(db: Session, user_id: int, payload: CreateExerciseRequest):
    if payload.muscle_group not in MUSCLE_GROUPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid muscle group. Allowed: {', '.join(MUSCLE_GROUPS)}",
        )

    name = payload.name.strip()

    # Avoid duplicates against globals or the user's own custom list (case-insensitive).
    clash = (
        db.query(Exercise)
        .filter(
            (Exercise.user_id.is_(None)) | (Exercise.user_id == user_id),
            Exercise.name.ilike(name),
        )
        .first()
    )
    if clash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An exercise with that name already exists",
        )

    exercise = Exercise(name=name, muscle_group=payload.muscle_group, is_custom=True, user_id=user_id)
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, user_id: int, exercise_id: int):
    exercise = (
        db.query(Exercise)
        .filter(Exercise.id == exercise_id, Exercise.user_id == user_id, Exercise.is_custom.is_(True))
        .first()
    )
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom exercise not found")

    in_use = db.query(WorkoutSet).filter(WorkoutSet.exercise_id == exercise_id).first()
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise is used in a logged workout and can't be deleted",
        )

    db.delete(exercise)
    db.commit()
    return True


# ─── Workout sessions ──────────────────────────────────────────────────────────
def _serialize_session(db: Session, log: WorkoutLog) -> WorkoutSessionResponse:
    """Flatten one-row-per-set storage into Liftoff-style grouped output."""
    sets = (
        db.query(WorkoutSet)
        .filter(WorkoutSet.workout_log_id == log.id)
        .order_by(WorkoutSet.id.asc())
        .all()
    )

    grouped: dict = {}
    order: list = []
    for s in sets:
        if s.exercise_id not in grouped:
            ex = s.exercise
            grouped[s.exercise_id] = {
                "exercise_id": s.exercise_id,
                "exercise_name": ex.name if ex else "Unknown",
                "muscle_group": ex.muscle_group if ex else "other",
                "sets": [],
            }
            order.append(s.exercise_id)
        grouped[s.exercise_id]["sets"].append(
            {"set_number": s.set_number, "weight_kg": s.weight_kg, "reps": s.reps}
        )

    return WorkoutSessionResponse(
        id=log.id,
        user_id=log.user_id,
        log_date=log.log_date,
        notes=log.notes,
        exercises=[grouped[i] for i in order],
    )


def get_workouts(db: Session, user_id: int, from_date: date = None, to_date: date = None):
    query = db.query(WorkoutLog).filter(WorkoutLog.user_id == user_id)
    if from_date:
        query = query.filter(WorkoutLog.log_date >= from_date)
    if to_date:
        query = query.filter(WorkoutLog.log_date <= to_date)
    logs = query.order_by(WorkoutLog.log_date.desc()).all()
    return [_serialize_session(db, log) for log in logs]


def create_workout(db: Session, user_id: int, payload: CreateWorkoutRequest):
    # Validate every exercise is visible to this user (global or own custom).
    valid_ids = {e.id for e in get_exercises(db, user_id)}
    for entry in payload.entries:
        if entry.exercise_id not in valid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid exercise id {entry.exercise_id}",
            )

    # One session per day — reuse the day's session if it already exists.
    log = (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user_id, WorkoutLog.log_date == payload.log_date)
        .first()
    )
    if not log:
        log = WorkoutLog(user_id=user_id, log_date=payload.log_date, notes=payload.notes)
        db.add(log)
        db.flush()  # get log.id without ending the transaction
    elif payload.notes is not None:
        log.notes = payload.notes

    for entry in payload.entries:
        for i, s in enumerate(entry.sets, start=1):
            db.add(
                WorkoutSet(
                    workout_log_id=log.id,
                    exercise_id=entry.exercise_id,
                    set_number=i,
                    weight_kg=s.weight_kg,
                    reps=s.reps,
                )
            )

    db.commit()
    db.refresh(log)
    return _serialize_session(db, log)


def delete_workout(db: Session, user_id: int, log_id: int):
    log = (
        db.query(WorkoutLog)
        .filter(WorkoutLog.id == log_id, WorkoutLog.user_id == user_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    db.delete(log)  # cascade removes its sets
    db.commit()
    return True
