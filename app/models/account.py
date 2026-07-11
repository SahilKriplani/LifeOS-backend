from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Account(Base):
    """A user-defined money bucket (Cash, Bank, Wallet, etc.). We never link a
    real bank — an account is just a labelled balance the user segregates money
    into. Its live balance is *derived* (opening_balance + income − expense),
    never stored, so it can't drift out of sync with the ledger."""

    __tablename__ = "accounts"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name            = Column(String(50), nullable=False)
    opening_balance = Column(Numeric(12, 2), nullable=False, default=0)
    # The default "Cash" account seeded for every user — cannot be deleted.
    is_default      = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Account id={self.id} name={self.name} default={self.is_default}>"
