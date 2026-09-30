from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_seeker: bool = True
    department: Optional[str] = None
    telegram_username: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile: Optional[str] = None
    department: Optional[str] = None
    telegram_username: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    detail: str
    reset_token: Optional[str] = None  # only populated when EXPOSE_RESET_TOKEN is True (dev)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
