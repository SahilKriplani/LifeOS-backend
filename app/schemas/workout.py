from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional

# Allowed muscle groups — shared by seed data, custom-exercise validation,
# and (mirrored on) the frontend grouping UI.
MUSCLE_GROUPS = [
    "chest",
    "back",
    "shoulders",
    "biceps",
    "triceps",
    "quads",
    "hamstrings",
    "glutes",
    "calves",
    "core",
    "forearms",
    "cardio",
]

# ─── Exercise library ──────────────────────────────────────────────────────────
class CreateExerciseRequest(BaseModel):
    name:         str = Field(min_length=1, max_length=120)
    muscle_group: str


class ExerciseResponse(BaseModel):
    id:           int
    name:         str
    muscle_group: str
    is_custom:    bool
    user_id:      Optional[int]

    model_config = {"from_attributes": True}


class ExerciseListResponse(BaseModel):
    success: bool
    data:    list[ExerciseResponse]
    message: str = "OK"


class ExerciseSingleResponse(BaseModel):
    success: bool
    data:    ExerciseResponse
    message: str = "OK"


# ─── Workout input (a whole session) ───────────────────────────────────────────
class WorkoutSetInput(BaseModel):
    weight_kg: Optional[Decimal] = None
    reps:      int = Field(ge=0)


class WorkoutEntryInput(BaseModel):
    exercise_id: int
    sets:        list[WorkoutSetInput] = Field(min_length=1)


class CreateWorkoutRequest(BaseModel):
    log_date: date
    notes:    Optional[str] = None
    entries:  list[WorkoutEntryInput] = Field(min_length=1)


# ─── Workout output (grouped exercise → sets) ──────────────────────────────────
class WorkoutSetResponse(BaseModel):
    set_number: int
    weight_kg:  Optional[Decimal]
    reps:       int


class WorkoutExerciseResponse(BaseModel):
    exercise_id:   int
    exercise_name: str
    muscle_group:  str
    sets:          list[WorkoutSetResponse]


class WorkoutSessionResponse(BaseModel):
    id:        int
    user_id:   int
    log_date:  date
    notes:     Optional[str]
    exercises: list[WorkoutExerciseResponse]


class WorkoutListResponse(BaseModel):
    success: bool
    data:    list[WorkoutSessionResponse]
    message: str = "OK"


class WorkoutSingleResponse(BaseModel):
    success: bool
    data:    WorkoutSessionResponse
    message: str = "OK"
