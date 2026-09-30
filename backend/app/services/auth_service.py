from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
import secrets
from app.models.user import User, PasswordResetToken
from app.schemas.user import UserCreate, UserUpdate
from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: UserCreate) -> User:
        hashed_password = pwd_context.hash(user.password)
        telegram_username = (user.telegram_username or "").strip().lstrip("@") or None
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            phone=user.phone,
            is_seeker=user.is_seeker,
            department=(user.department or "").strip() or None,
            telegram_username=telegram_username,
            telegram_notifications_enabled=telegram_username is not None
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise ValueError("Invalid token")
        except JWTError:
            raise ValueError("Invalid token")
        
        user = self.get_user_by_email(email)
        if user is None:
            raise ValueError("User not found")
        return user

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "telegram_username" in update_data:
            username = (update_data["telegram_username"] or "").strip().lstrip("@") or None
            update_data["telegram_username"] = username
            if username:
                update_data["telegram_notifications_enabled"] = True
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_password_reset_token(self, email: str) -> str | None:
        """Create a single-use reset token for the user with this email.

        Returns the raw token if the user exists, otherwise None. Existing
        unused tokens for the user are invalidated so only the newest works.
        """
        user = self.get_user_by_email(email)
        if not user:
            return None

        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,  # noqa: E712
        ).update({"used": True})

        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )
        self.db.add(PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=expires_at,
            used=False,
        ))
        self.db.commit()
        return raw_token

    def reset_password(self, raw_token: str, new_password: str) -> bool:
        """Consume a valid reset token and set a new password. Returns success."""
        record = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token_hash == _hash_token(raw_token)
        ).first()
        if not record or record.used:
            return False

        expires_at = record.expires_at
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
        if expires_at < datetime.utcnow():
            return False

        user = self.get_user_by_id(record.user_id)
        if not user:
            return False

        user.hashed_password = pwd_context.hash(new_password)
        record.used = True
        self.db.commit()
        return True
