from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class OtpCode(Base):
    """
    A short-lived, single-use email login code.

    We store only an HMAC of the 6-digit code (never the code itself), with a
    hard expiry and an attempt counter so a code can be brute-force-capped and
    auto-invalidated. Rows are disposable — the latest unconsumed, unexpired row
    for an identifier is the only one that can be verified.
    """

    __tablename__ = "otp_codes"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    # Lower-cased email the code was issued to.
    identifier  = Column(String(150), nullable=False, index=True)
    channel     = Column(String(10),  nullable=False, default="email")
    purpose     = Column(String(20),  nullable=False, default="login")
    # Hex HMAC-SHA256 of the code (64 chars). Never the plaintext code.
    code_hash   = Column(String(64),  nullable=False)
    attempts    = Column(Integer,     nullable=False, default=0)
    expires_at  = Column(DateTime,    nullable=False)
    consumed_at = Column(DateTime,    nullable=True)
    created_at  = Column(DateTime,    server_default=func.now())

    __table_args__ = (
        # Fast lookup of "latest live code for this email".
        Index("idx_otp_identifier_created", "identifier", "created_at"),
    )

    def __repr__(self):
        return f"<OtpCode id={self.id} identifier={self.identifier}>"
