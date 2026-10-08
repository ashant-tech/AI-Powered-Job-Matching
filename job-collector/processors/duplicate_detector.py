"""
Duplicate Detector - Detect and remove duplicate job postings
"""
import hashlib
import re
import os
import sys
from urllib.parse import urlsplit, urlunsplit

from difflib import SequenceMatcher
from typing import List

# The collector shares deduplication rules with the backend ingestion service.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.job_deduplication import are_duplicate_jobs


class DuplicateDetector:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes = set()
    
    def remove_duplicates(self, jobs: list[dict]) -> list[dict]:
        """Remove duplicate jobs from the list"""
        unique_jobs = []
        seen_signatures = set()
        
        for job in jobs:
            signatures = self._generate_job_signatures(job)
            
            duplicate_index = next(
                (index for index, existing in enumerate(unique_jobs) if are_duplicate_jobs(job, existing)),
                None,
            )
            if seen_signatures.isdisjoint(signatures) and duplicate_index is None:
                seen_signatures.update(signatures)
                unique_jobs.append(job)
            else:
                print(f"Duplicate job found: {job['title']} at {job['company']}")
                if duplicate_index is not None and self._record_quality(job) > self._record_quality(unique_jobs[duplicate_index]):
                    unique_jobs[duplicate_index] = job
        
        return unique_jobs

    @staticmethod
    def _record_quality(job: dict) -> int:
        apply_url = job.get('apply_url') or job.get('source_url') or job.get('url') or ''
        source = str(job.get('source') or '').lower()
        direct_link = bool(apply_url) and 't.me/' not in apply_url.lower()
        return (
            (100 if direct_link else 0)
            + min(len(str(job.get('description') or '')), 4000)
            + min(len(str(job.get('requirements') or '')), 1000)
            + min(len(str(job.get('skills') or '')), 500)
            + (50 if 'telegram' not in source else 0)
        )
    
    def _generate_job_signature(self, job: dict) -> str:
        """Generate a unique signature for a job"""
        return '|'.join(self._generate_job_signatures(job))

    def _generate_job_signatures(self, job: dict) -> set[str]:
        source_url = job.get('source_url') or job.get('apply_url') or job.get('url')
        external_id = job.get('external_id')
        signatures = set()
        if external_id:
            signatures.add(f"external:{external_id.strip().lower()}")
        if source_url:
            signatures.add(f"url:{self._normalize_url(source_url)}")

        # Company is omitted because copied listings often use the channel
        # name on one source and the employer name on another.
        content = '|'.join([
            self._normalize_text(job.get('title', '')),
            self._normalize_text(job.get('location', '')),
            self._normalize_text(job.get('description', '')),
        ])
        signatures.add(f"content:{hashlib.md5(content.encode()).hexdigest()}")
        return signatures

    @staticmethod
    def _normalize_text(value: str) -> str:
        return re.sub(r'\s+', ' ', str(value).lower()).strip()

    @staticmethod
    def _normalize_url(value: str) -> str:
        parsed = urlsplit(str(value).strip())
        return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip('/'), '', ''))
    
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
