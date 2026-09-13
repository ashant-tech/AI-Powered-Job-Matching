import re


# Common technical skills to look for
TECHNICAL_SKILLS = [
    "python", "javascript", "java", "c++", "c#", "ruby", "php", "swift", "kotlin",
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
    "sql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
    "git", "jenkins", "ci/cd", "agile", "scrum", "jira",
    "machine learning", "deep learning", "data science", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "html", "css", "sass", "less", "typescript", "graphql", "rest api",
    "linux", "windows", "macos", "bash", "shell scripting"
]

# Common soft skills
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", "critical thinking",
    "time management", "adaptability", "creativity", "collaboration", "decision making",
    "project management", "analytical", "strategic thinking", "mentoring", "coaching"
]

def extract_skills(text: str) -> list[str]:
    """
    Extract skills from CV text using pattern matching.
    In production, this would use NLP/ML models for better accuracy.
    """
    text_lower = text.lower()
    found_skills = []
    
    # Check for technical skills
    for skill in TECHNICAL_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Check for soft skills
    for skill in SOFT_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Look for skill patterns like "proficient in X", "experienced with Y"
    skill_patterns = [
        r'proficient\s+in\s+([a-zA-Z\s]+)',
        r'experienced\s+with\s+([a-zA-Z\s]+)',
        r'skilled\s+in\s+([a-zA-Z\s]+)',
        r'knowledge\s+of\s+([a-zA-Z\s]+)',
        r'familiar\s+with\s+([a-zA-Z\s]+)'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            skill = match.strip()
            if len(skill) > 2 and skill not in found_skills:
                found_skills.append(skill)
    
    # Remove duplicates and sort
    found_skills = list(set(found_skills))
    found_skills.sort()
    
    return found_skills

def categorize_skills(skills: list[str]) -> dict:
    """
    Categorize skills into technical and soft skills.
    """
    categorized = {
        "technical": [],
        "soft": [],
        "other": []
    }
    
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in [s.lower() for s in TECHNICAL_SKILLS]:
            categorized["technical"].append(skill)
        elif skill_lower in [s.lower() for s in SOFT_SKILLS]:
            categorized["soft"].append(skill)
        else:
            categorized["other"].append(skill)
    
    return categorized
