from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from decimal import Decimal
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

# ─── Google SSO ───────────────────────────────────────────────────────────────
class GoogleAuthRequest(BaseModel):
    # The ID token (JWT credential) returned by Google Identity Services.
    credential: str

# ─── Email OTP ────────────────────────────────────────────────────────────────
class OtpRequestRequest(BaseModel):
    email: EmailStr
    # Optional display name, only used when the code creates a brand-new account.
    name: Optional[str] = None

class OtpVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)
    name: Optional[str] = None

class OtpRequestResponse(BaseModel):
    success: bool
    message: str
    # Seconds the client must wait before it may request another code.
    retry_after: int

# ─── User response (never expose password) ───────────────────────────────────
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    target_weight_kg: Optional[Decimal] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ─── Generic auth response ────────────────────────────────────────────────────
class AuthResponse(BaseModel):
    success: bool
    message: str
    user: UserResponse
    token: Optional[str] = None
    
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    # Goal weight in kg. Send 0 / null handling is done in the router.
    target_weight_kg: Optional[Decimal] = Field(default=None, ge=20, le=400)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str = Field(min_length=6)