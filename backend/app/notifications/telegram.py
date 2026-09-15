"""
Telegram Notification Service - Send job match notifications via Telegram
"""
import requests
import logging
from typing import Optional
from app.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotificationService:
    def __init__(self):
        self.api_token = settings.TELEGRAM_BOT_TOKEN
        self.telegram_api_url = f"https://api.telegram.org/bot{self.api_token}" if self.api_token else None
    
    def send_telegram_message(self, chat_id: str, message: str) -> bool:
        """
        Send a message to a Telegram user.
        
        Args:
            chat_id: Telegram chat ID of the user
            message: Message to send
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_token:
            logger.warning("Telegram API token not configured")
            return False
        
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Telegram message sent successfully to chat_id: {chat_id}")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_job_match_notification(self, chat_id: str, user_name: str, match_count: int, top_jobs: list) -> bool:
        """
        Send job match notification via Telegram.
        
        Args:
            chat_id: Telegram chat ID of the user
            user_name: Name of the user
            match_count: Number of job matches found
            top_jobs: List of top job matches
        
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"""
🎯 <b>New Job Matches Found!</b>

Hello {user_name},

Great news! We found <b>{match_count}</b> new job matches that align with your profile and skills.

<b>Top Matches:</b>
"""
        
        # Add top 3 jobs
        for i, job in enumerate(top_jobs[:3], 1):
            message += f"\n{i}. <b>{job.get('title', 'Position')}</b> at {job.get('company', 'Company')}"
            message += f"\n   💰 {job.get('salary_min', 0):,.0f} - {job.get('salary_max', 0):,.0f} ETB"
            message += f"\n   📍 {job.get('location', 'Ethiopia')}"
            message += f"\n   🔗 {job.get('source_url', 'Link')}"
            message += "\n"
        
        message += f"""
Log in to your dashboard to view all matches and apply to positions that interest you.

<b>AI Job Matching System</b>
🇪🇹 Ethiopian Job Matching
"""
        
        return self.send_telegram_message(chat_id, message)
    
    def send_application_status_notification(self, chat_id: str, user_name: str, job_title: str, company: str, status: str) -> bool:
        """
        Send application status update via Telegram.
        
        Args:
            chat_id: Telegram chat ID of the user
            user_name: Name of the user
            job_title: Title of the job
            company: Company name
            status: Application status
        
        Returns:
            bool: True if successful, False otherwise
        """
        status_emoji = {
            "pending": "⏳",
            "viewed": "👁",
            "applied": "✅",
            "rejected": "❌",
            "accepted": "🎉"
        }
        
        emoji = status_emoji.get(status, "📋")
        
        message = f"""
📋 <b>Application Status Update</b>

Hello {user_name},

Your application for <b>{job_title}</b> at <b>{company}</b> has been updated.

Status: {emoji} <b>{status.upper()}</b>

Log in to your dashboard for more details and to track your application progress.

<b>AI Job Matching System</b>
🇪🇹 Ethiopian Job Matching
"""
        
        return self.send_telegram_message(chat_id, message)
    
    def send_new_job_alert(self, chat_id: str, user_name: str, job_count: int, job_types: list) -> bool:
        """
        Send alert about new jobs matching user's profile.
        
        Args:
            chat_id: Telegram chat ID of the user
            user_name: Name of the user
            job_count: Number of new jobs
            job_types: List of job types
        
        Returns:
            bool: True if successful, False otherwise
        """
        job_types_str = ", ".join(job_types) if job_types else "various fields"
        
        message = f"""
🆕 <b>New Jobs Alert!</b>

Hello {user_name},

We found <b>{job_count}</b> new jobs that match your profile in {job_types_str}!

Top categories:
• Technology & IT
• Banking & Finance
• Construction & Engineering
• Marketing & Sales
• NGO & Development

Log in to your dashboard to view these opportunities and apply to positions that interest you.

<b>AI Job Matching System</b>
🇪🇹 Ethiopian Job Matching
"""
        
        return self.send_telegram_message(chat_id, message)
    
    def send_daily_job_digest(self, chat_id: str, user_name: str, job_count: int, featured_jobs: list) -> bool:
        """
        Send daily digest of new jobs.
        
        Args:
            chat_id: Telegram chat_id of the user
            user_name: Name of the user
            job_count: Total number of new jobs
            featured_jobs: List of featured jobs
        
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"""
📅 <b>Daily Job Digest</b>

Hello {user_name},

Here's your daily job digest for Ethiopian positions:

<b>New Jobs Today:</b> {job_count}

<b>Featured Opportunities:</b>
"""
        
        for i, job in enumerate(featured_jobs[:5], 1):
            message += f"\n{i}. <b>{job.get('title', 'Position')}</b> - {job.get('company', 'Company')}"
            message += f"\n   💰 {job.get('salary_min', 0):,.0f} - {job.get('salary_max', 0):,.0f} ETB"
        
        message += f"""
Stay tuned for more opportunities tailored to your skills and experience!

<b>AI Job Matching System</b>
🇪🇹 Ethiopian Job Matching
"""
        
        return self.send_telegram_message(chat_id, message)
    
    def enable_telegram_notifications(self, chat_id: str, user_id: int) -> bool:
        """
        Enable Telegram notifications for a user.
        
        Args:
            chat_id: Telegram chat ID of the user
            user_id: User ID in the system
        
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"""
✅ <b>Telegram Notifications Enabled</b>

You have successfully enabled Telegram notifications for job alerts!

You will receive:
• New job matches for your profile
• Application status updates
• Daily job digests
• New job alerts in your preferred categories

We'll send you notifications for jobs that match your skills, experience, and preferences.

To disable notifications, visit your notification settings in the dashboard.

<b>AI Job Matching System</b>
🇪🇹 Ethiopian Job Matching
"""
        
        return self.send_telegram_message(chat_id, message)
    
    def send_welcome_message(self, chat_id: str, user_name: str) -> bool:
        """
        Send welcome message when user connects Telegram.
        
        Args:
            chat_id: Telegram chat_id of the user
            user_name: Name of the user
        
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"""
👋 <b>Welcome to AI Job Matching!</b>

Hello {user_name}!

Welcome to the AI Job Matching System's Telegram notifications. We're excited to help you find your perfect job in Ethiopia!

🇪🇹 <b>Ethiopian Job Market:</b>
• IT & Technology
• Banking & Finance
• Construction & Engineering
• NGO & Development
• Remote Opportunities

<b>What you'll receive:</b>
• Personalized job matches
• Application status updates
• Daily job digests
• Career opportunities

We'll only send you relevant job alerts based on your profile and preferences.

<b>AI Job Matching System</b>
🇪🇹 Ethiopian Job Matching
"""
        
        return self.send_telegram_message(chat_id, message)
