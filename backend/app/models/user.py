from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.config.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_seeker = Column(Boolean, default=True)  # True for job seeker, False for employer
    department = Column(String)  # Field of study, e.g. "Computer Science" — drives job recommendations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    profile = Column(Text)  # JSON string for profile data
    
    # Telegram notification settings
    telegram_chat_id = Column(String, nullable=True)  # Telegram chat ID for notifications
    telegram_notifications_enabled = Column(Boolean, default=False)  # Enable/disable Telegram notifications
    telegram_username = Column(String, nullable=True)  # Telegram username (optional)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, index=True)  # sha256 of the raw token
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
