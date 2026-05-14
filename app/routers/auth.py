from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
)
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ─── Register ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=AuthResponse)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return AuthResponse(
        success=True,
        message="Account created successfully",
        user=UserResponse.model_validate(user),
        token=token,
    )


# ─── Login ────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id)})

    return AuthResponse(
        success=True,
        message="Logged in successfully",
        user=UserResponse.model_validate(user),
        token=token,
    )


# ─── Logout ───────────────────────────────────────────────────────────────────
@router.post("/logout")
def logout():
    return {
        "success": True,
        "message": "Logged out successfully",
    }


# ─── Me ───────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=AuthResponse)
def me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AuthResponse(
        success=True,
        message="Authenticated",
        user=UserResponse.model_validate(current_user),
    )


# ─── Update Profile ───────────────────────────────────────────────────────────
@router.patch("/update-profile", response_model=AuthResponse)
def update_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.name:
        current_user.name = payload.name

    db.commit()
    db.refresh(current_user)

    return AuthResponse(
        success=True,
        message="Profile updated",
        user=UserResponse.model_validate(current_user),
    )


# ─── Change Password ──────────────────────────────────────────────────────────
@router.patch("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password = hash_password(payload.new_password)
    db.commit()

    return {
        "success": True,
        "message": "Password changed successfully",
    }