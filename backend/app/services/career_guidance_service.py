"""
Career Path Guidance Service

Provides intelligent career progression guidance based on user's current profile,
skills, and experience level. Helps users understand steps needed to progress
toward their desired careers.
"""
from typing import List, Dict, Optional
from app.models.user import User
from app.models.cv import CV
from app.services.field_classifier import normalize_department


# Career progression paths for different fields
CAREER_PATHS = {
    "computer_it": {
        "entry_level": {
            "title": "Junior Developer/IT Support",
            "skills": ["python", "javascript", "basic networking", "problem solving"],
            "next_step": "mid_level",
            "requirements": ["1-2 years experience", "basic project completion", "team collaboration"],
            "learning_resources": [
                "Complete Python/JavaScript fundamentals",
                "Build 2-3 portfolio projects",
                "Learn basic Git and version control",
                "Get familiar with cloud platforms (AWS/Azure)"
            ]
        },
        "mid_level": {
            "title": "Software Engineer/DevOps Engineer",
            "skills": ["software development", "cloud computing", "database management", "api development"],
            "next_step": "senior_level",
            "requirements": ["3-5 years experience", "full-stack development", "system design"],
            "learning_resources": [
                "Master a backend framework (Django/Node.js)",
                "Learn containerization (Docker/Kubernetes)",
                "Study system design patterns",
                "Contribute to open source projects"
            ]
        },
        "senior_level": {
            "title": "Senior Software Engineer/Architect",
            "skills": ["system architecture", "leadership", "mentoring", "advanced cloud"],
            "next_step": "executive_level",
            "requirements": ["5+ years experience", "team leadership", "architecture design"],
            "learning_resources": [
                "Develop leadership and mentoring skills",
                "Master microservices architecture",
                "Learn advanced DevOps and CI/CD",
                "Study enterprise patterns and scalability"
            ]
        },
        "executive_level": {
            "title": "Engineering Manager/CTO",
            "skills": ["strategic planning", "team management", "business acumen", "technical leadership"],
            "next_step": None,
            "requirements": ["8+ years experience", "management experience", "strategic thinking"],
            "learning_resources": [
                "Develop business and financial acumen",
                "Master team management and hiring",
                "Learn strategic planning and execution",
                "Study organizational psychology"
            ]
        }
    },
    "engineering": {
        "entry_level": {
            "title": "Junior Engineer",
            "skills": ["cad", "technical drawing", "basic engineering principles"],
            "next_step": "mid_level",
            "requirements": ["1-2 years experience", "technical software proficiency"],
            "learning_resources": [
                "Master CAD software (AutoCAD, SolidWorks)",
                "Get engineering certification (FE exam)",
                "Learn project management basics",
                "Understand industry standards and codes"
            ]
        },
        "mid_level": {
            "title": "Engineer/Project Engineer",
            "skills": ["project management", "advanced design", "quality control"],
            "next_step": "senior_level",
            "requirements": ["3-5 years experience", "project leadership"],
            "learning_resources": [
                "Get professional engineering license (PE)",
                "Master project management (PMP)",
                "Learn advanced engineering software",
                "Develop client communication skills"
            ]
        },
        "senior_level": {
            "title": "Senior Engineer/Lead Engineer",
            "skills": ["team leadership", "complex design", "client management"],
            "next_step": "executive_level",
            "requirements": ["5+ years experience", "team management"],
            "learning_resources": [
                "Develop leadership and mentoring skills",
                "Master complex project management",
                "Learn business development",
                "Study contract and proposal writing"
            ]
        },
        "executive_level": {
            "title": "Engineering Manager/Director",
            "skills": ["strategic planning", "business development", "organizational leadership"],
            "next_step": None,
            "requirements": ["8+ years experience", "management experience"],
            "learning_resources": [
                "Develop strategic business planning",
                "Master organizational leadership",
                "Learn financial management",
                "Study industry regulations and compliance"
            ]
        }
    },
    "health": {
        "entry_level": {
            "title": "Junior Healthcare Professional",
            "skills": ["basic patient care", "medical terminology", "clinical procedures"],
            "next_step": "mid_level",
            "requirements": ["1-2 years experience", "certification/licensure"],
            "learning_resources": [
                "Complete required certifications",
                "Master clinical procedures",
                "Develop patient communication skills",
                "Learn electronic health record systems"
            ]
        },
        "mid_level": {
            "title": "Healthcare Professional/Specialist",
            "skills": ["specialized care", "patient assessment", "treatment planning"],
            "next_step": "senior_level",
            "requirements": ["3-5 years experience", "specialization"],
            "learning_resources": [
                "Get specialized certification",
                "Master advanced clinical skills",
                "Develop research capabilities",
                "Learn healthcare management"
            ]
        },
        "senior_level": {
            "title": "Senior Specialist/Department Head",
            "skills": ["leadership", "quality improvement", "mentorship"],
            "next_step": "executive_level",
            "requirements": ["5+ years experience", "leadership experience"],
            "learning_resources": [
                "Develop leadership and management skills",
                "Master quality improvement methodologies",
                "Learn healthcare administration",
                "Develop teaching and mentoring abilities"
            ]
        },
        "executive_level": {
            "title": "Healthcare Director/Chief Medical Officer",
            "skills": ["strategic planning", "healthcare administration", "policy development"],
            "next_step": None,
            "requirements": ["8+ years experience", "administrative experience"],
            "learning_resources": [
                "Master healthcare administration",
                "Develop strategic planning skills",
                "Learn policy and regulatory compliance",
                "Study healthcare economics"
            ]
        }
    },
    "business_finance": {
        "entry_level": {
            "title": "Junior Analyst/Associate",
            "skills": ["data analysis", "basic accounting", "financial reporting"],
            "next_step": "mid_level",
            "requirements": ["1-2 years experience", "analytical skills"],
            "learning_resources": [
                "Master Excel and data analysis",
                "Learn basic accounting principles",
                "Get familiar with financial software",
                "Develop business communication skills"
            ]
        },
        "mid_level": {
            "title": "Analyst/Manager",
            "skills": ["financial modeling", "business analysis", "project management"],
            "next_step": "senior_level",
            "requirements": ["3-5 years experience", "business acumen"],
            "learning_resources": [
                "Get professional certification (CPA, CFA)",
                "Master financial modeling",
                "Develop project management skills",
                "Learn business strategy"
            ]
        },
        "senior_level": {
            "title": "Senior Manager/Senior Analyst",
            "skills": ["strategic analysis", "team leadership", "client management"],
            "next_step": "executive_level",
            "requirements": ["5+ years experience", "leadership experience"],
            "learning_resources": [
                "Develop leadership and management skills",
                "Master strategic business analysis",
                "Learn client relationship management",
                "Study advanced financial planning"
            ]
        },
        "executive_level": {
            "title": "Director/CFO",
            "skills": ["strategic planning", "financial leadership", "business development"],
            "next_step": None,
            "requirements": ["8+ years experience", "executive experience"],
            "learning_resources": [
                "Master strategic financial planning",
                "Develop executive leadership skills",
                "Learn business development and M&A",
                "Study corporate governance"
            ]
        }
    }
}


class CareerGuidanceService:
    """Service for providing career path guidance and progression recommendations."""
    
    def __init__(self):
        self.career_paths = CAREER_PATHS
    
    def get_user_career_level(self, cv: Optional[CV]) -> str:
        """Determine user's current career level based on CV analysis."""
        if not cv:
            return "entry_level"
        
        if cv.experience_level:
            # Map experience levels to career stages
            level_mapping = {
                "entry_level": "entry_level",
                "junior": "entry_level", 
                "mid_level": "mid_level",
                "senior": "senior_level",
                "executive": "executive_level",
                "expert": "executive_level"
            }
            return level_mapping.get(cv.experience_level.lower(), "entry_level")
        
        # Fallback to years of experience
        if cv.total_years_experience:
            years = cv.total_years_experience
            if years < 2:
                return "entry_level"
            elif years < 5:
                return "mid_level"
            elif years < 8:
                return "senior_level"
            else:
                return "executive_level"
        
        return "entry_level"
    
    def get_career_path(self, user: User, cv: Optional[CV] = None) -> Dict:
        """Get career path guidance for user based on their field and current level."""
        # Determine user's field
        user_field = normalize_department(user.department)
        if cv and cv.field and cv.field != "other":
            user_field = cv.field
        
        if not user_field or user_field == "other":
            user_field = "computer_it"  # Default fallback
        
        # Get career paths for user's field
        field_paths = self.career_paths.get(user_field, self.career_paths["computer_it"])
        
        # Determine current level
        current_level = self.get_user_career_level(cv)
        
        # Get current and next stages
        current_stage = field_paths.get(current_level, field_paths["entry_level"])
        next_level_key = current_stage.get("next_step")
        next_stage = field_paths.get(next_level_key) if next_level_key else None
        
        return {
            "field": user_field,
            "current_level": current_level,
            "current_stage": current_stage,
            "next_stage": next_stage,
            "all_stages": field_paths,
            "progress_percentage": self._calculate_progress_percentage(current_level, field_paths)
        }
    
    def _calculate_progress_percentage(self, current_level: str, field_paths: Dict) -> int:
        """Calculate career progress percentage."""
        stages = ["entry_level", "mid_level", "senior_level", "executive_level"]
        current_index = stages.index(current_level) if current_level in stages else 0
        return int((current_index / (len(stages) - 1)) * 100)
    
    def get_skill_gaps_for_next_level(self, user: User, cv: Optional[CV] = None) -> Dict:
        """Identify skill gaps to reach the next career level."""
        career_path = self.get_career_path(user, cv)
        current_stage = career_path["current_stage"]
        next_stage = career_path["next_stage"]
        
        if not next_stage:
            return {
                "message": "You've reached the executive level - focus on leadership and strategic skills",
                "current_skills": current_stage.get("skills", []),
                "missing_skills": [],
                "recommendations": []
            }
        
        # Parse user's current skills
        user_skills = set()
        if cv and cv.skills:
            try:
                import json
                skills_data = json.loads(cv.skills)
                if isinstance(skills_data, list):
                    user_skills = {str(skill).lower() for skill in skills_data}
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Identify missing skills
        required_skills = set(next_stage.get("skills", []))
        missing_skills = [skill for skill in required_skills if skill not in user_skills]
        
        return {
            "current_level": career_path["current_level"],
            "next_level": career_path["next_stage"],
            "current_skills": current_stage.get("skills", []),
            "required_skills": next_stage.get("skills", []),
            "missing_skills": missing_skills,
            "requirements": next_stage.get("requirements", []),
            "learning_resources": next_stage.get("learning_resources", []),
            "skill_gap_percentage": len(missing_skills) / len(required_skills) * 100 if required_skills else 0
        }
    
    def get_career_roadmap(self, user: User, cv: Optional[CV] = None) -> List[Dict]:
        """Get complete career roadmap from current level to executive."""
        career_path = self.get_career_path(user, cv)
        current_level = career_path["current_level"]
        all_stages = career_path["all_stages"]
        
        stages_order = ["entry_level", "mid_level", "senior_level", "executive_level"]
        current_index = stages_order.index(current_level) if current_level in stages_order else 0
        
        roadmap = []
        for i in range(current_index, len(stages_order)):
            stage_key = stages_order[i]
            stage = all_stages.get(stage_key)
            if stage:
                roadmap.append({
                    "level": stage_key,
                    "title": stage.get("title"),
                    "skills": stage.get("skills", []),
                    "requirements": stage.get("requirements", []),
                    "is_current": (i == current_index),
                    "is_next": (i == current_index + 1)
                })
        
        return roadmap
