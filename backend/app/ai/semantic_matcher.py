import json
from typing import Dict, List
from app.models.cv import CV
from app.models.job import Job

class SemanticMatcher:
    def __init__(self):
        # In production, this would load pre-trained ML models
        # For now, we'll use rule-based matching
        pass

    def calculate_match_score(self, cv: CV, job: Job) -> float:
        """
        Calculate a match score between a CV and a job (0-100).
        This is a simplified version - in production, use semantic embeddings.
        """
        score = 0.0
        
        # Parse CV skills if they're stored as JSON
        cv_skills = []
        if cv.skills:
            try:
                cv_skills = json.loads(cv.skills)
            except json.JSONDecodeError:
                cv_skills = []
        
        # Parse job skills if they're stored as JSON
        job_skills = []
        if job.skills:
            try:
                job_skills = json.loads(job.skills)
            except json.JSONDecodeError:
                job_skills = []
        
        # Skill matching (40% weight)
        skill_score = self._calculate_skill_match(cv_skills, job_skills)
        score += skill_score * 0.4
        
        # Experience matching (25% weight)
        experience_score = self._calculate_experience_match(cv, job)
        score += experience_score * 0.25
        
        # Location matching (15% weight)
        location_score = self._calculate_location_match(cv, job)
        score += location_score * 0.15
        
        # Job type matching (10% weight)
        job_type_score = self._calculate_job_type_match(cv, job)
        score += job_type_score * 0.1
        
        # Semantic text matching (10% weight)
        semantic_score = self._calculate_semantic_match(cv, job)
        score += semantic_score * 0.1
        
        return round(score, 2)

    def _calculate_skill_match(self, cv_skills: List[str], job_skills: List[str]) -> float:
        """
        Calculate skill match percentage.
        """
        if not job_skills:
            return 0.5  # Neutral score if no job skills specified
        
        if not cv_skills:
            return 0.0
        
        # Convert to lowercase for comparison
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Count matching skills
        matches = 0
        for job_skill in job_skills_lower:
            if job_skill in cv_skills_lower:
                matches += 1
        
        # Calculate percentage
        match_percentage = matches / len(job_skills) if job_skills else 0
        return match_percentage

    def _calculate_experience_match(self, cv: CV, job: Job) -> float:
        """
        Calculate experience match based on CV text and job requirements.
        """
        # This is simplified - in production, you'd parse years of experience
        if not cv.parsed_text or not job.description:
            return 0.5
        
        cv_text_lower = cv.parsed_text.lower()
        job_desc_lower = job.description.lower()
        
        # Look for experience keywords
        experience_keywords = ["years of experience", "year experience", "worked with"]
        
        match_score = 0.5  # Base score
        
        for keyword in experience_keywords:
            if keyword in cv_text_lower and keyword in job_desc_lower:
                match_score += 0.1
        
        return min(match_score, 1.0)

    def _calculate_location_match(self, cv: CV, job: Job) -> float:
        """
        Calculate location match.
        """
        if not job.location:
            return 1.0  # No location preference
        
        if job.location.lower() in ["remote", "anywhere", "any"]:
            return 1.0  # Remote jobs match everyone
        
        # In production, you'd extract location from CV
        # For now, return neutral score
        return 0.5

    def _calculate_job_type_match(self, cv: CV, job: Job) -> float:
        """
        Calculate job type match.
        """
        if not job.job_type:
            return 1.0  # No preference
        
        # In production, you'd extract preferred job type from CV
        # For now, return neutral score
        return 0.5

    def _calculate_semantic_match(self, cv: CV, job: Job) -> float:
        """
        Calculate semantic similarity between CV and job description.
        This is a simplified version - in production, use embeddings.
        """
        if not cv.parsed_text or not job.description:
            return 0.5
        
        cv_text_lower = cv.parsed_text.lower()
        job_desc_lower = job.description.lower()
        
        # Simple word overlap as a proxy for semantic similarity
        cv_words = set(cv_text_lower.split())
        job_words = set(job_desc_lower.split())
        
        if not job_words:
            return 0.5
        
        overlap = len(cv_words & job_words)
        union = len(cv_words | job_words)
        
        jaccard_similarity = overlap / union if union > 0 else 0
        return jaccard_similarity
