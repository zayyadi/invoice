from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)
    company_name: str | None = None
    phone: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: str
    company_name: str | None
    phone: str | None
    timezone: str
    default_currency: str
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    phone: str | None = None
    timezone: str | None = None
    default_currency: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
