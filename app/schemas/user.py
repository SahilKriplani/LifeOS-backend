from pydantic import BaseModel, EmailStr, Field
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
    user: UserResponse
    token: str | None = None
    
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str = Field(min_length=6)