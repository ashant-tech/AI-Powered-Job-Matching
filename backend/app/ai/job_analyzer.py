import re

import json

def analyze_job_description(job_description: str) -> dict:
    """
    Analyze job description and extract structured information.
    """
    analysis = {
        "required_skills": [],
        "preferred_skills": [],
        "experience_level": "",
        "education_requirements": [],
        "responsibilities": [],
        "benefits": []
    }
    
    text_lower = job_description.lower()
    
    # Extract experience level
    experience_patterns = {
        "entry": ["entry level", "junior", "0-1 year", "0-2 years"],
        "mid": ["mid level", "mid-senior", "2-5 years", "3-5 years", "intermediate"],
        "senior": ["senior", "5+ years", "7+ years", "10+ years", "lead", "principal"]
    }
    
    for level, patterns in experience_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                analysis["experience_level"] = level
                break
        if analysis["experience_level"]:
            break
    
    # Extract responsibilities (simplified)
    responsibility_pattern = r'(?i)(responsibilities|duties|what you\'ll do)[:\s]*(.*?)(?=\n\n|\nrequirements|qualification|$)'
    responsibilities = re.findall(responsibility_pattern, job_description, re.DOTALL)
    for resp in responsibilities:
        if resp[1].strip():
            # Split by common delimiters
            items = re.split(r'[\n•\-\*]', resp[1].strip())
            for item in items:
                if item.strip() and len(item.strip()) > 10:
                    analysis["responsibilities"].append(item.strip()[:100])
    
    # Extract benefits
    benefit_pattern = r'(?i)(benefits|perks|what we offer)[:\s]*(.*?)(?=\n\n|\nrequirements|qualification|$)'
    benefits = re.findall(benefit_pattern, job_description, re.DOTALL)
    for benefit in benefits:
        if benefit[1].strip():
            items = re.split(r'[\n•\-\*]', benefit[1].strip())
            for item in items:
                if item.strip() and len(item.strip()) > 5:
                    analysis["benefits"].append(item.strip()[:100])
    
    return analysis

def extract_job_skills(job_description: str, requirements: str = None) -> list[str]:
    """
    Extract skills from job description and requirements.
    """
    from app.ai.skill_extractor import extract_skills
    
    combined_text = job_description
    if requirements:
        combined_text += " " + requirements
    
    return extract_skills(combined_text)

def calculate_job_complexity(job_description: str) -> str:
    """
    Estimate job complexity based on description.
    """
    text_lower = job_description.lower()
    
    complexity_indicators = {
        "high": ["architecture", "design", "lead", "senior", "principal", "strategy", "optimization"],
        "medium": ["develop", "implement", "maintain", "support", "coordinate"],
        "low": ["assist", "support", "help", "learn", "training"]
    }
    
    scores = {"high": 0, "medium": 0, "low": 0}
    
    for level, indicators in complexity_indicators.items():
        for indicator in indicators:
            if indicator in text_lower:
                scores[level] += 1
    
    if scores["high"] > scores["medium"] and scores["high"] > scores["low"]:
        return "high"
    elif scores["medium"] > scores["low"]:
        return "medium"
    else:
        return "low"
