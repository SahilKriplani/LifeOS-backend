from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.otp import OtpCode
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    GoogleAuthRequest,
    OtpRequestRequest,
    OtpVerifyRequest,
    OtpRequestResponse,
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
from app.utils.otp import generate_otp, hash_otp, verify_otp
from app.services.email_service import send_otp_email

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


# ─── Email OTP: request a code ────────────────────────────────────────────────
@router.post("/otp/request", response_model=OtpRequestResponse)
def request_otp(
    payload: OtpRequestRequest,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    ident = payload.email.strip().lower()

    # 1) Resend cooldown — block a new code if one was just issued.
    last = (
        db.query(OtpCode)
        .filter(OtpCode.identifier == ident)
        .order_by(OtpCode.created_at.desc())
        .first()
    )
    if last and last.created_at:
        elapsed = (now - last.created_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait}s before requesting another code.",
            )

    # 2) Hourly cap per email — blunt abuse / bill protection.
    sent_last_hour = (
        db.query(OtpCode)
        .filter(
            OtpCode.identifier == ident,
            OtpCode.created_at > now - timedelta(hours=1),
        )
        .count()
    )
    if sent_last_hour >= settings.OTP_MAX_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many codes requested. Please try again later.",
        )

    # 3) Generate + deliver FIRST. If email delivery fails we persist nothing,
    #    so the user can retry immediately.
    code = generate_otp()
    try:
        send_otp_email(ident, code)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    # 4) Invalidate any still-live codes for this email, then store the new one.
    db.query(OtpCode).filter(
        OtpCode.identifier == ident,
        OtpCode.consumed_at.is_(None),
    ).update({OtpCode.consumed_at: now}, synchronize_session=False)

    db.add(
        OtpCode(
            identifier=ident,
            code_hash=hash_otp(code),
            expires_at=now + timedelta(seconds=settings.OTP_TTL_SECONDS),
            created_at=now,
        )
    )
    db.commit()

    return OtpRequestResponse(
        success=True,
        message="We've sent a 6-digit code to your email.",
        retry_after=settings.OTP_RESEND_COOLDOWN_SECONDS,
    )


# ─── Email OTP: verify a code (logs in OR creates the account) ─────────────────
@router.post("/otp/verify", response_model=AuthResponse)
def verify_otp_code(
    payload: OtpVerifyRequest,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    ident = payload.email.strip().lower()

    otp = (
        db.query(OtpCode)
        .filter(
            OtpCode.identifier == ident,
            OtpCode.consumed_at.is_(None),
        )
        .order_by(OtpCode.created_at.desc())
        .first()
    )

    invalid = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired code. Please request a new one.",
    )

    if not otp:
        raise invalid

    if otp.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This code has expired. Please request a new one.",
        )

    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        otp.consumed_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many incorrect attempts. Please request a new code.",
        )

    if not verify_otp(payload.code.strip(), otp.code_hash):
        otp.attempts += 1
        db.commit()
        remaining = settings.OTP_MAX_ATTEMPTS - otp.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect code. {remaining} attempt(s) left.",
        )

    # Correct code → consume it (single use).
    otp.consumed_at = now

    # Find-or-create the account. Match case-insensitively so legacy mixed-case
    # rows still resolve. New accounts are passwordless (OTP / Google only).
    user = db.query(User).filter(func.lower(User.email) == ident).first()
    if not user:
        display = (payload.name or "").strip() or ident.split("@")[0]
        user = User(name=display, email=ident, password=None)
        db.add(user)

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return AuthResponse(
        success=True,
        message="Signed in successfully",
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

    if payload.target_weight_kg is not None:
        current_user.target_weight_kg = payload.target_weight_kg

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