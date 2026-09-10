import logging
import smtplib
from email.message import EmailMessage

from app.config.settings import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        logger.info("SMTP not configured; email to %s skipped: %s", to, subject)
        return False
    msg = EmailMessage()
    msg["From"] = settings.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        return True
    except OSError as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        return False
