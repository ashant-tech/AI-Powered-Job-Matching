import json
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.notification import Notification
from app.models.job import ExternalJob
from app.models.user import User
from app.notifications.telegram import TelegramNotificationService
from app.services.job_service import JobService

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
        send_telegram: bool = True,
        external_job_ids: Optional[List[str]] = None
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            external_job_ids=json.dumps(external_job_ids) if external_job_ids else None
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
            if user and user.telegram_notifications_enabled:
                # Try to send using chat_id first, then fallback to username
                sent = False
                
                if user.telegram_chat_id:
                    if notification_type == "match":
                        self.telegram_service.send_telegram_message(
                            user.telegram_chat_id,
                            f"🎯 {title}\n\n{message}"
                        )
                        sent = True
                    elif notification_type == "application":
                        self.telegram_service.send_telegram_message(
                            user.telegram_chat_id,
                            f"📋 {title}\n\n{message}"
                        )
                        sent = True
                    else:
                        self.telegram_service.send_telegram_message(
                            user.telegram_chat_id,
                            f"🔔 {title}\n\n{message}"
                        )
                        sent = True
                
                # Fallback to username if chat_id not available or sending failed
                if not sent and user.telegram_username:
                    if notification_type == "match":
                        self.telegram_service.send_telegram_message_by_username(
                            user.telegram_username,
                            f"🎯 {title}\n\n{message}"
                        )
                    elif notification_type == "application":
                        self.telegram_service.send_telegram_message_by_username(
                            user.telegram_username,
                            f"📋 {title}\n\n{message}"
                        )
                    else:
                        self.telegram_service.send_telegram_message_by_username(
                            user.telegram_username,
                            f"🔔 {title}\n\n{message}"
                        )
                        
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")

    def purge_expired_notifications(self, user_id: Optional[int] = None) -> int:
        """Remove or trim notifications whose jobs have expired.

        Deletes match notifications whose jobs are all expired and rebuilds
        messages for partially expired ones. Returns the number deleted.
        """
        JobService(self.db).deactivate_expired_jobs()
        JobService(self.db).purge_expired_matches()

        query = self.db.query(Notification).filter(Notification.external_job_ids.isnot(None))
        if user_id:
            query = query.filter(Notification.user_id == user_id)

        deleted = 0
        for notification in query.all():
            try:
                job_ids = json.loads(notification.external_job_ids or "[]")
            except json.JSONDecodeError:
                job_ids = []

            if not job_ids:
                continue

            active_jobs = self.db.query(ExternalJob).filter(
                ExternalJob.external_id.in_(job_ids),
                ExternalJob.is_active == True  # noqa: E712
            ).all()

            if not active_jobs:
                self.db.delete(notification)
                deleted += 1
            elif len(active_jobs) < len(job_ids):
                notification.external_job_ids = json.dumps([job.external_id for job in active_jobs])
                notification.message = self.build_match_message(active_jobs)

        self.db.commit()
        return deleted

    @staticmethod
    def build_match_message(top_jobs: list) -> str:
        job_details = []
        for i, job in enumerate(top_jobs[:3], 1):
            deadline_part = f" (apply by {job.deadline.strftime('%b %d, %Y')})" if job.deadline else ""
            job_details.append(f"{i}. {job.title} at {job.company}{deadline_part}")

        if len(top_jobs) > 3:
            job_details.append(f"... and {len(top_jobs) - 3} more")

        return (
            f"We found {len(top_jobs)} active job matches for your profile:\n\n"
            + "\n".join(job_details)
            + "\n\nCheck your recommendations for details!"
        )

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        self.purge_expired_notifications(user_id)

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

        if top_jobs:
            message = self.build_match_message(top_jobs)
        else:
            message = f"We found {match_count} new job matches for your profile. Check your recommendations!"

        notification = self.create_notification(
            user_id,
            "match",
            title,
            message,
            send_telegram=False,
            external_job_ids=[job.external_id for job in (top_jobs or [])]
        )
        
        # Send Telegram notification with job details
        if user and user.telegram_notifications_enabled and top_jobs:
            sent = False
            chat_id = None
            
            # Try using chat_id first
            if user.telegram_chat_id:
                chat_id = user.telegram_chat_id
                sent = self.telegram_service.send_job_match_notification(
                    chat_id,
                    user_name,
                    match_count,
                    top_jobs
                )
            
            # Fallback to username if chat_id not available or sending failed
            if not sent and user.telegram_username:
                chat_id = self.telegram_service.get_chat_id_from_username(user.telegram_username)
                if chat_id:
                    sent = self.telegram_service.send_job_match_notification(
                        chat_id,
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
        if user and user.telegram_notifications_enabled:
            chat_id = user.telegram_chat_id
            
            # Fallback to username if chat_id not available
            if not chat_id and user.telegram_username:
                chat_id = self.telegram_service.get_chat_id_from_username(user.telegram_username)
            
            if chat_id:
                self.telegram_service.send_application_status_notification(
                    chat_id,
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
        if user and user.telegram_notifications_enabled:
            chat_id = user.telegram_chat_id
            
            # Fallback to username if chat_id not available
            if not chat_id and user.telegram_username:
                chat_id = self.telegram_service.get_chat_id_from_username(user.telegram_username)
            
            if chat_id:
                self.telegram_service.send_new_job_alert(
                    chat_id,
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
        if user and user.telegram_notifications_enabled:
            chat_id = user.telegram_chat_id
            
            # Fallback to username if chat_id not available
            if not chat_id and user.telegram_username:
                chat_id = self.telegram_service.get_chat_id_from_username(user.telegram_username)
            
            if chat_id:
                self.telegram_service.send_daily_job_digest(
                    chat_id,
                    user_name,
                    job_count,
                    featured_jobs or []
                )
        
        return notification

    def enable_telegram_notifications(self, user_id: int, chat_id: str = None, username: str = None) -> bool:
        """Enable Telegram notifications for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if chat_id:
            user.telegram_chat_id = chat_id
        if username:
            user.telegram_username = username
            
        user.telegram_notifications_enabled = True
        self.db.commit()
        
        # Send welcome message
        target_chat_id = chat_id
        if not target_chat_id and username:
            target_chat_id = self.telegram_service.get_chat_id_from_username(username)
        
        if target_chat_id:
            self.telegram_service.enable_telegram_notifications(target_chat_id, user.full_name or "User")
        
        return True

    def disable_telegram_notifications(self, user_id: int) -> bool:
        """Disable Telegram notifications for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.telegram_notifications_enabled = False
        self.db.commit()
        
        return True
