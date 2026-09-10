import re
from datetime import date

from app.ai.skill_extractor import extract_skills
from app.schemas.cv import CVAnalysis

_DEGREE = re.compile(
    r"\b(bachelor|master|ph\.?d|doctorate|b\.?sc|m\.?sc|b\.?a\b|m\.?a\b|mba|b\.?eng|m\.?eng|diploma|associate)[^\n]{0,120}",
    re.IGNORECASE,
)
_YEAR_RANGE = re.compile(r"((?:19|20)\d{2})\s*(?:-|–|to)\s*((?:19|20)\d{2}|present|current|now)", re.IGNORECASE)
_YEARS_EXP = re.compile(r"(\d{1,2})\+?\s*(?:years|yrs)\s+(?:of\s+)?experience", re.IGNORECASE)
_EXPERIENCE_HEADER = re.compile(r"^(work\s+)?experience|employment( history)?|professional background", re.IGNORECASE)
_SECTION_HEADER = re.compile(r"^(education|skills|projects|certifications|references|summary|languages)\b", re.IGNORECASE)


def _extract_education(text: str) -> list[str]:
    return list(dict.fromkeys(m.group(0).strip() for m in _DEGREE.finditer(text)))[:10]


def _extract_experience(text: str) -> list[str]:
    entries: list[str] = []
    in_section = False
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if _EXPERIENCE_HEADER.match(stripped):
            in_section = True
            continue
        if in_section and _SECTION_HEADER.match(stripped):
            in_section = False
        if in_section and (_YEAR_RANGE.search(stripped) or (len(stripped) < 80 and stripped[0].isupper())):
            entries.append(stripped)
    if not entries:
        entries = [m.group(0) for m in _YEAR_RANGE.finditer(text)]
    return entries[:15]


def _estimate_years(text: str) -> float:
    explicit = [int(m.group(1)) for m in _YEARS_EXP.finditer(text)]
    if explicit:
        return float(max(explicit))
    total = 0
    current_year = date.today().year
    for m in _YEAR_RANGE.finditer(text):
        start = int(m.group(1))
        end_token = m.group(2).lower()
        end = current_year if end_token in {"present", "current", "now"} else int(end_token)
        if end >= start:
            total += end - start
    return float(min(total, 40))


def _summarize(text: str, skills: list[str], years: float) -> str:
    first = next((line for line in text.split("\n") if len(line) > 40), "")
    skill_str = ", ".join(skills[:6]) if skills else "no recognised skills"
    return f"{first[:200]} Approximately {years:g} years of experience; key skills: {skill_str}."


def analyze_cv(text: str) -> CVAnalysis:
    skills = extract_skills(text)
    years = _estimate_years(text)
    return CVAnalysis(
        skills=skills,
        education=_extract_education(text),
        experience=_extract_experience(text),
        years_of_experience=years,
        summary=_summarize(text, skills, years),
    )
