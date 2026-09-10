from sqlalchemy.orm import Session

from app.middleware.error_handler import AppError
from app.models.match import Match
from app.models.notification import Notification
from app.models.user import User
from app.notifications.email import send_email
from app.notifications.sms import send_sms


def notify_new_matches(db: Session, user: User, matches: list[Match]) -> None:
    for match in matches:
        job = match.job
        title = f"New job match: {job.title} at {job.company}"
        location = job.location or "location unspecified"
        message = f"Your CV matches {match.score:.0f}% with {job.title} at {job.company} ({location})."
        db.add(Notification(user_id=user.id, job_id=job.id, title=title, message=message, channel="in_app"))
        if send_email(user.email, title, message):
            db.add(Notification(user_id=user.id, job_id=job.id, title=title, message=message, channel="email"))
        if user.phone and send_sms(user.phone, message):
            db.add(Notification(user_id=user.id, job_id=job.id, title=title, message=message, channel="sms"))
    db.commit()


def list_notifications(db: Session, user: User, unread_only: bool = False) -> list[Notification]:
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc(), Notification.id.desc()).all()


def mark_read(db: Session, user: User, notification_id: int) -> Notification:
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if notification is None:
        raise AppError("Notification not found", 404)
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, user: User) -> int:
    query = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False))
    updated = query.update({"is_read": True})
    db.commit()
    return updated
