from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, UserUpdate


def register_user(db: Session, data: UserRegister) -> User:
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        company_name=data.company_name,
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: UserLogin) -> User:
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def create_tokens(user: User) -> dict[str, str]:
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token: str, db: Session) -> dict[str, str]:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_tokens(user)


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.company_name is not None:
        user.company_name = data.company_name
    if data.phone is not None:
        user.phone = data.phone
    if data.timezone is not None:
        user.timezone = data.timezone
    if data.default_currency is not None:
        user.default_currency = data.default_currency

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.password_hash = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
