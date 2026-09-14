from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.notification_service import NotificationService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    return notification_service.get_user_notifications(current_user.id, unread_only)

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    
    notification = notification_service.mark_as_read(notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification

@router.put("/read-all")
async def mark_all_as_read(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    count = notification_service.mark_all_as_read(current_user.id)
    return {"marked_as_read": count}
