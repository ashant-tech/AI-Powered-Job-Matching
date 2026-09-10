from sqlalchemy.orm import Session

from app.middleware.error_handler import AppError
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.jwt import create_access_token
from app.utils.security import hash_password, verify_password


def register_user(db: Session, data: UserCreate) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise AppError("Email already registered", 409)
    user = User(email=data.email, full_name=data.full_name, phone=data.phone, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> tuple[User, str]:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise AppError("Invalid email or password", 401)
    return user, create_access_token(str(user.id))
