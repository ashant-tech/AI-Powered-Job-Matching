import re
from typing import Dict, List

def analyze_cv_text(cv_text: str) -> Dict:
    """
    Analyze CV text and extract structured information.
    This is a simplified version - in production, you'd use NLP/ML models.
    """
    analysis = {
        "experience": [],
        "education": [],
        "summary": "",
        "contact_info": {}
    }
    
    # Extract contact information
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, cv_text)
    if emails:
        analysis["contact_info"]["email"] = emails[0]
    
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones = re.findall(phone_pattern, cv_text)
    if phones:
        analysis["contact_info"]["phone"] = phones[0]
    
    # Extract experience (simplified pattern matching)
    experience_pattern = r'(?i)(experience|employment|work history)[:\s]*(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
    experiences = re.findall(experience_pattern, cv_text, re.DOTALL)
    for exp in experiences:
        if exp[1].strip():
            analysis["experience"].append({
                "title": "Extracted Position",
                "company": "Extracted Company",
                "description": exp[1].strip()[:200],
                "years": "Not specified"
            })
    
    # Extract education (simplified pattern matching)
    education_pattern = r'(?i)(education|academic|qualification)[:\s]*(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
    educations = re.findall(education_pattern, cv_text, re.DOTALL)
    for edu in educations:
        if edu[1].strip():
            analysis["education"].append({
                "degree": "Extracted Degree",
                "institution": "Extracted Institution",
                "year": "Not specified"
            })
    
    # Generate summary
    analysis["summary"] = f"CV analysis complete. Found {len(analysis['experience'])} experience entries and {len(analysis['education'])} education entries."
    
    return analysis
