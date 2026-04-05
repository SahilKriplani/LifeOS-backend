from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ─── Register ─────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

# ─── Login ────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ─── User response (never expose password) ───────────────────────────────────
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}

# ─── Generic auth response ────────────────────────────────────────────────────
class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None