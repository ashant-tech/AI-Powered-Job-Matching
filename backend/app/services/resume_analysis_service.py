"""
Resume Analysis Service

Provides AI-powered resume analysis and improvement suggestions to help users
create stronger, ATS-friendly resumes. Identifies transferable and hidden skills
from a candidate's experience.
"""
from typing import List, Dict, Optional
import re
from app.models.cv import CV


# ATS-friendly keywords and phrases by field
ATS_KEYWORDS = {
    "computer_it": [
        "python", "javascript", "react", "node.js", "django", "flask", "sql", "nosql",
        "cloud computing", "aws", "azure", "docker", "kubernetes", "git", "agile",
        "scrum", "ci/cd", "api development", "microservices", "system design",
        "machine learning", "data analysis", "cybersecurity", "devops", "full stack",
        "frontend", "backend", "database", "algorithms", "data structures"
    ],
    "engineering": [
        "autocad", "solidworks", "revit", "project management", "quality control",
        "structural analysis", "fluid dynamics", "thermodynamics", "materials science",
        "manufacturing", "construction", "civil engineering", "mechanical engineering",
        "electrical engineering", "chemical engineering", "industrial engineering",
        "fe exam", "pe license", "cad/cam", "finite element analysis", "safety protocols"
    ],
    "health": [
        "patient care", "clinical procedures", "medical terminology", "electronic health records",
        "patient assessment", "treatment planning", "medical diagnosis", "healthcare management",
        "clinical research", "medical software", "patient safety", "quality improvement",
        "healthcare compliance", "patient communication", "medical documentation",
        "triage", "vital signs", "medical procedures", "patient education"
    ],
    "business_finance": [
        "financial analysis", "financial modeling", "accounting", "budgeting", "forecasting",
        "business intelligence", "data analysis", "project management", "strategic planning",
        "risk management", "financial reporting", "audit", "compliance", "business development",
        "market analysis", "customer relationship management", "supply chain management",
        "excel", "power bi", "tableau", "financial software", "business strategy"
    ]
}


# Common transferable skills across all fields
TRANSFERABLE_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "time management", "project management", "adaptability", "creativity", "analytical thinking",
    "customer service", "negotiation", "presentation", "writing", "research",
    "mentoring", "training", "organization", "planning", "decision making",
    "conflict resolution", "collaboration", "multitasking", "attention to detail"
]


# Hidden skills indicators - phrases that suggest underlying skills
HIDDEN_SKILL_INDICATORS = {
    "leadership": ["led", "managed", "supervised", "coordinated", "directed", "mentored"],
    "problem solving": ["solved", "resolved", "addressed", "troubleshooted", "fixed"],
    "communication": ["presented", "explained", "wrote", "reported", "communicated"],
    "teamwork": ["collaborated", "worked with", "team", "group", "together"],
    "project management": ["planned", "organized", "coordinated", "managed project"],
    "analytical thinking": ["analyzed", "evaluated", "assessed", "studied", "researched"],
    "customer service": ["customer", "client", "served", "helped", "assisted"],
    "adaptability": ["adapted", "flexible", "adjusted", "learned quickly"],
    "creativity": ["created", "designed", "innovated", "developed new"],
    "mentoring": ["trained", "taught", "guided", "mentored", "coached"]
}


class ResumeAnalysisService:
    """Service for analyzing CVs and providing improvement suggestions."""
    
    def __init__(self):
        self.ats_keywords = ATS_KEYWORDS
        self.transferable_skills = TRANSFERABLE_SKILLS
        self.hidden_skill_indicators = HIDDEN_SKILL_INDICATORS
    
    def analyze_resume(self, cv: CV) -> Dict:
        """Comprehensive resume analysis with improvement suggestions."""
        if not cv:
            return {
                "error": "No CV data available for analysis"
            }
        
        # Extract text content from CV
        cv_text = self._extract_cv_text(cv)
        
        # Determine field
        field = cv.field if cv.field and cv.field != "other" else "computer_it"
        
        # Perform various analyses
        ats_score = self._calculate_ats_score(cv_text, field)
        skill_analysis = self._analyze_skills(cv_text, field)
        hidden_skills = self._identify_hidden_skills(cv_text)
        improvement_suggestions = self._generate_improvement_suggestions(cv, cv_text, field)
        
        return {
            "ats_score": ats_score,
            "ats_rating": self._get_ats_rating(ats_score),
            "skill_analysis": skill_analysis,
            "hidden_skills": hidden_skills,
            "improvement_suggestions": improvement_suggestions,
            "field": field,
            "experience_level": cv.experience_level or "unknown",
            "total_years_experience": cv.total_years_experience or 0
        }
    
    def _extract_cv_text(self, cv: CV) -> str:
        """Extract all text content from CV for analysis."""
        text_parts = []
        
        if cv.summary:
            text_parts.append(cv.summary)
        
        if cv.skills:
            try:
                import json
                skills_data = json.loads(cv.skills)
                if isinstance(skills_data, list):
                    text_parts.append(" ".join(skills_data))
            except (json.JSONDecodeError, TypeError):
                text_parts.append(cv.skills)
        
        if cv.experience:
            try:
                import json
                experience_data = json.loads(cv.experience)
                if isinstance(experience_data, list):
                    for exp in experience_data:
                        if isinstance(exp, dict):
                            text_parts.append(exp.get("description", ""))
                            text_parts.append(exp.get("company", ""))
                            text_parts.append(exp.get("title", ""))
            except (json.JSONDecodeError, TypeError):
                text_parts.append(cv.experience)
        
        if cv.education:
            try:
                import json
                education_data = json.loads(cv.education)
                if isinstance(education_data, list):
                    for edu in education_data:
                        if isinstance(edu, dict):
                            text_parts.append(edu.get("degree", ""))
                            text_parts.append(edu.get("institution", ""))
                            text_parts.append(edu.get("field_of_study", ""))
            except (json.JSONDecodeError, TypeError):
                text_parts.append(cv.education)
        
        return " ".join(text_parts).lower()
    
    def _calculate_ats_score(self, cv_text: str, field: str) -> int:
        """Calculate ATS-friendliness score (0-100)."""
        if not cv_text:
            return 0
        
        field_keywords = self.ats_keywords.get(field, self.ats_keywords["computer_it"])
        
        # Count matching keywords
        matches = 0
        for keyword in field_keywords:
            if keyword.lower() in cv_text:
                matches += 1
        
        # Calculate score
        if len(field_keywords) == 0:
            return 0
        
        score = int((matches / len(field_keywords)) * 100)
        return min(score, 100)
    
    def _get_ats_rating(self, score: int) -> str:
        """Get rating based on ATS score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _analyze_skills(self, cv_text: str, field: str) -> Dict:
        """Analyze skills in the CV."""
        if not cv_text:
            return {
                "found_skills": [],
                "missing_ats_keywords": [],
                "skill_coverage": 0
            }
        
        field_keywords = self.ats_keywords.get(field, self.ats_keywords["computer_it"])
        
        # Find skills present in CV
        found_skills = []
        for keyword in field_keywords:
            if keyword.lower() in cv_text:
                found_skills.append(keyword)
        
        # Find missing ATS keywords
        missing_keywords = [kw for kw in field_keywords if kw.lower() not in cv_text]
        
        # Calculate skill coverage
        coverage = int((len(found_skills) / len(field_keywords)) * 100) if field_keywords else 0
        
        return {
            "found_skills": found_skills,
            "missing_ats_keywords": missing_keywords[:10],  # Top 10 missing
            "skill_coverage": coverage
        }
    
    def _identify_hidden_skills(self, cv_text: str) -> List[str]:
        """Identify transferable and hidden skills from experience descriptions."""
        if not cv_text:
            return []
        
        hidden_skills = []
        
        for skill, indicators in self.hidden_skill_indicators.items():
            for indicator in indicators:
                if indicator in cv_text:
                    if skill not in hidden_skills:
                        hidden_skills.append(skill)
                    break
        
        return hidden_skills
    
    def _generate_improvement_suggestions(self, cv: CV, cv_text: str, field: str) -> List[str]:
        """Generate specific improvement suggestions."""
        suggestions = []
        
        # Check for missing sections
        if not cv.summary or len(cv.summary) < 50:
            suggestions.append("Add a comprehensive professional summary (2-3 sentences highlighting your key strengths and career goals)")
        
        if not cv.skills or len(cv.skills) < 10:
            suggestions.append("Expand your skills section with specific technical and soft skills")
        
        if not cv.experience:
            suggestions.append("Add detailed work experience with company names, dates, and achievements")
        
        if not cv.education:
            suggestions.append("Include your educational background with degrees, institutions, and graduation dates")
        
        # Check ATS keywords
        field_keywords = self.ats_keywords.get(field, self.ats_keywords["computer_it"])
        missing_keywords = [kw for kw in field_keywords if kw.lower() not in cv_text]
        
        if len(missing_keywords) > 5:
            suggestions.append(f"Add more field-specific keywords. Consider including: {', '.join(missing_keywords[:5])}")
        
        # Check for quantifiable achievements
        if not re.search(r'\d+%|\d+ percent|\$\d+|\d+ (people|projects|clients|team|customers)', cv_text):
            suggestions.append("Add quantifiable achievements (e.g., 'increased sales by 25%', 'managed team of 10 people')")
        
        # Check for action verbs
        action_verbs = ["led", "managed", "developed", "created", "implemented", "achieved", "improved", "increased", "reduced", "designed"]
        action_verb_count = sum(1 for verb in action_verbs if verb in cv_text)
        
        if action_verb_count < 3:
            suggestions.append("Use more action verbs at the beginning of bullet points (e.g., 'Led a team of...', 'Developed a system that...')")
        
        # Check for transferable skills
        hidden_skills = self._identify_hidden_skills(cv_text)
        if len(hidden_skills) < 5:
            suggestions.append("Highlight more transferable skills like leadership, communication, and problem-solving")
        
        # Experience level specific suggestions
        if cv.experience_level and cv.experience_level in ["entry_level", "junior"]:
            suggestions.append("For entry-level positions, emphasize education, internships, and relevant projects")
        elif cv.experience_level in ["senior", "executive", "expert"]:
            suggestions.append("For senior positions, highlight leadership, strategic thinking, and mentorship experience")
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def get_resume_optimization_tips(self, field: str) -> List[str]:
        """Get general resume optimization tips for a specific field."""
        field_tips = {
            "computer_it": [
                "Include specific programming languages and frameworks",
                "Highlight projects with GitHub links",
                "Mention cloud platforms and DevOps tools",
                "Include technical certifications (AWS, Azure, GCP)",
                "Quantify technical achievements (e.g., 'reduced API response time by 40%')"
            ],
            "engineering": [
                "List CAD and engineering software proficiency",
                "Include relevant certifications (FE, PE)",
                "Highlight project experience with specific outcomes",
                "Mention safety protocols and quality standards",
                "Include interdisciplinary collaboration examples"
            ],
            "health": [
                "Include specific clinical skills and procedures",
                "List healthcare software proficiency (EHR systems)",
                "Highlight patient care outcomes and metrics",
                "Include relevant certifications and licenses",
                "Mention specialized training and continuing education"
            ],
            "business_finance": [
                "Include financial software proficiency (Excel, SAP)",
                "Highlight quantifiable business achievements",
                "List relevant certifications (CPA, CFA, PMP)",
                "Include industry-specific knowledge",
                "Mention cross-functional collaboration examples"
            ]
        }
        
        return field_tips.get(field, field_tips["computer_it"])
