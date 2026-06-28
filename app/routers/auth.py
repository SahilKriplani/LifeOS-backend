from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    GoogleAuthRequest,
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


# ─── Google SSO ───────────────────────────────────────────────────────────────
@router.post("/google", response_model=AuthResponse)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured",
        )

    # Verify the ID token: checks Google's signature, audience (our client id),
    # issuer and expiry. Raises ValueError if anything is off.
    try:
        claims = google_id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    if not claims.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email not verified",
        )

    google_sub = claims["sub"]
    email = claims["email"]
    name = claims.get("name") or email.split("@")[0]

    # 1) Already linked to this Google account → log in.
    user = db.query(User).filter(User.google_id == google_sub).first()

    # 2) Existing local account with the same (verified) email → link it.
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_sub
        else:
            # 3) Brand-new user — create a passwordless Google account.
            user = User(name=name, email=email, google_id=google_sub, password=None)
            db.add(user)

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return AuthResponse(
        success=True,
        message="Logged in with Google",
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