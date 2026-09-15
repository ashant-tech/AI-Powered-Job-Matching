from sqlalchemy.orm import Session
from typing import List
from app.models.notification import Notification
from app.models.user import User
from app.notifications.telegram import TelegramNotificationService

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.telegram_service = TelegramNotificationService()

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        send_telegram: bool = True
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
        
        # Send Telegram notification if enabled
        if send_telegram:
            self._send_telegram_notification(user_id, notification_type, title, message)
        
        return notification

    def _send_telegram_notification(self, user_id: int, notification_type: str, title: str, message: str):
        """Send Telegram notification if user has enabled it"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.telegram_chat_id and user.telegram_notifications_enabled:
                if notification_type == "match":
                    # For match notifications, we need job details - will be handled by calling method
                    self.telegram_service.send_telegram_message(
                        user.telegram_chat_id,
                        f"🎯 {title}\n\n{message}"
                    )
                elif notification_type == "application":
                    self.telegram_service.send_telegram_message(
                        user.telegram_chat_id,
                        f"📋 {title}\n\n{message}"
                    )
                else:
                    self.telegram_service.send_telegram_message(
                        user.telegram_chat_id,
                        f"🔔 {title}\n\n{message}"
                    )
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")

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

    def send_match_notification(self, user_id: int, match_count: int, top_jobs: list = None) -> Notification:
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user else "User"
        
        title = "New Job Matches Found"
        message = f"We found {match_count} new job matches for your profile. Check your recommendations!"
        
        notification = self.create_notification(user_id, "match", title, message, send_telegram=False)
        
        # Send Telegram notification with job details
        if user and user.telegram_chat_id and user.telegram_notifications_enabled and top_jobs:
            self.telegram_service.send_job_match_notification(
                user.telegram_chat_id,
                user_name,
                match_count,
                top_jobs
            )
        
        return notification

    def send_application_notification(self, user_id: int, job_title: str, company: str, status: str = "viewed") -> Notification:
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user else "User"
        
        title = "Application Status Update"
        message = f"Your application for {job_title} at {company} has been {status}."
        
        notification = self.create_notification(user_id, "application", title, message, send_telegram=False)
        
        # Send Telegram notification
        if user and user.telegram_chat_id and user.telegram_notifications_enabled:
            self.telegram_service.send_application_status_notification(
                user.telegram_chat_id,
                user_name,
                job_title,
                company,
                status
            )
        
        return notification

    def send_new_job_alert(self, user_id: int, job_count: int, job_types: list = None) -> Notification:
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user else "User"
        
        title = "New Jobs Alert"
        message = f"We found {job_count} new jobs matching your profile!"
        
        notification = self.create_notification(user_id, "job_alert", title, message, send_telegram=False)
        
        # Send Telegram notification
        if user and user.telegram_chat_id and user.telegram_notifications_enabled:
            self.telegram_service.send_new_job_alert(
                user.telegram_chat_id,
                user_name,
                job_count,
                job_types or ["various fields"]
            )
        
        return notification

    def send_daily_job_digest(self, user_id: int, job_count: int, featured_jobs: list = None) -> Notification:
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user else "User"
        
        title = "Daily Job Digest"
        message = f"Your daily digest: {job_count} new jobs available."
        
        notification = self.create_notification(user_id, "digest", title, message, send_telegram=False)
        
        # Send Telegram notification
        if user and user.telegram_chat_id and user.telegram_notifications_enabled:
            self.telegram_service.send_daily_job_digest(
                user.telegram_chat_id,
                user_name,
                job_count,
                featured_jobs or []
            )
        
        return notification

    def enable_telegram_notifications(self, user_id: int, chat_id: str) -> bool:
        """Enable Telegram notifications for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.telegram_chat_id = chat_id
        user.telegram_notifications_enabled = True
        self.db.commit()
        
        # Send welcome message
        self.telegram_service.enable_telegram_notifications(chat_id, user.full_name or "User")
        
        return True

    def disable_telegram_notifications(self, user_id: int) -> bool:
        """Disable Telegram notifications for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.telegram_notifications_enabled = False
        self.db.commit()
        
        return True
