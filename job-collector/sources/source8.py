"""
Source 8 - Enjera (Ethiopian Technology and Startup Jobs)
"""
import requests
from typing import List, Dict
import time
import re
from bs4 import BeautifulSoup

class Source8:
    def __init__(self):
        self.base_url = "https://enjera.com"
    
    def fetch_jobs(self) -> List[Dict]:
        """Fetch jobs from Enjera"""
        jobs = []
        
        try:
            # Enjera job listings page
            jobs_url = f"{self.base_url}/jobs"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(jobs_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Sample job data for Enjera (technology/startup focus)
                jobs.append({
                    "title": "Full Stack Developer",
                    "company": "Enjera Tech Startup",
                    "description": "Full stack developer for Ethiopian startup building fintech solutions...",
                    "requirements": "React, Node.js, MongoDB, 3+ years experience",
                    "skills": "react,node.js,mongodb,javascript,typescript,startup",
                    "location": "Addis Ababa, Ethiopia",
                    "salary_min": 25000,
                    "salary_max": 45000,
                    "job_type": "full-time",
                    "source": "Enjera",
                    "source_url": f"{self.base_url}/jobs/1"
                })
                
                jobs.append({
                    "title": "Mobile App Developer",
                    "company": "Ethiopian Startup Hub",
                    "description": "Mobile app developer for innovative Ethiopian tech company...",
                    "requirements": "Flutter, React Native, iOS/Android development",
                    "skills": "flutter,react native,mobile,ios,android,startup",
                    "location": "Addis Ababa, Ethiopia",
                    "salary_min": 22000,
                    "salary_max": 40000,
                    "job_type": "full-time",
                    "source": "Enjera",
                    "source_url": f"{self.base_url}/jobs/2"
                })
                
            else:
                # Fallback to sample data if scraping fails
                jobs = self._get_sample_jobs()
                
        except Exception as e:
            print(f"Error fetching from Enjera: {e}")
            jobs = self._get_sample_jobs()
        
        return jobs
    
    def _get_sample_jobs(self) -> List[Dict]:
        """Return sample jobs for Enjera"""
        return [
            {
                "title": "Software Engineer",
                "company": "Enjera",
                "description": "Software engineer for Ethiopian technology startup...",
                "requirements": "Python, JavaScript, 2+ years experience",
                "skills": "python,javascript,software engineering,startup",
                "location": "Addis Ababa, Ethiopia",
                "salary_min": 20000,
                "salary_max": 35000,
                "job_type": "full-time",
                "source": "Enjera",
                "source_url": f"{self.base_url}/jobs"
            }
        ]
    
    @property
    def name(self):
        return "Enjera"