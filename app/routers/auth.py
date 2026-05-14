from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest, AuthResponse, UserResponse,  UpdateProfileRequest, ChangePasswordRequest
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# ─── Register ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Set JWT cookie
    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="none",
        secure=True,
        path="/",
    )

    return AuthResponse(
        success=True,
        message="Account created successfully",
        user=UserResponse.model_validate(user),
    )

# ─── Login ────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Set JWT cookie
    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,   # set True in production (HTTPS)
    )

    return AuthResponse(
        success=True,
        message="Logged in successfully",
        user=UserResponse.model_validate(user),
    )

# ─── Logout ───────────────────────────────────────────────────────────────────
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
    key="access_token",
    path="/",
    samesite="none",
    secure=True,
)
    return {"success": True, "message": "Logged out successfully"}

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

@router.patch("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    current_user.password = hash_password(payload.new_password)
    db.commit()
    return {"success": True, "message": "Password changed successfully"}