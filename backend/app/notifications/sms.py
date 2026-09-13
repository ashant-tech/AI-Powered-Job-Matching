
from app.config.settings import settings

class SMSService:
    def __init__(self):
        self.api_key = settings.SMS_API_KEY

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send an SMS message.
        This is a placeholder - integrate with your SMS provider (Twilio, etc.)
        """
        if not self.api_key:
            print("SMS service not configured")
            return False
        
        try:
            # Example integration with Twilio (would need twilio package)
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone_number
            # )
            
            print(f"SMS sent to {phone_number}: {message}")
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def send_match_notification_sms(
        self,
        phone_number: str,
        match_count: int
    ) -> bool:
        """
        Send SMS notification about new job matches.
        """
        message = f"You have {match_count} new job matches! Check your dashboard for details."
        return self.send_sms(phone_number, message)

    def send_application_status_sms(
        self,
        phone_number: str,
        job_title: str,
        status: str
    ) -> bool:
        """
        Send SMS about application status update.
        """
        message = f"Application status update for {job_title}: {status}"
        return self.send_sms(phone_number, message)
