from sqlalchemy import Column, Integer, String, Date, Numeric, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    """A single income or expense entry, tied to an account and (optionally) a
    category. Deleting the account reassigns its transactions to Cash rather than
    losing history; deleting a category leaves the transaction as 'Uncategorized'
    (category_id -> NULL)."""

    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id  = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    type        = Column(Enum("income", "expense"), nullable=False)
    amount      = Column(Numeric(12, 2), nullable=False)
    note        = Column(String(255), nullable=True)
    date        = Column(Date, nullable=False)
    created_at  = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Transaction id={self.id} type={self.type} amount={self.amount}>"
