from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class PlatformEnum(str, Enum):
    leetcode   = "leetcode"
    codeforces = "codeforces"
    gfg        = "gfg"
    other      = "other"

class DifficultyEnum(str, Enum):
    easy   = "easy"
    medium = "medium"
    hard   = "hard"

class CreateDSALogRequest(BaseModel):
    problem_name: str
    platform:     PlatformEnum     = PlatformEnum.leetcode
    difficulty:   DifficultyEnum
    topic:        Optional[str]    = None
    solved_at:    date

class DSALogResponse(BaseModel):
    id:           int
    user_id:      int
    problem_name: str
    platform:     PlatformEnum
    difficulty:   DifficultyEnum
    topic:        Optional[str]
    solved_at:    date

    model_config = {"from_attributes": True}

class DSAStatsResponse(BaseModel):
    total:    int
    easy:     int
    medium:   int
    hard:     int
    by_topic: dict[str, int]

class DSALogListResponse(BaseModel):
    success: bool
    data:    list[DSALogResponse]
    message: str = "OK"

class DSALogSingleResponse(BaseModel):
    success: bool
    data:    DSALogResponse
    message: str = "OK"

class DSAStatsWrapped(BaseModel):
    success: bool
    data:    DSAStatsResponse
    message: str = "OK"