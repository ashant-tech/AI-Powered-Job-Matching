from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.config.settings import settings
from app.middleware.rate_limit import RateLimiter
from app.schemas.user import (
    UserCreate,
    UserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
)
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

register_limiter = RateLimiter(max_requests=5, window_seconds=3600)
login_limiter = RateLimiter(max_requests=20, window_seconds=600)
forgot_limiter = RateLimiter(max_requests=5, window_seconds=600)
reset_limiter = RateLimiter(max_requests=10, window_seconds=600)

_GENERIC_FORGOT_DETAIL = (
    "If an account exists for that email, a password reset link has been sent."
)

@router.post("/register", response_model=UserResponse, dependencies=[Depends(register_limiter)])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    db_user = auth_service.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return auth_service.create_user(user)

@router.post("/login", dependencies=[Depends(login_limiter)])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    return user


@router.post("/forgot-password", response_model=ForgotPasswordResponse, dependencies=[Depends(forgot_limiter)])
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Create a reset token and email it. Always returns the same generic detail
    so the endpoint can't be used to discover which emails are registered."""
    auth_service = AuthService(db)
    raw_token = auth_service.create_password_reset_token(payload.email)

    reset_token_response = None
    if raw_token:
        user = auth_service.get_user_by_email(payload.email)
        reset_link = (
            f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw_token}"
        )
        try:
            from app.notifications.email import EmailService

            EmailService().send_password_reset_email(
                to_email=payload.email,
                user_name=(user.full_name or user.username) if user else "there",
                reset_link=reset_link,
                expire_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
            )
        except Exception:
            # Email delivery is best-effort; a missing SMTP config must not
            # break the request or reveal whether the account exists.
            pass

        if settings.EXPOSE_RESET_TOKEN:
            reset_token_response = raw_token

    return ForgotPasswordResponse(detail=_GENERIC_FORGOT_DETAIL, reset_token=reset_token_response)


@router.post("/reset-password", dependencies=[Depends(reset_limiter)])
async def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )
    ok = auth_service.reset_password(payload.token, payload.new_password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return {"detail": "Password has been reset. You can now sign in."}
