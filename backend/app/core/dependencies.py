from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import ensure_database_schema, get_db
from app.core.security import get_password_hash
from app.models.user import User

DEV_EMAIL = "dev@aura-invoice.local"
DEV_PASSWORD_HASH = get_password_hash("dev-password-123")


def _get_or_create_dev_user(db: Session) -> User:
    ensure_database_schema()

    user = db.query(User).filter(User.email == DEV_EMAIL).first()
    if not user:
        user = User(
            email=DEV_EMAIL,
            password_hash=DEV_PASSWORD_HASH,
            full_name="Dev User",
            company_name="Aura Invoice Dev",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    _claim_legacy_records(db, user)
    return user


def _claim_legacy_records(db: Session, user: User) -> None:
    db.execute(
        text("UPDATE invoices SET user_id = :user_id WHERE user_id IS NULL"),
        {"user_id": user.id},
    )
    db.execute(
        text("UPDATE clients SET user_id = :user_id WHERE user_id IS NULL"),
        {"user_id": user.id},
    )
    db.execute(
        text("UPDATE payments SET user_id = :user_id WHERE user_id IS NULL"),
        {"user_id": user.id},
    )
    db.commit()


def get_current_user(
    db: Session = Depends(get_db),
) -> User:
    return _get_or_create_dev_user(db)


def get_optional_user(
    db: Session = Depends(get_db),
) -> User:
    return _get_or_create_dev_user(db)
