import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


def send_sms(phone: str, message: str) -> bool:
    if not settings.sms_api_key:
        logger.info("SMS provider not configured; SMS to %s skipped", phone)
        return False
    logger.info("Sending SMS to %s: %s", phone, message[:80])
    return True
