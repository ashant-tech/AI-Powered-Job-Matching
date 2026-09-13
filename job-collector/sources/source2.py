"""
Source 2 - Another job board scraper
"""
import requests

import time

class Source2:
    def __init__(self):
        self.name = "Source2"
        self.base_url = "https://another-job-board.com"
        self.api_key = "your-api-key"  # Configure this
    
    def fetch_jobs(self) -> list[dict]:
        """Fetch jobs from Source2 API"""
        jobs = []
        
        try:
            # Example API call
            # headers = {"Authorization": f"Bearer {self.api_key}"}
            # response = requests.get(f"{self.base_url}/api/jobs", headers=headers)
            # data = response.json()
            
            # Example job data structure
            job_data = {
                "title": "Data Scientist",
                "company": "Data Corp",
                "description": "Looking for experienced data scientist...",
                "requirements": "Machine learning, Python, SQL",
                "skills": ["python", "machine learning", "sql", "data analysis"],
                "location": "New York, NY",
                "salary_min": 100000,
                "salary_max": 150000,
                "job_type": "full-time",
                "source": self.name,
                "source_url": f"{self.base_url}/jobs/456"
            }
            
            jobs.append(job_data)
            
            # Add rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching from Source2: {e}")
        
        return jobs
    
    def fetch_jobs_by_category(self, category: str) -> list[dict]:
        """Fetch jobs by specific category"""
        # Implement category-based fetching
        pass
