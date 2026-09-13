"""
Duplicate Detector - Detect and remove duplicate job postings
"""
import hashlib

from difflib import SequenceMatcher
from typing import List

class DuplicateDetector:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes = set()
    
    def remove_duplicates(self, jobs: list[dict]) -> list[dict]:
        """Remove duplicate jobs from the list"""
        unique_jobs = []
        seen_signatures = set()
        
        for job in jobs:
            signature = self._generate_job_signature(job)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_jobs.append(job)
            else:
                print(f"Duplicate job found: {job['title']} at {job['company']}")
        
        return unique_jobs
    
    def _generate_job_signature(self, job: dict) -> str:
        """Generate a unique signature for a job"""
        # Create a signature based on key fields
        signature_parts = [
            job.get('title', '').lower().strip(),
            job.get('company', '').lower().strip(),
            job.get('location', '').lower().strip(),
            job.get('job_type', '').lower().strip(),
        ]
        
        signature_string = '|'.join(signature_parts)
        
        # Create hash
        signature_hash = hashlib.md5(signature_string.encode()).hexdigest()
        
        return signature_hash
    
    def find_similar_jobs(self, jobs: list[dict]) -> List[tuple]:
        """Find jobs that are similar but not exact duplicates"""
        similar_pairs = []
        
        for i, job1 in enumerate(jobs):
            for j, job2 in enumerate(jobs[i+1:], i+1):
                similarity = self._calculate_similarity(job1, job2)
                
                if similarity >= self.similarity_threshold:
                    similar_pairs.append((i, j, similarity))
        
        return similar_pairs
    
    def _calculate_similarity(self, job1: dict, job2: dict) -> float:
        """Calculate similarity between two jobs"""
        # Compare title similarity
        title_similarity = self._string_similarity(
            job1.get('title', ''),
            job2.get('title', '')
        )
        
        # Compare company similarity
        company_similarity = self._string_similarity(
            job1.get('company', ''),
            job2.get('company', '')
        )
        
        # Compare description similarity
        description_similarity = self._string_similarity(
            job1.get('description', ''),
            job2.get('description', '')
        )
        
        # Weighted average
        weights = {
            'title': 0.4,
            'company': 0.3,
            'description': 0.3
        }
        
        overall_similarity = (
            title_similarity * weights['title'] +
            company_similarity * weights['company'] +
            description_similarity * weights['description']
        )
        
        return overall_similarity
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher"""
        if not str1 or not str2:
            return 0.0
        
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def group_similar_jobs(self, jobs: list[dict]) -> dict[str, list]:
        """Group similar jobs together"""
        groups = {}
        
        for job in jobs:
            # Create a group key based on company and location
            group_key = f"{job.get('company', '').lower()}_{job.get('location', '').lower()}"
            
            if group_key not in groups:
                groups[group_key] = []
            
            groups[group_key].append(job)
        
        return groups
    
    def merge_duplicate_fields(self, jobs: list[dict]) -> dict:
        """Merge information from duplicate jobs"""
        if not jobs:
            return {}
        
        # Use the first job as base
        merged = jobs[0].copy()
        
        # Merge skills from all duplicates
        all_skills = set()
        for job in jobs:
            if 'skills' in job:
                try:
                    import json
                    skills = json.loads(job['skills'])
                    all_skills.update(skills)
                except:
                    pass
        
        if all_skills:
            import json
            merged['skills'] = json.dumps(list(all_skills))
        
        # Use the highest salary range
        max_salary_min = max(job.get('salary_min', 0) for job in jobs)
        max_salary_max = max(job.get('salary_max', 0) for job in jobs)
        
        merged['salary_min'] = max_salary_min
        merged['salary_max'] = max_salary_max
        
        # Combine sources
        sources = [job.get('source', 'unknown') for job in jobs]
        merged['source'] = ', '.join(set(sources))
        
        return merged
