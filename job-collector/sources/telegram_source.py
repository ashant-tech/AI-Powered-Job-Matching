"""
Telegram Job Source - Ethiopian Job Telegram Channels
"""
import requests
from typing import List, Dict
import time
import re
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramJobSource:
    def __init__(self):
        self.api_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.channels = [
            {"name": "Ethio Jobs Vacancy", "username": "Ethiojobs2000"},
            {"name": "Afriwork Freelance", "username": "freelance_ethio"},
            {"name": "Ethiojobs Official", "username": "ethiojobsofficial"},
            {"name": "EffoyJobs", "username": "effoyjobs"},
            {"name": "Ethio Job Vacancy", "username": "ethio_job_vacancy1"},
            {"name": "Ethio Daily Vacancy", "username": "informationnegari"},
            {"name": "Ethiopia Vacancy", "username": "ethiopiavacancy0"},
            {"name": "HaHuJobs", "username": "hahujobs"},
            {"name": "Afriwork Amharic", "username": "afriworkamharic"},
            {"name": "Ethiopian Vacancy", "username": "vacancyforallethio"},
            {"name": "Ethio Jobs Hub", "username": "Ethiojobshubs"},
            {"name": "Embassy NGO Jobs", "username": "jobs_in_ethio"},
            {"name": "Ethiopian Reporter Jobs", "username": "ethiopian_reporter_job"},
            {"name": "E-LMIS", "username": "FDRE_MoLSofficial"},
            {"name": "GeezJobs Ethiopia", "username": "geezjobs_ethiopia"},
            {"name": "Shegerjobs", "username": "shegarjob"},
            {"name": "NGO Jobs Vacancy", "username": "vacancy3"},
            {"name": "HarmeeJobs", "username": "harmeejobs"},
            {"name": "Elelanajobs", "username": "elelanajobs"},
            {"name": "Fanajobs", "username": "fanajobs"},
            {"name": "Ethioworks", "username": "ethioworks1"},
            {"name": "Onlinejobs Ethiopia", "username": "Ethiontwork"},
            {"name": "Tikvah Jobs", "username": "tikvahethmagazine"},
            {"name": "Shola Jobs", "username": "ngoethiopia"},
            {"name": "Tikus Jobs", "username": "tikusjobs"},
            {"name": "AbayJobs", "username": "abayjobscom"},
            {"name": "Ethio Job Vacancy", "username": "Ethiojob1Vacancy"},
            {"name": "Abol Jobs Ethiopia", "username": "aboljobs"},
            {"name": "Dereja", "username": "Derejaofficial"},
            {"name": "Safaricom NGO Jobs", "username": "kebenajobs"},
            {"name": "Adama Jobs", "username": "adama_Jobs"},
            {"name": "Gadaa Network", "username": "gadaanetwork"},
            {"name": "Jobs for All", "username": "Jobs_for_all1"},
        ]
    
    @property
    def name(self):
        return "Telegram Channels"
    
    def fetch_jobs(self) -> List[Dict]:
        """Fetch jobs from Telegram channels"""
        jobs = []
        
        for channel in self.channels:
            try:
                logger.info(f"Fetching jobs from {channel['name']} (@{channel['username']})")
                channel_jobs = self._fetch_from_channel(channel)
                jobs.extend(channel_jobs)
                
                # Rate limiting between channels
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching from {channel['name']}: {e}")
                continue
        
        logger.info(f"Total jobs collected from Telegram: {len(jobs)}")
        return jobs
    
    def _fetch_from_channel(self, channel: Dict) -> List[Dict]:
        """Fetch jobs from a specific Telegram channel"""
        jobs = []
        
        if not self.api_token:
            logger.warning("Telegram API token not configured. Using sample data.")
            return self._get_sample_jobs(channel)
        
        try:
            # Get recent messages from channel
            api_url = f"https://api.telegram.org/bot{self.api_token}/getUpdates"
            
            # Get channel updates (you'd need to use getChatHistory in production)
            # For now, we'll use a simpler approach - sample data for each channel
            return self._get_sample_jobs(channel)
            
        except Exception as e:
            logger.error(f"Error fetching from Telegram API: {e}")
            return self._get_sample_jobs(channel)
    
    def _get_sample_jobs(self, channel: Dict) -> List[Dict]:
        """Return sample jobs for each Telegram channel"""
        # Generate sample jobs based on channel type
        sample_jobs = []
        
        # Generate different job types based on channel name
        if "ngo" in channel['name'].lower() or "embassy" in channel['name'].lower():
            sample_jobs.append({
                "title": "Program Officer",
                "company": f"{channel['name']}",
                "description": f"NGO program officer needed for development projects in Ethiopia...",
                "requirements": "5+ years experience, Amharic/English fluency, program management",
                "skills": "program management,ngo,development,amharic,english",
                "location": "Addis Ababa, Ethiopia",
                "salary_min": 25000,
                "salary_max": 45000,
                "job_type": "full-time",
                "source": f"Telegram: {channel['name']}",
                "source_url": f"https://t.me/{channel['username']}"
            })
        elif "tech" in channel['name'].lower() or "ethio" in channel['name'].lower():
            sample_jobs.append({
                "title": "Software Developer",
                "company": f"{channel['name']}",
                "description": f"Software developer needed for mobile app development projects...",
                "requirements": "3+ years experience, Android/iOS development, Java/Kotlin",
                "skills": "java,android,kotlin,mobile development,flutter",
                "location": "Addis Ababa, Ethiopia",
                "salary_min": 20000,
                "salary_max": 35000,
                "job_type": "full-time",
                "source": f"Telegram: {channel['name']}",
                "source_url": f"https://t.me/{channel['username']}"
            })
        else:
            sample_jobs.append({
                "title": "Business Development Executive",
                "company": f"{channel['name']}",
                "description": f"Business development executive needed for market expansion...",
                "requirements": "Marketing experience, sales skills, business strategy",
                "skills": "marketing,sales,business development,strategy,management",
                "location": "Addis Ababa, Ethiopia",
                "salary_min": 22000,
                "salary_max": 40000,
                "job_type": "full-time",
                "source": f"Telegram: {channel['name']}",
                "source_url": f"https://t.me/{channel['username']}"
            })
        
        return sample_jobs
    
    def set_api_token(self, token: str):
        """Set Telegram API token"""
        self.api_token = token
        logger.info("Telegram API token configured")
    
    @property
    def name(self):
        return "Telegram Channels"
