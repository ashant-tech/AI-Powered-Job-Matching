from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserOut
from app.services.auth_service import authenticate, register_user
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)) -> Token:
    user = register_user(db, data)
    return Token(access_token=create_access_token(str(user.id)), user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user, token = authenticate(db, form.username, form.password)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login/json", response_model=Token)
def login_json(data: UserLogin, db: Session = Depends(get_db)) -> Token:
    user, token = authenticate(db, data.email, data.password)
    return Token(access_token=token, user=UserOut.model_validate(user))
