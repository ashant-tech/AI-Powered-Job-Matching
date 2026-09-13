"""
Job Cleaner - Clean and normalize job data
"""
import re

from datetime import datetime

class JobCleaner:
    def __init__(self):
        self.required_fields = ['title', 'company', 'description']
    
    def clean_jobs(self, jobs: list[dict]) -> list[dict]:
        """Clean and normalize a list of jobs"""
        cleaned_jobs = []
        
        for job in jobs:
            try:
                cleaned_job = self.clean_job(job)
                if cleaned_job:
                    cleaned_jobs.append(cleaned_job)
            except Exception as e:
                print(f"Error cleaning job: {e}")
        
        return cleaned_jobs
    
    def clean_job(self, job: dict) -> dict:
        """Clean and normalize a single job"""
        # Check required fields
        if not all(field in job for field in self.required_fields):
            print(f"Job missing required fields: {job.get('title', 'Unknown')}")
            return None
        
        cleaned = {}
        
        # Clean title
        cleaned['title'] = self.clean_text(job['title'])
        
        # Clean company
        cleaned['company'] = self.clean_text(job['company'])
        
        # Clean description
        cleaned['description'] = self.clean_text(job['description'])
        
        # Clean requirements
        if 'requirements' in job:
            cleaned['requirements'] = self.clean_text(job['requirements'])
        
        # Clean and normalize skills
        if 'skills' in job:
            cleaned['skills'] = self.clean_skills(job['skills'])
        
        # Clean location
        if 'location' in job:
            cleaned['location'] = self.clean_location(job['location'])
        
        # Clean salary
        if 'salary_min' in job:
            cleaned['salary_min'] = self.clean_salary(job['salary_min'])
        if 'salary_max' in job:
            cleaned['salary_max'] = self.clean_salary(job['salary_max'])
        
        # Normalize job type
        if 'job_type' in job:
            cleaned['job_type'] = self.normalize_job_type(job['job_type'])
        
        # Keep source information
        cleaned['source'] = job.get('source', 'unknown')
        cleaned['source_url'] = job.get('source_url', '')
        
        # Set default values
        cleaned['is_active'] = True
        cleaned['created_at'] = datetime.utcnow().isoformat()
        
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\.\,\@\/\#\$\%]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def clean_skills(self, skills) -> str:
        """Clean and normalize skills list"""
        if isinstance(skills, str):
            # If skills is a string, try to parse it
            skills = [skill.strip() for skill in skills.split(',')]
        
        if not isinstance(skills, list):
            return "[]"
        
        # Clean each skill
        cleaned_skills = []
        for skill in skills:
            if isinstance(skill, str):
                cleaned_skill = skill.strip().lower()
                if cleaned_skill:
                    cleaned_skills.append(cleaned_skill)
        
        # Remove duplicates and sort
        cleaned_skills = list(set(cleaned_skills))
        cleaned_skills.sort()
        
        import json
        return json.dumps(cleaned_skills)
    
    def clean_location(self, location: str) -> str:
        """Clean and normalize location"""
        if not location:
            return ""
        
        location = location.strip()
        
        # Normalize common location formats
        location = re.sub(r'\s*,\s*', ', ', location)
        location = re.sub(r'\s+', ' ', location)
        
        return location
    
    def clean_salary(self, salary) -> float:
        """Clean and normalize salary"""
        if isinstance(salary, (int, float)):
            return float(salary)
        
        if isinstance(salary, str):
            # Remove currency symbols and commas
            salary = re.sub(r'[^\d.]', '', salary)
            try:
                return float(salary)
            except ValueError:
                return 0.0
        
        return 0.0
    
    def normalize_job_type(self, job_type: str) -> str:
        """Normalize job type"""
        if not job_type:
            return ""
        
        job_type = job_type.strip().lower()
        
        # Map common variations
        type_mapping = {
            'full time': 'full-time',
            'full-time': 'full-time',
            'part time': 'part-time',
            'part-time': 'part-time',
            'contract': 'contract',
            'freelance': 'contract',
            'remote': 'remote',
            'work from home': 'remote',
            'wfh': 'remote',
        }
        
        return type_mapping.get(job_type, job_type)
