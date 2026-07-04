from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.category import Category

# Starter categories seeded on a user's first visit to the finance module. They
# can rename, delete, or add to these freely — this is just a sensible baseline
# so the module isn't empty on day one.
DEFAULT_EXPENSE_CATEGORIES = [
    "Food", "Groceries", "Transport", "Shopping",
    "Bills", "Health", "Entertainment", "Other",
]
DEFAULT_INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investments", "Gift", "Other",
]


def ensure_finance_defaults(db: Session, user_id: int) -> None:
    """Idempotent bootstrap: give a user their undeletable 'Cash' account and a
    starter set of categories the first time they touch the finance module.
    Called at the top of the finance GET endpoints, so existing users get
    back-filled too without any auth-flow changes."""
    changed = False

    has_account = db.query(Account).filter(Account.user_id == user_id).count()
    if not has_account:
        db.add(Account(
            user_id=user_id,
            name="Cash",
            opening_balance=Decimal("0"),
            is_default=True,
        ))
        changed = True

    has_category = db.query(Category).filter(Category.user_id == user_id).count()
    if not has_category:
        for name in DEFAULT_EXPENSE_CATEGORIES:
            db.add(Category(user_id=user_id, name=name, type="expense"))
        for name in DEFAULT_INCOME_CATEGORIES:
            db.add(Category(user_id=user_id, name=name, type="income"))
        changed = True

    if changed:
        db.commit()
