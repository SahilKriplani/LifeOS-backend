from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_URL: str = "http://localhost:3000"
    # OAuth client ID used to verify Google ID tokens. Empty = Google SSO disabled.
    GOOGLE_CLIENT_ID: str = ""

    # ─── Email OTP ────────────────────────────────────────────────────────────
    OTP_LENGTH: int = 6
    OTP_TTL_SECONDS: int = 300              # code is valid for 5 minutes
    OTP_RESEND_COOLDOWN_SECONDS: int = 45   # min gap between two sends
    OTP_MAX_PER_HOUR: int = 5               # sends per email per rolling hour
    OTP_MAX_ATTEMPTS: int = 5               # wrong tries before a code dies

    # ─── Email delivery (Resend) ──────────────────────────────────────────────
    # Resend HTTP API (https://resend.com). If RESEND_API_KEY is empty the OTP
    # is logged to the server console instead of being emailed — so the flow is
    # testable in dev with zero setup.
    #   RESEND_FROM must use a domain you've verified in Resend. The shared
    #   sandbox sender "onboarding@resend.dev" works WITHOUT domain verification
    #   but can only deliver to the email address that owns the Resend account.
    RESEND_API_KEY: str = ""
    RESEND_FROM: str = "LifeOS <onboarding@resend.dev>"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()