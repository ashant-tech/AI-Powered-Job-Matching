"""
Career Transition Guidance Service

Analyzes transferable skills for different industries, identifies career paths based on skills,
suggests certifications/education needed for transitions, and provides success probability scoring.
"""
from typing import List, Dict, Optional
from app.models.cv import CV
from app.models.user import User
from app.services.field_classifier import normalize_department


# Industry transition paths with skill mappings
CAREER_TRANSITIONS = {
    "computer_it": {
        "to_engineering": {
            "transferable_skills": ["problem solving", "analytical thinking", "systems thinking", "technical documentation"],
            "new_skills_needed": ["cad software", "engineering principles", "manufacturing processes", "safety protocols"],
            "certifications": ["Six Sigma", "AutoCAD Certification", "Project Management Professional"],
            "education": ["Engineering degree", "Technical certification programs"],
            "transition_difficulty": "medium",
            "success_probability": 70
        },
        "to_business_finance": {
            "transferable_skills": ["data analysis", "problem solving", "process improvement", "technical documentation"],
            "new_skills_needed": ["financial modeling", "business analysis", "accounting principles", "market analysis"],
            "certifications": ["CFA Level 1", "Financial Modeling Certification", "Business Analytics"],
            "education": ["MBA", "Finance degree", "Business analytics programs"],
            "transition_difficulty": "low",
            "success_probability": 85
        },
        "to_health": {
            "transferable_skills": ["data analysis", "systems thinking", "process improvement", "documentation"],
            "new_skills_needed": ["medical terminology", "healthcare systems", "clinical protocols", "patient care"],
            "certifications": ["Health Informatics", "Healthcare Data Analytics", "Project Management in Healthcare"],
            "education": ["Health Informatics degree", "Public Health programs"],
            "transition_difficulty": "high",
            "success_probability": 60
        }
    },
    "engineering": {
        "to_computer_it": {
            "transferable_skills": ["problem solving", "systems thinking", "technical documentation", "project management"],
            "new_skills_needed": ["programming", "software development", "cloud computing", "data structures"],
            "certifications": ["AWS Certification", "Google Cloud Certification", "Full Stack Development"],
            "education": ["Computer Science degree", "Coding bootcamps", "Software engineering programs"],
            "transition_difficulty": "medium",
            "success_probability": 75
        },
        "to_business_finance": {
            "transferable_skills": ["project management", "analytical thinking", "budget management", "process improvement"],
            "new_skills_needed": ["financial analysis", "business strategy", "market analysis", "risk management"],
            "certifications": ["PMP", "Financial Analysis Certification", "Six Sigma"],
            "education": ["MBA", "Finance degree", "Business administration"],
            "transition_difficulty": "low",
            "success_probability": 80
        },
        "to_health": {
            "transferable_skills": ["systems thinking", "quality control", "project management", "technical documentation"],
            "new_skills_needed": ["healthcare systems", "medical device knowledge", "regulatory compliance", "patient safety"],
            "certifications": ["Biomedical Engineering", "Healthcare Project Management"],
            "education": ["Biomedical Engineering degree", "Health Technology programs"],
            "transition_difficulty": "high",
            "success_probability": 65
        }
    },
    "business_finance": {
        "to_computer_it": {
            "transferable_skills": ["data analysis", "project management", "problem solving", "communication"],
            "new_skills_needed": ["programming", "software development", "data science", "cloud platforms"],
            "certifications": ["Data Science Certification", "Cloud Computing", "SQL"],
            "education": ["Data Science degree", "Coding bootcamps", "Business analytics"],
            "transition_difficulty": "medium",
            "success_probability": 70
        },
        "to_engineering": {
            "transferable_skills": ["project management", "analytical thinking", "budget management", "process improvement"],
            "new_skills_needed": ["technical principles", "engineering software", "manufacturing processes", "safety standards"],
            "certifications": ["Six Sigma", "Project Management", "Engineering Fundamentals"],
            "education": ["Engineering degree", "Technical programs"],
            "transition_difficulty": "high",
            "success_probability": 55
        },
        "to_health": {
            "transferable_skills": ["project management", "analytical thinking", "communication", "process improvement"],
            "new_skills_needed": ["healthcare administration", "medical terminology", "healthcare finance", "regulatory knowledge"],
            "certifications": ["Healthcare Administration", "Healthcare Finance"],
            "education": ["Healthcare Administration degree", "Public Health"],
            "transition_difficulty": "medium",
            "success_probability": 75
        }
    },
    "health": {
        "to_computer_it": {
            "transferable_skills": ["data analysis", "systems thinking", "documentation", "problem solving"],
            "new_skills_needed": ["programming", "software development", "health informatics", "data science"],
            "certifications": ["Health Informatics", "Data Science", "Healthcare IT"],
            "education": ["Health Informatics degree", "Data Science programs", "Healthcare IT certification"],
            "transition_difficulty": "medium",
            "success_probability": 70
        },
        "to_business_finance": {
            "transferable_skills": ["project management", "communication", "analytical thinking", "process improvement"],
            "new_skills_needed": ["financial analysis", "business administration", "healthcare economics", "management"],
            "certifications": ["Healthcare Administration", "Healthcare Finance", "MBA"],
            "education": ["Healthcare Administration degree", "MBA with healthcare focus"],
            "transition_difficulty": "low",
            "success_probability": 80
        },
        "to_engineering": {
            "transferable_skills": ["systems thinking", "quality control", "documentation", "problem solving"],
            "new_skills_needed": ["technical principles", "engineering software", "manufacturing knowledge", "safety protocols"],
            "certifications": ["Biomedical Engineering", "Quality Assurance"],
            "education": ["Biomedical Engineering degree", "Engineering programs"],
            "transition_difficulty": "high",
            "success_probability": 50
        }
    }
}


# Industry growth and demand analysis
INDUSTRY_ANALYSIS = {
    "computer_it": {
        "growth_rate": "high",
        "job_demand": "very high",
        "salary_trend": "increasing",
        "future_outlook": "excellent",
        "key_trends": ["AI/ML", "Cloud Computing", "Cybersecurity", "Data Science"]
    },
    "engineering": {
        "growth_rate": "moderate",
        "job_demand": "high",
        "salary_trend": "stable",
        "future_outlook": "good",
        "key_trends": ["Sustainable Engineering", "Smart Infrastructure", "Automation", "3D Printing"]
    },
    "health": {
        "growth_rate": "high",
        "job_demand": "very high",
        "salary_trend": "increasing",
        "future_outlook": "excellent",
        "key_trends": ["Telehealth", "Health Informatics", "Personalized Medicine", "Aging Population Care"]
    },
    "business_finance": {
        "growth_rate": "moderate",
        "job_demand": "high",
        "salary_trend": "stable",
        "future_outlook": "good",
        "key_trends": ["FinTech", "Data Analytics", "ESG Investing", "Digital Transformation"]
    }
}


class CareerTransitionService:
    """Service for career transition guidance and analysis."""
    
    def __init__(self):
        self.career_transitions = CAREER_TRANSITIONS
        self.industry_analysis = INDUSTRY_ANALYSIS
    
    def analyze_transferable_skills(self, cv: CV, target_field: str) -> Dict:
        """Analyze transferable skills for career transition."""
        if not cv:
            return {"error": "No CV data available"}
        
        # Determine current field
        current_field = cv.field if cv.field and cv.field != "other" else "computer_it"
        
        # Get transition data
        transition_key = f"to_{target_field}"
        transition_data = self.career_transitions.get(current_field, {}).get(transition_key)
        
        if not transition_data:
            return {
                "error": f"No transition data available from {current_field} to {target_field}",
                "suggestion": "Consider a different transition path or consult with a career counselor"
            }
        
        # Parse user's current skills
        user_skills = set()
        if cv.skills:
            try:
                import json
                skills_data = json.loads(cv.skills)
                if isinstance(skills_data, list):
                    user_skills = {str(skill).lower() for skill in skills_data}
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Identify transferable skills the user has
        transferable_skills = transition_data["transferable_skills"]
        user_transferable = [skill for skill in transferable_skills if skill in user_skills]
        
        # Calculate transferability score
        transferability_score = int((len(user_transferable) / len(transferable_skills)) * 100) if transferable_skills else 0
        
        return {
            "current_field": current_field,
            "target_field": target_field,
            "transferable_skills": transferable_skills,
            "user_has_transferable": user_transferable,
            "transferability_score": transferability_score,
            "new_skills_needed": transition_data["new_skills_needed"],
            "certifications": transition_data["certifications"],
            "education": transition_data["education"],
            "transition_difficulty": transition_data["transition_difficulty"],
            "success_probability": transition_data["success_probability"],
            "recommendation": self._generate_transition_recommendation(transferability_score, transition_data)
        }
    
    def _generate_transition_recommendation(self, transferability_score: int, transition_data: Dict) -> str:
        """Generate personalized transition recommendation."""
        difficulty = transition_data["transition_difficulty"]
        success_prob = transition_data["success_probability"]
        
        if transferability_score >= 70 and success_prob >= 70:
            return f"Excellent transition potential! You have strong transferable skills and a {success_prob}% success probability. Focus on the identified certifications and education to maximize your chances."
        elif transferability_score >= 50 and success_prob >= 60:
            return f"Good transition potential. You have some transferable skills and a {success_prob}% success probability. Consider gaining additional experience or certifications before making the transition."
        elif transferability_score >= 30:
            return f"Moderate transition potential. This is a {difficulty} transition with {success_prob}% success probability. You'll need to invest significantly in new skills and education."
        else:
            return f"Challenging transition. This is a {difficulty} transition with limited transferable skills. Consider whether this path aligns with your long-term goals and if you're willing to invest the required time and resources."
    
    def get_all_transition_paths(self, cv: CV) -> List[Dict]:
        """Get all possible career transition paths for the user."""
        if not cv:
            return []
        
        current_field = cv.field if cv.field and cv.field != "other" else "computer_it"
        
        available_transitions = self.career_transitions.get(current_field, {})
        
        transition_paths = []
        for target_field, transition_data in available_transitions.items():
            target_field_clean = target_field.replace("to_", "")
            
            # Parse user's current skills
            user_skills = set()
            if cv.skills:
                try:
                    import json
                    skills_data = json.loads(cv.skills)
                    if isinstance(skills_data, list):
                        user_skills = {str(skill).lower() for skill in skills_data}
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Calculate transferability
            transferable_skills = transition_data["transferable_skills"]
            user_transferable = [skill for skill in transferable_skills if skill in user_skills]
            transferability_score = int((len(user_transferable) / len(transferable_skills)) * 100) if transferable_skills else 0
            
            transition_paths.append({
                "target_field": target_field_clean,
                "transferability_score": transferability_score,
                "success_probability": transition_data["success_probability"],
                "transition_difficulty": transition_data["transition_difficulty"],
                "certifications_needed": len(transition_data["certifications"]),
                "education_needed": len(transition_data["education"]),
                "overall_score": (transferability_score + transition_data["success_probability"]) // 2
            })
        
        # Sort by overall score
        transition_paths.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return transition_paths
    
    def analyze_industry_comparison(self, current_field: str, target_field: str) -> Dict:
        """Compare industries for career transition decision making."""
        current_analysis = self.industry_analysis.get(current_field, self.industry_analysis["computer_it"])
        target_analysis = self.industry_analysis.get(target_field, self.industry_analysis["computer_it"])
        
        comparison = {
            "current_field": current_field,
            "target_field": target_field,
            "current_analysis": current_analysis,
            "target_analysis": target_analysis,
            "growth_comparison": self._compare_growth(current_analysis, target_analysis),
            "demand_comparison": self._compare_demand(current_analysis, target_analysis),
            "salary_trend_comparison": self._compare_salary_trend(current_analysis, target_analysis),
            "recommendation": self._generate_industry_recommendation(current_analysis, target_analysis)
        }
        
        return comparison
    
    def _compare_growth(self, current: Dict, target: Dict) -> str:
        """Compare growth rates between industries."""
        growth_order = {"low": 0, "moderate": 1, "high": 2}
        current_score = growth_order.get(current["growth_rate"], 1)
        target_score = growth_order.get(target["growth_rate"], 1)
        
        if target_score > current_score:
            return f"Target field has higher growth potential ({target['growth_rate']} vs {current['growth_rate']})"
        elif target_score < current_score:
            return f"Current field has higher growth potential ({current['growth_rate']} vs {target['growth_rate']})"
        else:
            return "Both fields have similar growth potential"
    
    def _compare_demand(self, current: Dict, target: Dict) -> str:
        """Compare job demand between industries."""
        demand_order = {"low": 0, "moderate": 1, "high": 2, "very high": 3}
        current_score = demand_order.get(current["job_demand"], 1)
        target_score = demand_order.get(target["job_demand"], 1)
        
        if target_score > current_score:
            return f"Target field has higher job demand ({target['job_demand']} vs {current['job_demand']})"
        elif target_score < current_score:
            return f"Current field has higher job demand ({current['job_demand']} vs {target['job_demand']})"
        else:
            return "Both fields have similar job demand"
    
    def _compare_salary_trend(self, current: Dict, target: Dict) -> str:
        """Compare salary trends between industries."""
        if target["salary_trend"] == "increasing" and current["salary_trend"] != "increasing":
            return f"Target field has better salary trends ({target['salary_trend']} vs {current['salary_trend']})"
        elif current["salary_trend"] == "increasing" and target["salary_trend"] != "increasing":
            return f"Current field has better salary trends ({current['salary_trend']} vs {target['salary_trend']})"
        else:
            return "Both fields have similar salary trends"
    
    def _generate_industry_recommendation(self, current: Dict, target: Dict) -> str:
        """Generate industry comparison recommendation."""
        if target["future_outlook"] == "excellent" and current["future_outlook"] != "excellent":
            return f"Strong recommendation to transition to {target} - excellent future outlook with high growth and demand"
        elif target["future_outlook"] == "excellent":
            return f"Good potential in {target} - excellent future outlook, but consider transition costs"
        elif target["future_outlook"] == current["future_outlook"]:
            return f"Both fields have similar outlook - consider personal interests and transition costs"
        else:
            return f"Transition to {target} may not provide significant industry advantages - consider other factors"
    
    def get_transition_timeline(self, cv: CV, target_field: str) -> Dict:
        """Get estimated timeline for career transition."""
        transition_analysis = self.analyze_transferable_skills(cv, target_field)
        
        if "error" in transition_analysis:
            return transition_analysis
        
        difficulty = transition_analysis["transition_difficulty"]
        certifications_needed = len(transition_analysis["certifications"])
        education_needed = len(transition_analysis["education"])
        
        # Estimate timeline based on difficulty and requirements
        base_months = {"low": 6, "medium": 12, "high": 18}
        timeline_months = base_months.get(difficulty, 12)
        
        # Add time for certifications (3 months each)
        timeline_months += certifications_needed * 3
        
        # Add time for education (6 months each)
        timeline_months += education_needed * 6
        
        # Create phase breakdown
        phases = []
        current_month = 0
        
        if certifications_needed > 0:
            phases.append({
                "phase": "Certification",
                "duration": f"{certifications_needed * 3} months",
                "description": f"Complete {certifications_needed} certification(s)"
            })
            current_month += certifications_needed * 3
        
        if education_needed > 0:
            phases.append({
                "phase": "Education",
                "duration": f"{education_needed * 6} months",
                "description": f"Complete {education_needed} education program(s)"
            })
            current_month += education_needed * 6
        
        phases.append({
            "phase": "Skill Development",
            "duration": f"{3} months",
            "description": "Develop new skills through practice and projects"
        })
        current_month += 3
        
        phases.append({
            "phase": "Job Search",
            "duration": f"{3} months",
            "description": "Active job search and networking in new field"
        })
        
        return {
            "total_timeline_months": timeline_months,
            "total_timeline_years": round(timeline_months / 12, 1),
            "phases": phases,
            "difficulty": difficulty,
            "estimated_cost": self._estimate_transition_cost(certifications_needed, education_needed),
            "risk_factors": self._identify_risk_factors(difficulty, transition_analysis)
        }
    
    def _estimate_transition_cost(self, certifications: int, education: int) -> Dict:
        """Estimate costs for career transition."""
        # Average costs (rough estimates)
        certification_cost = certifications * 500  # $500 per certification
        education_cost = education * 5000  # $5000 per education program
        opportunity_cost = 6 * 5000  # 6 months * $5000/month (lost wages)
        
        total_cost = certification_cost + education_cost + opportunity_cost
        
        return {
            "certification_cost": certification_cost,
            "education_cost": education_cost,
            "opportunity_cost": opportunity_cost,
            "total_estimated_cost": total_cost,
            "currency": "USD"
        }
    
    def _identify_risk_factors(self, difficulty: str, analysis: Dict) -> List[str]:
        """Identify potential risk factors in career transition."""
        risks = []
        
        if difficulty == "high":
            risks.append("High difficulty transition requires significant time and financial investment")
        
        if analysis["success_probability"] < 60:
            risks.append("Lower success probability - may require extended transition period")
        
        if len(analysis["new_skills_needed"]) > 5:
            risks.append("Large number of new skills required - steep learning curve")
        
        if len(analysis["certifications"]) > 2:
            risks.append("Multiple certifications needed - additional time and cost")
        
        if len(analysis["education"]) > 0:
            risks.append("Formal education required - significant time and financial commitment")
        
        if not risks:
            risks.append("Low-risk transition with good success probability")
        
        return risks
