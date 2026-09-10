from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.match import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(unread_only: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return notification_service.list_notifications(db, user, unread_only)


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return notification_service.mark_read(db, user, notification_id)


@router.post("/read-all")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, int]:
    return {"updated": notification_service.mark_all_read(db, user)}
