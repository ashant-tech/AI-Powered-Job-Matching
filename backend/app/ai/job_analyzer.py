import re

from app.ai.skill_extractor import extract_skills

_MIN_YEARS = re.compile(r"(\d{1,2})\+?\s*(?:years|yrs)", re.IGNORECASE)


def analyze_job(description: str, requirements: str = "") -> tuple[list[str], float]:
    text = f"{description}\n{requirements}"
    skills = extract_skills(text)
    years = [int(m.group(1)) for m in _MIN_YEARS.finditer(text)]
    return skills, float(min(years)) if years else 0.0
