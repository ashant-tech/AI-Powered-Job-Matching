"""
Salary Negotiation Assistant Service

Provides market salary analysis, salary negotiation script generation, counter-offer suggestions,
benefits package analysis, and equity/stock option evaluation.
"""
from typing import List, Dict, Optional
from app.models.job import ExternalJob
from app.models.cv import CV


# Market salary data by field, experience level, and location (Ethiopia).
# Values are MONTHLY GROSS in Ethiopian Birr (ETB) — Ethiopian job postings
# (EthioJobs, Telegram channels) quote monthly salary, and job.salary_min/max
# are parsed as monthly, so the market bands must be monthly to compare fairly.
# Figures are national medians; LOCATION_MULTIPLIERS adjust them per city.
# These are realistic estimates — tune them as better local data becomes available.
MARKET_SALARY_DATA = {
    "computer_it": {
        "entry_level": {"min": 8000, "median": 15000, "max": 25000},
        "mid_level": {"min": 20000, "median": 35000, "max": 55000},
        "senior_level": {"min": 45000, "median": 70000, "max": 110000},
        "executive_level": {"min": 90000, "median": 140000, "max": 220000}
    },
    "engineering": {
        "entry_level": {"min": 7000, "median": 12000, "max": 20000},
        "mid_level": {"min": 18000, "median": 30000, "max": 48000},
        "senior_level": {"min": 40000, "median": 60000, "max": 95000},
        "executive_level": {"min": 80000, "median": 120000, "max": 190000}
    },
    "health": {
        "entry_level": {"min": 6000, "median": 10000, "max": 16000},
        "mid_level": {"min": 12000, "median": 20000, "max": 32000},
        "senior_level": {"min": 28000, "median": 45000, "max": 70000},
        "executive_level": {"min": 60000, "median": 90000, "max": 140000}
    },
    "business_finance": {
        "entry_level": {"min": 7000, "median": 12000, "max": 20000},
        "mid_level": {"min": 18000, "median": 30000, "max": 48000},
        "senior_level": {"min": 40000, "median": 60000, "max": 95000},
        "executive_level": {"min": 80000, "median": 120000, "max": 190000}
    }
}


# Location multipliers (cost of living adjustments for Ethiopian cities)
LOCATION_MULTIPLIERS = {
    "addis ababa": 1.3,      # Capital city, highest cost of living
    "addis": 1.3,            # Abbreviation
    "dire dawa": 1.1,        # Major city
    "mekelle": 1.05,         # Regional capital
    "hawassa": 1.05,         # Regional capital
    "adama": 1.0,            # Industrial city
    "bahir dar": 1.0,         # Regional capital
    "gondar": 0.95,          # Historical city
    "jimma": 0.95,           # Regional capital
    "ethiopia": 1.0,         # Country average
    "remote": 0.85,          # Remote work typically lower cost
    "other": 1.0
}


# Benefits package evaluation criteria (Ethiopia-appropriate)
BENEFITS_CRITERIA = {
    "health_insurance": {"weight": 30, "excellent": "Full coverage with minimal deductibles", "good": "Standard coverage", "fair": "Basic coverage"},
    "retirement_pension": {"weight": 25, "excellent": "Company pension scheme with 10%+ contribution", "good": "Social security + private pension", "fair": "Social security only"},
    "vacation_days": {"weight": 15, "excellent": "20+ days per year", "good": "15-19 days per year", "fair": "10-14 days per year"},
    "remote_work": {"weight": 15, "excellent": "Full remote work option", "good": "Hybrid option available", "fair": "On-site only"},
    "professional_development": {"weight": 10, "excellent": "Full training sponsorship", "good": "Partial training support", "fair": "Limited training budget"},
    "bonus_structure": {"weight": 5, "excellent": "Annual bonus + performance bonuses", "good": "Annual bonus only", "fair": "No bonus or irregular"}
}


class SalaryNegotiationService:
    """Service for salary negotiation assistance and market analysis."""
    
    def __init__(self):
        self.market_salary_data = MARKET_SALARY_DATA
        self.location_multipliers = LOCATION_MULTIPLIERS
        self.benefits_criteria = BENEFITS_CRITERIA
    
    def analyze_market_salary(self, field: str, experience_level: str, location: str = "other") -> Dict:
        """Analyze market salary based on field, experience, and location."""
        # Get base salary data
        field_data = self.market_salary_data.get(field, self.market_salary_data["computer_it"])
        level_data = field_data.get(experience_level, field_data["entry_level"])
        
        # Apply location multiplier
        location_lower = location.lower()
        location_multiplier = 1.0
        for loc, mult in self.location_multipliers.items():
            if loc in location_lower:
                location_multiplier = mult
                break
        
        # Calculate adjusted salaries
        adjusted_min = int(level_data["min"] * location_multiplier)
        adjusted_median = int(level_data["median"] * location_multiplier)
        adjusted_max = int(level_data["max"] * location_multiplier)
        
        return {
            "field": field,
            "experience_level": experience_level,
            "location": location,
            "location_multiplier": location_multiplier,
            "base_salary_range": level_data,
            "adjusted_salary_range": {
                "min": adjusted_min,
                "median": adjusted_median,
                "max": adjusted_max
            },
            "market_analysis": self._generate_market_analysis(adjusted_median, level_data),
            "negotiation_range": {
                "conservative": adjusted_median,
                "moderate": int(adjusted_median * 1.1),
                "aggressive": int(adjusted_median * 1.2)
            }
        }
    
    def _generate_market_analysis(self, median_salary: int, level_data: Dict) -> str:
        """Generate market analysis text. Thresholds are monthly gross ETB."""
        if median_salary >= 60000:
            return "High salary range - this is a senior/executive level position with strong compensation"
        elif median_salary >= 30000:
            return "Above-average salary range - indicates mid-to-senior level position"
        elif median_salary >= 15000:
            return "Average salary range - typical for mid-level positions"
        else:
            return "Entry-level salary range - common for junior positions"
    
    def evaluate_job_offer(self, job: ExternalJob, cv: Optional[CV] = None) -> Dict:
        """Evaluate a job offer against market rates and user's qualifications."""
        if not job:
            return {"error": "No job data available"}
        
        # Determine field and experience level
        field = job.field if job.field and job.field != "other" else "computer_it"
        experience_level = self._determine_experience_level(cv, job)
        location = job.location if job.location else "other"
        
        # Get market analysis
        market_analysis = self.analyze_market_salary(field, experience_level, location)
        
        # Evaluate the job's salary against market
        job_salary_min = job.salary_min if job.salary_min else 0
        job_salary_max = job.salary_max if job.salary_max else 0
        job_salary_avg = (job_salary_min + job_salary_max) / 2 if job_salary_min and job_salary_max else job_salary_min or job_salary_max
        
        market_median = market_analysis["adjusted_salary_range"]["median"]
        
        # Calculate offer competitiveness
        if job_salary_avg > 0:
            if job_salary_avg >= market_median * 1.1:
                competitiveness = "excellent"
                competitiveness_score = 90
            elif job_salary_avg >= market_median:
                competitiveness = "good"
                competitiveness_score = 75
            elif job_salary_avg >= market_median * 0.9:
                competitiveness = "fair"
                competitiveness_score = 60
            else:
                competitiveness = "below_market"
                competitiveness_score = 40
        else:
            competitiveness = "not_specified"
            competitiveness_score = 50
        
        return {
            "job_title": job.title,
            "company": job.company,
            "field": field,
            "experience_level": experience_level,
            "location": location,
            "job_salary": {
                "min": job_salary_min,
                "max": job_salary_max,
                "average": job_salary_avg
            },
            "market_salary": market_analysis["adjusted_salary_range"],
            "competitiveness": competitiveness,
            "competitiveness_score": competitiveness_score,
            "negotiation_potential": self._assess_negotiation_potential(competitiveness_score, job_salary_avg, market_median),
            "recommendation": self._generate_offer_recommendation(competitiveness, job_salary_avg, market_median)
        }
    
    def _determine_experience_level(self, cv: Optional[CV], job: ExternalJob) -> str:
        """Determine experience level from CV or job requirements."""
        if cv and cv.experience_level:
            level_mapping = {
                "entry_level": "entry_level",
                "junior": "entry_level",
                "mid_level": "mid_level",
                "senior": "senior_level",
                "executive": "executive_level",
                "expert": "executive_level"
            }
            return level_mapping.get(cv.experience_level.lower(), "entry_level")
        
        # Fallback to job requirements
        if job.requirements:
            requirements_lower = job.requirements.lower()
            if any(word in requirements_lower for word in ["senior", "lead", "principal", "architect"]):
                return "senior_level"
            elif any(word in requirements_lower for word in ["manager", "director", "head", "chief"]):
                return "executive_level"
            elif any(word in requirements_lower for word in ["mid", "3+", "experienced"]):
                return "mid_level"
        
        return "entry_level"
    
    def _assess_negotiation_potential(self, score: int, job_salary: float, market_median: float) -> str:
        """Assess potential for salary negotiation."""
        if score >= 80:
            return "Low - offer is already competitive"
        elif score >= 60:
            return "Moderate - some room for negotiation"
        elif score >= 40:
            return "High - significant negotiation potential"
        else:
            return "Very High - strong negotiation needed"
    
    def _generate_offer_recommendation(self, competitiveness: str, job_salary: float, market_median: float) -> str:
        """Generate recommendation for the job offer."""
        if competitiveness == "excellent":
            return "Excellent offer! The salary is above market rate. Consider accepting or negotiating benefits."
        elif competitiveness == "good":
            return "Good offer at market rate. Consider negotiating for better benefits or signing bonus."
        elif competitiveness == "fair":
            return "Fair offer slightly below market. Consider negotiating salary or better benefits."
        elif competitiveness == "below_market":
            return f"Offer below market rate by ETB {int(market_median - job_salary):,}. Strong negotiation recommended."
        else:
            return "Salary not specified. Request market rate information during interview process."
    
    def generate_negotiation_script(self, job: ExternalJob, target_salary: int, user_strengths: List[str]) -> Dict:
        """Generate personalized salary negotiation script."""
        if not job:
            return {"error": "No job data available"}
        
        script_components = {
            "opening": f"Thank you for the offer for the {job.title} position at {job.company}. I'm very excited about the opportunity to join your team.",
            "value_proposition": self._generate_value_proposition(user_strengths),
            "salary_request": f"Based on my research of market rates for similar positions and considering my experience and skills, I was hoping for a salary in the ETB {target_salary:,} range.",
            "flexibility": "I'm flexible depending on the total compensation package and growth opportunities within the role.",
            "benefits_interest": "I'd also like to discuss the benefits package, particularly healthcare coverage, retirement matching, and professional development opportunities.",
            "timeline": "When would you be able to get back to me with a revised offer?",
            "closing": "I'm very enthusiastic about this opportunity and believe I can make significant contributions to {job.company}."
        }
        
        return {
            "job_title": job.title,
            "company": job.company,
            "target_salary": target_salary,
            "script_components": script_components,
            "full_script": self._combine_script(script_components),
            "key_points": user_strengths,
            "preparation_tips": self._get_negotiation_preparation_tips()
        }
    
    def _generate_value_proposition(self, user_strengths: List[str]) -> str:
        """Generate value proposition based on user's strengths."""
        if not user_strengths:
            return "I bring strong technical skills and a proven track record of delivering results."
        
        strengths_text = ", ".join(user_strengths[:3])
        return f"My strengths include {strengths}, which I believe will allow me to make immediate contributions to the team."
    
    def _combine_script(self, components: Dict) -> str:
        """Combine script components into full script."""
        return " ".join(components.values())
    
    def _get_negotiation_preparation_tips(self) -> List[str]:
        """Get preparation tips for salary negotiation."""
        return [
            "Research market rates for your position and location",
            "Document your achievements and quantifiable results",
            "Practice your negotiation script out loud",
            "Be prepared to discuss your total compensation expectations",
            "Know your walk-away point before starting negotiations",
            "Consider non-monetary benefits as part of total compensation",
            "Practice active listening during negotiations",
            "Be confident but flexible in your approach"
        ]
    
    def analyze_benefits_package(self, benefits: Dict) -> Dict:
        """Analyze and score a benefits package."""
        if not benefits:
            return {"error": "No benefits data provided"}
        
        total_score = 0
        max_score = 0
        benefit_analysis = {}
        
        for benefit_type, criteria in self.benefits_criteria.items():
            user_benefit = benefits.get(benefit_type)
            weight = criteria["weight"]
            max_score += weight
            
            if user_benefit:
                # Simple scoring based on keywords (updated for Ethiopia context)
                benefit_lower = str(user_benefit).lower()
                if any(word in benefit_lower for word in ["full", "comprehensive", "20+", "10%", "hybrid", "sponsorship", "annual"]):
                    score = weight
                    quality = "excellent"
                elif any(word in benefit_lower for word in ["standard", "social security", "15-19", "partial", "bonus"]):
                    score = int(weight * 0.75)
                    quality = "good"
                else:
                    score = int(weight * 0.5)
                    quality = "fair"
                
                total_score += score
                benefit_analysis[benefit_type] = {
                    "provided": True,
                    "quality": quality,
                    "score": score,
                    "max_score": weight
                }
            else:
                benefit_analysis[benefit_type] = {
                    "provided": False,
                    "quality": "not_provided",
                    "score": 0,
                    "max_score": weight
                }
        
        overall_score = int((total_score / max_score) * 100) if max_score > 0 else 0
        
        return {
            "overall_score": overall_score,
            "overall_rating": self._get_benefits_rating(overall_score),
            "benefit_analysis": benefit_analysis,
            "missing_benefits": [bt for bt, ba in benefit_analysis.items() if not ba["provided"]],
            "strengths": [bt for bt, ba in benefit_analysis.items() if ba["quality"] == "excellent"],
            "improvements": self._suggest_benefits_improvements(benefit_analysis)
        }
    
    def _get_benefits_rating(self, score: int) -> str:
        """Get rating based on benefits score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _suggest_benefits_improvements(self, benefit_analysis: Dict) -> List[str]:
        """Suggest improvements for benefits package."""
        improvements = []
        
        for benefit_type, analysis in benefit_analysis.items():
            if not analysis["provided"]:
                if benefit_type == "health_insurance":
                    improvements.append("Request comprehensive health insurance with minimal deductibles")
                elif benefit_type == "retirement_pension":
                    improvements.append("Negotiate for company pension scheme or retirement contributions")
                elif benefit_type == "vacation_days":
                    improvements.append("Request additional vacation days (15+ is standard)")
                elif benefit_type == "remote_work":
                    improvements.append("Discuss remote work or hybrid options")
                elif benefit_type == "professional_development":
                    improvements.append("Request training sponsorship or development budget")
                elif benefit_type == "bonus_structure":
                    improvements.append("Negotiate for performance-based bonus structure")
            elif analysis["quality"] == "fair":
                improvements.append(f"Consider negotiating better {benefit_type.replace('_', ' ')} terms")
        
        return improvements[:5]
    
    def calculate_total_compensation(self, base_salary: int, benefits: Dict, bonuses: Dict) -> Dict:
        """Calculate total compensation package value."""
        # Simplified calculation
        benefits_value = benefits.get("monetary_value", 0)
        annual_bonus = bonuses.get("annual_bonus", 0)
        signing_bonus = bonuses.get("signing_bonus", 0)
        equity_value = bonuses.get("equity_value", 0)
        
        total_compensation = base_salary + benefits_value + annual_bonus + signing_bonus + equity_value
        
        return {
            "base_salary": base_salary,
            "benefits_value": benefits_value,
            "annual_bonus": annual_bonus,
            "signing_bonus": signing_bonus,
            "equity_value": equity_value,
            "total_compensation": total_compensation,
            "bonus_percentage": round((annual_bonus / base_salary) * 100, 1) if base_salary > 0 else 0,
            "breakdown": {
                "salary_percentage": round((base_salary / total_compensation) * 100, 1) if total_compensation > 0 else 0,
                "benefits_percentage": round((benefits_value / total_compensation) * 100, 1) if total_compensation > 0 else 0,
                "bonus_percentage": round((annual_bonus / total_compensation) * 100, 1) if total_compensation > 0 else 0
            }
        }
