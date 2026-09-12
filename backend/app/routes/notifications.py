from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.notification_service import NotificationService
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    return notification_service.get_user_notifications(user.id, unread_only)

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    notification = notification_service.mark_as_read(notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification

@router.put("/read-all")
async def mark_all_as_read(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    count = notification_service.mark_all_as_read(user.id)
    return {"marked_as_read": count}
