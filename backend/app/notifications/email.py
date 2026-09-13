import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config.settings import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: str | None = None
    ) -> bool:
        """
        Send an email using SMTP.
        """
        if not self.smtp_host or not self.smtp_user:
            print("Email service not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_match_notification_email(
        self,
        to_email: str,
        user_name: str,
        match_count: int
    ) -> bool:
        """
        Send email notification about new job matches.
        """
        subject = f"New Job Matches Found - {match_count} Opportunities"
        
        body = f"""
Hi {user_name},

Great news! We found {match_count} new job matches that align with your profile and skills.

Log in to your dashboard to view these opportunities and apply:

[Dashboard Link]

Best regards,
The AI Job Matching Team
        """
        
        html_body = f"""
<html>
<body>
    <h2>New Job Matches Found</h2>
    <p>Hi {user_name},</p>
    <p>Great news! We found <strong>{match_count}</strong> new job matches that align with your profile and skills.</p>
    <p>Log in to your dashboard to view these opportunities and apply.</p>
    <p>Best regards,<br>The AI Job Matching Team</p>
</body>
</html>
        """
        
        return self.send_email(to_email, subject, body, html_body)

    def send_application_status_email(
        self,
        to_email: str,
        user_name: str,
        job_title: str,
        company: str,
        status: str
    ) -> bool:
        """
        Send email about application status update.
        """
        subject = f"Application Status Update - {job_title} at {company}"
        
        body = f"""
Hi {user_name},

Your application for {job_title} at {company} has been updated.

Status: {status}

Log in to your dashboard for more details.

Best regards,
The AI Job Matching Team
        """
        
        return self.send_email(to_email, subject, body)
