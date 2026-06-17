from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    PasswordChange,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRead,
    UserRegister,
    UserUpdate,
)
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    user = auth_service.register_user(db, payload)
    return auth_service.create_tokens(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = auth_service.authenticate_user(db, payload)
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    return auth_service.refresh_access_token(payload.refresh_token, db)


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user


@router.put("/me", response_model=UserRead)
def update_current_user(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    return auth_service.update_user(db, current_user, payload)


@router.post("/me/password")
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change current user password."""
    auth_service.change_password(db, current_user, payload.current_password, payload.new_password)
    return {"message": "Password changed successfully"}
