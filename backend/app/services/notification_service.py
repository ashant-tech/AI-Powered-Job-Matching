from sqlalchemy.orm import Session
from typing import List
from app.models.notification import Notification
from app.models.user import User

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).all()

    def mark_as_read(self, notification_id: int) -> Notification:
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        return count

    def send_match_notification(self, user_id: int, match_count: int) -> Notification:
        title = "New Job Matches Found"
        message = f"We found {match_count} new job matches for your profile. Check your recommendations!"
        
        return self.create_notification(user_id, "match", title, message)

    def send_application_notification(self, user_id: int, job_title: str, company: str) -> Notification:
        title = "Application Status Update"
        message = f"Your application for {job_title} at {company} has been viewed."
        
        return self.create_notification(user_id, "application", title, message)
