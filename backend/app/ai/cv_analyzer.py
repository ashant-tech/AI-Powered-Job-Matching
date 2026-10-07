import re
from typing import List, Dict, Any


def analyze_cv_text(cv_text: str) -> dict:
    """
    Analyze CV text and extract structured information with enhanced intelligence.
    Uses advanced pattern recognition and contextual analysis.
    """
    analysis = {
        "experience": [],
        "education": [],
        "summary": "",
        "contact_info": {},
        "experience_level": "Not specified",
        "total_years_experience": 0,
        "job_titles": [],
        "key_skills": [],
        "achievements": [],
        "certifications": [],
        "projects": [],
        "languages": [],
        "soft_skills": []
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

    # Extract experience with more detail
    experiences = extract_experience(cv_text)
    analysis["experience"] = experiences

    # Calculate total years of experience
    analysis["total_years_experience"] = calculate_total_experience(experiences)

    # Determine experience level
    analysis["experience_level"] = determine_experience_level(analysis["total_years_experience"])

    # Extract job titles
    analysis["job_titles"] = extract_job_titles(experiences)

    # Extract education with more detail
    educations = extract_education(cv_text)
    analysis["education"] = educations

    # Extract achievements (quantifiable results)
    analysis["achievements"] = extract_achievements(cv_text)

    # Extract certifications
    analysis["certifications"] = extract_certifications(cv_text)

    # Extract projects
    analysis["projects"] = extract_projects(cv_text)

    # Extract languages
    analysis["languages"] = extract_languages(cv_text)

    # Extract technical skills with categorization
    skills_data = extract_enhanced_skills(cv_text)
    analysis["key_skills"] = skills_data["technical"]
    analysis["soft_skills"] = skills_data["soft"]

    # Generate intelligent summary
    analysis["summary"] = generate_intelligent_summary(analysis)

    return analysis


def extract_experience(cv_text: str) -> List[Dict[str, Any]]:
    """Extract work experience with job titles, companies, and dates."""
    experiences = []

    # Pattern for experience entries with dates
    experience_patterns = [
        r'(?i)(?:senior|junior|lead|principal|chief|director|manager|developer|engineer|analyst|consultant|specialist|coordinator|administrator|assistant|intern)[\w\s]*?(?:at|@|for|with)\s+([A-Z][\w\s]+?)(?:\n|,|\(|\.|$)',
        r'(?i)([\w\s]+?(?:developer|engineer|manager|analyst|designer|consultant|specialist)[\w\s]*?)(?:\s+at\s+|\s+@|\s+for\s+)([A-Z][\w\s]+?)(?:\n|,|\(|\.|$)',
    ]

    # Extract job titles
    job_title_keywords = [
        'software engineer', 'developer', 'senior developer', 'junior developer',
        'full stack developer', 'backend developer', 'frontend developer',
        'data scientist', 'machine learning engineer', 'devops engineer',
        'product manager', 'project manager', 'business analyst',
        'systems architect', 'technical lead', 'engineering manager',
        'consultant', 'analyst', 'designer', 'administrator',
        'intern', 'trainee', 'associate', 'assistant'
    ]

    # Simple extraction based on common patterns
    for keyword in job_title_keywords:
        pattern = rf'(?i)(.*?)({keyword}(?:\s+\w+)?)(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
        matches = re.findall(pattern, cv_text, re.DOTALL)
        for match in matches:
            context = match[0] + match[2]
            if len(context.strip()) > 10:
                experiences.append({
                    "title": match[1].strip(),
                    "company": extract_company_name(context),
                    "description": context[:300].strip(),
                    "years": extract_years(context),
                    "start_date": extract_date(context, 'start'),
                    "end_date": extract_date(context, 'end')
                })

    # If no structured matches found, use basic pattern
    if not experiences:
        experience_pattern = r'(?i)(experience|employment|work history)[:\s]*(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
        basic_matches = re.findall(experience_pattern, cv_text, re.DOTALL)
        for exp in basic_matches:
            if exp[1].strip():
                experiences.append({
                    "title": "Position",
                    "company": "Company",
                    "description": exp[1].strip()[:300],
                    "years": "Not specified",
                    "start_date": None,
                    "end_date": None
                })

    return experiences[:10]  # Limit to 10 most recent


def extract_education(cv_text: str) -> List[Dict[str, Any]]:
    """Extract education information with degrees, institutions, and years."""
    educations = []

    # Degree patterns
    degree_patterns = [
        r'(?:Bachelor|Master|PhD|Doctorate|Masters|Bachelors|Associate)(?:\s+(?:of|in)?\s+[\w\s]+?)(?:\n|,|\(|\.|$)',
        r'(?:B\.S\.|M\.S\.|B\.A\.|M\.A\.|Ph\.D\.|MBA)[\w\s]*?(?:\n|,|\(|\.|$)',
    ]

    # Institution patterns
    institution_patterns = [
        r'(?:University|College|Institute|School)(?:\s+of\s+[\w\s]+?)(?:\n|,|\(|\.|$)',
    ]

    # Extract education sections
    education_pattern = r'(?i)(education|academic|qualification)[:\s]*(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
    education_matches = re.findall(education_pattern, cv_text, re.DOTALL)

    for edu_match in education_matches:
        edu_text = edu_match[1]
        if not edu_text.strip():
            continue

        degree = "Degree"
        institution = "Institution"
        year = None

        # Try to extract degree
        for pattern in degree_patterns:
            match = re.search(pattern, edu_text)
            if match:
                degree = match.group(0).strip()
                break

        # Try to extract institution
        for pattern in institution_patterns:
            match = re.search(pattern, edu_text)
            if match:
                institution = match.group(0).strip()
                break

        # Try to extract year
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, edu_text)
        if years:
            year = years[-1]  # Most recent year

        educations.append({
            "degree": degree,
            "institution": institution,
            "year": str(year) if year else "Not specified",
            "field": extract_field_of_study(edu_text)
        })

    return educations[:5]  # Limit to 5 most recent


def extract_company_name(text: str) -> str:
    """Extract company name from text."""
    # Simple pattern - looks for capitalized words that might be company names
    company_pattern = r'(?:at|@|for|with)\s+([A-Z][a-zA-Z\s&]+?)(?:\n|,|\(|\.|$)'
    match = re.search(company_pattern, text)
    if match:
        return match.group(1).strip()
    return "Company"


def extract_years(text: str) -> str:
    """Extract years of experience from text."""
    # Look for patterns like "5 years", "3+ years", etc.
    year_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
    match = re.search(year_pattern, text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} years"
    return "Not specified"


def extract_date(text: str, date_type: str) -> str:
    """Extract start or end date from text."""
    # Look for date patterns
    date_patterns = [
        r'\b(19|20)\d{2}\b',  # Years
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d{2}\b',  # Month Year
    ]

    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))

    if dates:
        if date_type == 'start' and len(dates) > 0:
            return dates[0]
        elif date_type == 'end' and len(dates) > 1:
            return dates[-1]
        elif date_type == 'end' and len(dates) == 1:
            return "Present"

    return None


def extract_field_of_study(text: str) -> str:
    """Extract field of study from education text."""
    field_keywords = [
        'computer science', 'software engineering', 'data science',
        'business administration', 'economics', 'mathematics',
        'physics', 'chemistry', 'biology', 'engineering',
        'arts', 'humanities', 'social sciences'
    ]

    for field in field_keywords:
        if field.lower() in text.lower():
            return field

    return "Not specified"


def calculate_total_experience(experiences: List[Dict[str, Any]]) -> int:
    """Calculate total years of experience from experience entries."""
    total = 0
    for exp in experiences:
        years_str = exp.get('years', '0')
        # Extract number from years string
        match = re.search(r'(\d+)', years_str)
        if match:
            total += int(match.group(1))
    return total


def determine_experience_level(total_years: int) -> str:
    """Determine experience level based on total years."""
    if total_years == 0:
        return "Entry Level"
    elif total_years <= 2:
        return "Junior"
    elif total_years <= 5:
        return "Mid-Level"
    elif total_years <= 10:
        return "Senior"
    else:
        return "Executive/Expert"


def extract_job_titles(experiences: List[Dict[str, Any]]) -> List[str]:
    """Extract unique job titles from experience."""
    titles = set()
    for exp in experiences:
        title = exp.get('title', '').strip()
        if title and title != "Position":
            titles.add(title)
    return list(titles)


def generate_intelligent_summary(analysis: dict) -> str:
    """Generate an intelligent summary of the CV."""
    exp_count = len(analysis["experience"])
    edu_count = len(analysis["education"])
    total_years = analysis["total_years_experience"]
    exp_level = analysis["experience_level"]
    job_titles = analysis["job_titles"][:3]  # Top 3 titles

    summary_parts = []

    if exp_count > 0:
        summary_parts.append(f"Professional with {total_years}+ years of experience ({exp_level} level)")
        if job_titles:
            summary_parts.append(f"Background includes roles such as {', '.join(job_titles)}")

    if edu_count > 0:
        summary_parts.append(f"Holds {edu_count} educational qualification(s)")

    if not summary_parts:
        return "CV analysis complete. Profile information extracted."

    return ". ".join(summary_parts) + "."


def extract_achievements(cv_text: str) -> List[str]:
    """Extract quantifiable achievements from CV text."""
    achievements = []
    
    # Look for patterns with numbers and results
    achievement_patterns = [
        r'(?:increased|reduced|improved|achieved|delivered|saved|generated)\s+(?:by|to)?\s*(?:\d+%|\$\d+|\d+)',
        r'(?:led|managed|directed|supervised)\s+(?:a\s+)?\d+(?:\s+(?:person|people|team|member|developer|employee))?',
        r'(?:built|created|developed|launched|implemented)\s+(?:a\s+)?\w+(?:\s+(?:system|platform|application|tool|solution))?',
    ]
    
    for pattern in achievement_patterns:
        matches = re.findall(pattern, cv_text, re.IGNORECASE)
        achievements.extend(matches)
    
    return achievements[:10]  # Return top 10


def extract_certifications(cv_text: str) -> List[str]:
    """Extract certifications from CV text."""
    certifications = []
    
    # Common certification keywords
    cert_keywords = [
        'certified', 'certification', 'certificate', 'AWS', 'PMP', 'Scrum',
        'CCNA', 'MCSE', 'Oracle', 'Google Cloud', 'Microsoft', 'CompTIA',
        'CISSP', 'CEH', 'ITIL', 'PRINCE2', 'Six Sigma', 'ISO'
    ]
    
    # Look for certification patterns
    for keyword in cert_keywords:
        if keyword.lower() in cv_text.lower():
            # Extract the full certification context
            pattern = rf'(?:[A-Z][a-z]+\s+)?{keyword}(?:\s+[A-Z][a-z]+)?'
            matches = re.findall(pattern, cv_text, re.IGNORECASE)
            certifications.extend(matches)
    
    return list(set(certifications))[:10]  # Remove duplicates, return top 10


def extract_projects(cv_text: str) -> List[str]:
    """Extract project information from CV text."""
    projects = []
    
    # Look for project indicators
    project_indicators = ['project', 'built', 'developed', 'created', 'launched', 'implemented']
    
    for indicator in project_indicators:
        # Simple extraction - in production, use more sophisticated NLP
        if indicator in cv_text.lower():
            pattern = rf'{indicator}\s+[A-Z][^.,;]+'
            matches = re.findall(pattern, cv_text, re.IGNORECASE)
            projects.extend(matches)
    
    return projects[:8]  # Return top 8


def extract_languages(cv_text: str) -> List[str]:
    """Extract language skills from CV text."""
    languages = []
    
    # Common languages
    common_languages = [
        'english', 'amharic', 'french', 'german', 'spanish', 'chinese',
        'japanese', 'arabic', 'portuguese', 'russian', 'italian', 'dutch'
    ]
    
    for lang in common_languages:
        if lang in cv_text.lower():
            languages.append(lang.capitalize())
    
    return languages


def extract_enhanced_skills(cv_text: str) -> Dict[str, List[str]]:
    """Extract and categorize skills into technical and soft skills."""
    technical_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'go',
        'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
        'git', 'linux', 'windows', 'macos', 'android', 'ios', 'machine learning',
        'data science', 'ai', 'artificial intelligence', 'deep learning', 'nlp',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'microservices', 'rest api',
        'graphql', 'html', 'css', 'sass', 'webpack', 'vite', 'next.js', 'nuxt.js'
    ]
    
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'collaboration', 'problem solving',
        'critical thinking', 'time management', 'adaptability', 'creativity', 'innovation',
        'mentoring', 'training', 'presentation', 'negotiation', 'decision making',
        'strategic thinking', 'analytical', 'detail-oriented', 'organized', 'flexible',
        'proactive', 'self-motivated', 'customer service', 'interpersonal', 'management'
    ]
    
    found_technical = []
    found_soft = []
    
    cv_lower = cv_text.lower()
    
    for skill in technical_skills:
        if skill in cv_lower:
            found_technical.append(skill.capitalize())
    
    for skill in soft_skills:
        if skill in cv_lower:
            found_soft.append(skill.capitalize())
    
    return {
        "technical": found_technical,
        "soft": found_soft
    }
