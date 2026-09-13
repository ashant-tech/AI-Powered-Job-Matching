"""
Source 1 - Example job board scraper
"""
import requests
from bs4 import BeautifulSoup

import time

class Source1:
    def __init__(self):
        self.name = "Source1"
        self.base_url = "https://example-job-board.com"
    
    def fetch_jobs(self) -> list[dict]:
        """Fetch jobs from Source1"""
        jobs = []
        
        try:
            # This is a placeholder - implement actual scraping logic
            # response = requests.get(f"{self.base_url}/jobs")
            # soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example job data structure
            job_data = {
                "title": "Senior Software Engineer",
                "company": "Tech Company Inc",
                "description": "We are looking for a senior software engineer...",
                "requirements": "5+ years experience, Python, JavaScript",
                "skills": ["python", "javascript", "react"],
                "location": "San Francisco, CA",
                "salary_min": 120000,
                "salary_max": 180000,
                "job_type": "full-time",
                "source": self.name,
                "source_url": f"{self.base_url}/job/123"
            }
            
            jobs.append(job_data)
            
            # Add rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching from Source1: {e}")
        
        return jobs
    
    def parse_job_page(self, url: str) -> dict:
        """Parse individual job page"""
        # Implement detailed job page parsing
        pass
