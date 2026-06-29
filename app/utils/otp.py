import hmac
import hashlib
import secrets
from typing import Optional

from app.config import settings


def generate_otp(length: Optional[int] = None) -> str:
    """Cryptographically-random numeric code, zero-padded to `length`."""
    n = length or settings.OTP_LENGTH
    upper = 10 ** n
    return str(secrets.randbelow(upper)).zfill(n)


def hash_otp(code: str) -> str:
    """
    Deterministic keyed hash (HMAC-SHA256) of the code, keyed by SECRET_KEY.
    Deterministic so we can look the row up and compare without storing the
    plaintext code. Returns 64 hex chars.
    """
    return hmac.new(
        settings.SECRET_KEY.encode(),
        code.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_otp(code: str, code_hash: str) -> bool:
    """Constant-time comparison to avoid timing leaks."""
    return hmac.compare_digest(hash_otp(code), code_hash)
