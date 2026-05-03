from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from enum import Enum

class PriorityEnum(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"

class CreateTaskRequest(BaseModel):
    title:          str
    scheduled_date: date
    priority:       PriorityEnum = PriorityEnum.medium

class UpdateTaskRequest(BaseModel):
    title:    Optional[str]          = None
    is_done:  Optional[bool]         = None
    priority: Optional[PriorityEnum] = None

class TaskResponse(BaseModel):
    id:             int
    user_id:        int
    title:          str
    is_done:        bool
    scheduled_date: date
    priority:       PriorityEnum
    created_at:     datetime

    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    success: bool
    data:    list[TaskResponse]
    message: str = "OK"

class TaskSingleResponse(BaseModel):
    success: bool
    data:    TaskResponse
    message: str = "OK"