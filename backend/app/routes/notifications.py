from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.config.database import get_db
from app.services.notification_service import NotificationService
from app.middleware.auth import get_current_user

router = APIRouter()

class TelegramNotificationRequest(BaseModel):
    chat_id: str
    telegram_username: str = None

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

@router.post("/telegram/enable")
async def enable_telegram_notifications(
    request: TelegramNotificationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable Telegram notifications for the current user"""
    notification_service = NotificationService(db)
    
    success = notification_service.enable_telegram_notifications(
        current_user.id,
        request.chat_id
    )
    
    if success:
        # Update user's telegram username if provided
        if request.telegram_username:
            current_user.telegram_username = request.telegram_username
            db.commit()
        
        return {
            "message": "Telegram notifications enabled successfully",
            "telegram_chat_id": request.chat_id,
            "telegram_username": request.telegram_username
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to enable Telegram notifications"
        )

@router.post("/telegram/disable")
async def disable_telegram_notifications(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable Telegram notifications for the current user"""
    notification_service = NotificationService(db)
    
    success = notification_service.disable_telegram_notifications(current_user.id)
    
    if success:
        return {
            "message": "Telegram notifications disabled successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable Telegram notifications"
        )

@router.get("/telegram/status")
async def get_telegram_notification_status(
    current_user = Depends(get_current_user)
):
    """Get Telegram notification status for the current user"""
    return {
        "enabled": current_user.telegram_notifications_enabled or False,
        "chat_id": current_user.telegram_chat_id,
        "telegram_username": current_user.telegram_username
    }
