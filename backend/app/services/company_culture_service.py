"""
Company Culture Matching Service

Analyzes company culture from job descriptions and matches with user's work style preferences
to predict cultural fit and job satisfaction.
"""
from typing import List, Dict, Optional
from app.models.job import ExternalJob
from app.models.user import User


# Culture indicators in job descriptions
CULTURE_INDICATORS = {
    "collaborative": {
        "keywords": ["team", "collaborative", "together", "teamwork", "cooperation", "joint", "shared", "group"],
        "description": "Emphasizes teamwork and collaboration"
    },
    "innovative": {
        "keywords": ["innovative", "cutting-edge", "pioneer", "breakthrough", "disruptive", "creative", "innovation", "experimental"],
        "description": "Focuses on innovation and creativity"
    },
    "structured": {
        "keywords": ["structured", "process", "procedure", "organized", "systematic", "methodical", "disciplined", "routine"],
        "description": "Emphasizes structure and processes"
    },
    "fast_paced": {
        "keywords": ["fast-paced", "agile", "rapid", "dynamic", "quick", "fast", "accelerated", "deadline-driven"],
        "description": "Fast-moving, deadline-driven environment"
    },
    "flexible": {
        "keywords": ["flexible", "work-life balance", "remote", "hybrid", "adaptability", "versatile", "accommodating"],
        "description": "Emphasizes flexibility and work-life balance"
    },
    "hierarchical": {
        "keywords": ["hierarchy", "management", "supervisor", "chain of command", "authority", "leadership", "seniority"],
        "description": "Traditional hierarchical structure"
    },
    "flat": {
        "keywords": ["flat", "autonomous", "self-directed", "empowered", "ownership", "initiative", "minimal hierarchy"],
        "description": "Flat organizational structure with autonomy"
    },
    "customer_focused": {
        "keywords": ["customer", "client", "service", "satisfaction", "customer-centric", "client-focused", "user experience"],
        "description": "Strong focus on customer satisfaction"
    },
    "data_driven": {
        "keywords": ["data-driven", "analytics", "metrics", "kpi", "measurement", "quantitative", "evidence-based"],
        "description": "Decisions based on data and metrics"
    },
    "learning_oriented": {
        "keywords": ["learning", "growth", "development", "training", "education", "mentorship", "continuous improvement"],
        "description": "Emphasizes learning and development"
    }
}


# Work style preferences (would come from user profile)
WORK_STYLES = {
    "collaborative": "I prefer working in teams and collaborating with others",
    "independent": "I prefer working independently with minimal supervision",
    "structured": "I prefer clear processes and structured environments",
    "flexible": "I prefer flexible environments with autonomy",
    "fast_paced": "I thrive in fast-paced, dynamic environments",
    "steady": "I prefer steady, predictable work environments",
    "leadership": "I enjoy leadership and mentoring roles",
    "specialist": "I prefer deep technical work and specialization"
}


class CompanyCultureService:
    """Service for analyzing company culture and matching with user preferences."""
    
    def __init__(self):
        self.culture_indicators = CULTURE_INDICATORS
        self.work_styles = WORK_STYLES
    
    def analyze_company_culture(self, job: ExternalJob) -> Dict:
        """Analyze company culture from job description and requirements."""
        if not job:
            return {"error": "No job data available"}
        
        # Combine all text sources
        text_sources = []
        if job.description:
            text_sources.append(job.description)
        if job.requirements:
            text_sources.append(job.requirements)
        if job.company:
            text_sources.append(job.company)
        
        combined_text = " ".join(text_sources).lower()
        
        # Analyze culture indicators
        detected_cultures = []
        for culture_type, data in self.culture_indicators.items():
            keyword_count = sum(1 for keyword in data["keywords"] if keyword in combined_text)
            if keyword_count > 0:
                detected_cultures.append({
                    "type": culture_type,
                    "score": keyword_count,
                    "description": data["description"]
                })
        
        # Sort by score and return top matches
        detected_cultures.sort(key=lambda x: x["score"], reverse=True)
        
        # Determine overall culture profile
        if len(detected_cultures) >= 2:
            primary_culture = detected_cultures[0]["type"]
            secondary_culture = detected_cultures[1]["type"]
        elif len(detected_cultures) == 1:
            primary_culture = detected_cultures[0]["type"]
            secondary_culture = None
        else:
            primary_culture = "balanced"
            secondary_culture = None
        
        return {
            "primary_culture": primary_culture,
            "secondary_culture": secondary_culture,
            "detected_cultures": detected_cultures[:5],  # Top 5
            "culture_profile": self._generate_culture_profile(detected_cultures),
            "work_environment": self._assess_work_environment(detected_cultures)
        }
    
    def _generate_culture_profile(self, detected_cultures: List[Dict]) -> str:
        """Generate a human-readable culture profile."""
        if not detected_cultures:
            return "Balanced and traditional work environment"
        
        culture_types = [c["type"] for c in detected_cultures[:3]]
        
        profiles = {
            "collaborative": "Team-oriented, collaborative environment",
            "innovative": "Innovation-focused, creative environment",
            "structured": "Process-driven, organized environment",
            "fast_paced": "Dynamic, fast-moving environment",
            "flexible": "Flexible, autonomy-focused environment",
            "hierarchical": "Traditional, structured organization",
            "flat": "Flat, autonomous organization",
            "customer_focused": "Customer-centric environment",
            "data_driven": "Data-driven, analytical environment",
            "learning_oriented": "Growth-focused, learning environment"
        }
        
        profile_parts = [profiles.get(ct, ct) for ct in culture_types if ct in profiles]
        return ", ".join(profile_parts) if profile_parts else "Balanced work environment"
    
    def _assess_work_environment(self, detected_cultures: List[Dict]) -> Dict:
        """Assess the overall work environment characteristics."""
        culture_types = [c["type"] for c in detected_cultures]
        
        environment = {
            "pace": "moderate",
            "structure": "balanced",
            "collaboration": "moderate",
            "innovation": "moderate",
            "flexibility": "moderate"
        }
        
        # Assess pace
        if "fast_paced" in culture_types:
            environment["pace"] = "fast"
        elif "structured" in culture_types:
            environment["pace"] = "steady"
        
        # Assess structure
        if "structured" in culture_types or "hierarchical" in culture_types:
            environment["structure"] = "high"
        elif "flat" in culture_types or "flexible" in culture_types:
            environment["structure"] = "low"
        
        # Assess collaboration
        if "collaborative" in culture_types:
            environment["collaboration"] = "high"
        elif "independent" in culture_types:
            environment["collaboration"] = "low"
        
        # Assess innovation
        if "innovative" in culture_types:
            environment["innovation"] = "high"
        
        # Assess flexibility
        if "flexible" in culture_types:
            environment["flexibility"] = "high"
        elif "structured" in culture_types:
            environment["flexibility"] = "low"
        
        return environment
    
    def match_culture_fit(self, job: ExternalJob, user_work_style: str) -> Dict:
        """Match company culture with user's work style preferences."""
        if not job:
            return {"error": "No job data available"}
        
        # Analyze company culture
        company_culture = self.analyze_company_culture(job)
        
        # Map work style to culture preferences
        style_mapping = {
            "collaborative": ["collaborative", "teamwork"],
            "independent": ["flat", "autonomous"],
            "structured": ["structured", "hierarchical"],
            "flexible": ["flexible", "flat"],
            "fast_paced": ["fast_paced", "dynamic"],
            "steady": ["structured", "balanced"],
            "leadership": ["hierarchical", "flat"],
            "specialist": ["data_driven", "structured"]
        }
        
        preferred_cultures = style_mapping.get(user_work_style, ["balanced"])
        
        # Calculate fit score
        detected_types = [c["type"] for c in company_culture["detected_cultures"]]
        matches = sum(1 for pref in preferred_cultures if any(pref in det for det in detected_types))
        
        fit_score = int((matches / max(len(preferred_cultures), 1)) * 100)
        
        # Generate fit analysis
        fit_analysis = self._generate_fit_analysis(fit_score, company_culture, user_work_style)
        
        return {
            "company_culture": company_culture,
            "user_work_style": user_work_style,
            "fit_score": fit_score,
            "fit_rating": self._get_fit_rating(fit_score),
            "fit_analysis": fit_analysis,
            "recommendations": self._get_culture_recommendations(fit_score, company_culture, user_work_style)
        }
    
    def _generate_fit_analysis(self, fit_score: int, company_culture: Dict, user_work_style: str) -> str:
        """Generate analysis of the culture fit."""
        if fit_score >= 80:
            return f"Excellent cultural fit! Your {user_work_style} work style aligns well with {company_culture['company']}'s {company_culture['primary_culture']} culture."
        elif fit_score >= 60:
            return f"Good cultural fit. Your {user_work_style} work style is compatible with {company_culture['company']}'s culture, though there may be some areas to adjust to."
        elif fit_score >= 40:
            return f"Moderate cultural fit. Your {user_work_style} work style differs somewhat from {company_culture['company']}'s culture. Consider if you're comfortable with the differences."
        else:
            return f"Low cultural fit. Your {user_work_style} work style may not align well with {company_culture['company']}'s culture. This could impact job satisfaction."
    
    def _get_fit_rating(self, score: int) -> str:
        """Get rating based on fit score."""
        if score >= 80:
            return "Excellent Fit"
        elif score >= 60:
            return "Good Fit"
        elif score >= 40:
            return "Moderate Fit"
        else:
            return "Poor Fit"
    
    def _get_culture_recommendations(self, fit_score: int, company_culture: Dict, user_work_style: str) -> List[str]:
        """Get recommendations based on culture fit analysis."""
        recommendations = []
        
        if fit_score >= 80:
            recommendations.append("The culture aligns well with your preferences - focus on showcasing your cultural fit in interviews")
        elif fit_score >= 60:
            recommendations.append("Highlight your adaptability and ability to work in different environments")
            recommendations.append("Ask specific questions about team dynamics and work style during interviews")
        else:
            recommendations.append("Consider whether the cultural differences are acceptable for you")
            recommendations.append("Prepare to discuss how you adapt to different work environments")
            recommendations.append("Ask detailed questions about day-to-day work culture and team dynamics")
        
        # Culture-specific recommendations
        if company_culture["primary_culture"] == "fast_paced":
            recommendations.append("Be prepared to discuss how you handle tight deadlines and rapid changes")
        elif company_culture["primary_culture"] == "structured":
            recommendations.append("Highlight your organizational skills and attention to process")
        elif company_culture["primary_culture"] == "collaborative":
            recommendations.append("Emphasize your teamwork and collaboration experiences")
        elif company_culture["primary_culture"] == "innovative":
            recommendations.append("Share examples of creative problem-solving and innovation")
        
        return recommendations[:5]
    
    def get_culture_comparison(self, jobs: List[ExternalJob], user_work_style: str) -> List[Dict]:
        """Compare culture fit across multiple jobs."""
        comparisons = []
        
        for job in jobs:
            culture_match = self.match_culture_fit(job, user_work_style)
            comparisons.append({
                "job_id": job.external_id,
                "job_title": job.title,
                "company": job.company,
                "fit_score": culture_match["fit_score"],
                "fit_rating": culture_match["fit_rating"],
                "primary_culture": culture_match["company_culture"]["primary_culture"],
                "recommendation": culture_match["fit_analysis"]
            })
        
        # Sort by fit score
        comparisons.sort(key=lambda x: x["fit_score"], reverse=True)
        
        return comparisons
