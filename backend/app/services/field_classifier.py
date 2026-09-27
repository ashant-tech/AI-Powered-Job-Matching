"""Keyword-based classifier mapping jobs and user departments to broad fields.

Fields are intentionally coarse (computer_it, engineering, health, ...) so a
user's department ("Computer Science", "Software Engineering", "IT") and a job
posting ("Junior Backend Developer") land in the same bucket.
"""
import json
import re
from typing import Optional

FIELDS = (
    "computer_it",
    "engineering",
    "health",
    "business_finance",
    "education",
    "law",
    "agriculture",
    "hospitality",
    "media_design",
    "other",
)

FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "computer_it": (
        "software", "developer", "development", "programmer", "programming",
        "python", "java", "javascript", "typescript", "react", "node",
        "web developer", "frontend", "backend", "full stack", "fullstack",
        "database", "sql", "nosql", "data analyst", "data science",
        "data scientist", "data engineer", "machine learning", "ai",
        "artificial intelligence", "cybersecurity", "cyber security",
        "information security", "network", "networking", "system admin",
        "sysadmin", "devops", "cloud", "aws", "azure", "it support",
        "it officer", "it specialist", "information technology",
        "computer", "computing", "informatics", "hardware", "helpdesk",
        "help desk", "technical support", "erp", "sap", "digital",
        "web designer", "ux", "ui developer", "mobile app", "android",
        "ios developer", "flutter", "blockchain", "qa engineer",
        "quality assurance engineer", "scrum", "agile", "git",
    ),
    "engineering": (
        "engineer", "engineering", "civil", "structural", "mechanical",
        "electrical", "electronics", "construction", "site engineer",
        "surveyor", "quantity surveyor", "maintenance engineer",
        "production engineer", "industrial engineer", "power", "energy",
        "hvac", "plumbing", "welding", "cad", "autocad", "design engineer",
        "project engineer", "field engineer", "telecom engineer",
    ),
    "health": (
        "nurse", "nursing", "doctor", "physician", "medical", "medicine",
        "health", "clinic", "clinical", "hospital", "patient", "pharmacy",
        "pharmacist", "midwife", "surgeon", "surgery", "dental", "dentist",
        "laboratory technician", "lab technician", "radiology", "physio",
        "therapist", "public health", "epidemiolog", "nutrition",
        "optometr", "anesthe", "paramedic", "caregiver", "midwifery",
    ),
    "business_finance": (
        "account", "accountant", "accounting", "finance", "financial",
        "bank", "banking", "audit", "auditor", "business", "sales",
        "marketing", "manager", "management", "hr", "human resource",
        "recruit", "admin", "administration", "logistics", "supply chain",
        "procurement", "purchasing", "economist", "economics", "cashier",
        "bookkeep", "tax", "treasur", "investment", "insurance", "trade",
        "export", "import", "warehouse", "storekeeper", "secretary",
        "executive assistant", "office assistant", "receptionist",
        "customer service", "call center", "business development",
        "project manager", "program manager", "operations",
    ),
    "education": (
        "teacher", "teaching", "education", "educator", "school",
        "lecturer", "academic", "curriculum", "tutor", "instructor",
        "kindergarten", "pedagog", "student", "university", "college",
        "librarian", "library",
    ),
    "law": (
        "lawyer", "legal", "law", "attorney", "judiciary", "judge",
        "court", "paralegal", "notary", "compliance officer", "arbitrat",
    ),
    "agriculture": (
        "agricultur", "agronom", "crop", "livestock", "farm", "farming",
        "irrigation", "veterinar", "animal health", "soil", "horticultur",
        "forestry", "fishery", "poultry", "dairy", "bee", "apicul",
    ),
    "hospitality": (
        "hotel", "restaurant", "chef", "cook", "waiter", "waitress",
        "bartender", "barista", "tourism", "tour guide", "hospitality",
        "catering", "banquet", "housekeep", "front office", "concierge",
    ),
    "media_design": (
        "designer", "graphic", "graphics", "media", "journalis",
        "reporter", "content creator", "content writer", "copywriter",
        "video", "photograph", "editor", "editorial", "art director",
        "creative", "illustrat", "public relations", "communications officer",
        "social media", "broadcast", "radio", "tv", "writer",
    ),
}

# Extra aliases that only make sense for departments, not job ads
DEPARTMENT_ALIASES: dict[str, tuple[str, ...]] = {
    "computer_it": (
        "computer science", "computer engineering", "software engineering",
        "information system", "information science", "it", "ict",
        "software", "cyber", "data",
    ),
    "engineering": (
        "civil engineering", "mechanical engineering",
        "electrical engineering", "chemical engineering", "engineering",
        "construction technology", "water supply", "hydraulic",
    ),
    "health": (
        "nursing", "public health", "pharmacy", "physician", "health",
        "medical", "clinical",
    ),
    "business_finance": (
        "economics", "accounting", "management", "business administration",
        "finance", "banking", "marketing management", "logistics",
    ),
    "education": ("education", "teaching", "curriculum", "pedagogy"),
    "law": ("law", "legal studies", "juris"),
    "agriculture": ("agriculture", "agricultural", "agronomy", "veterinary",
                    "animal science", "natural resource"),
    "hospitality": ("hotel management", "tourism", "catering",
                    "food science"),
    "media_design": ("journalism", "communication", "media", "design",
                     "fine art", "graphics"),
}

_WORD_RE = re.compile(r"[a-z0-9+#]+")

# Tokens that signal a computing discipline. Used only to disambiguate
# "computer/software engineering" (which belongs in computer_it) from generic
# engineering (civil/mechanical/electrical).
_COMPUTER_SIGNAL_TOKENS = {
    "computer", "computing", "software", "informatics", "ict", "cyber",
    "programming", "programmer", "developer", "data",
}

# Per-section hit weights: titles are decisive, skills strong, description weak
# (long postings mention many unrelated keywords).
_TITLE_WEIGHT = 5.0
_SKILLS_WEIGHT = 3.0
_TEXT_WEIGHT = 1.0


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _count_hits(keywords: tuple[str, ...], text_lower: str, tokens: set[str]) -> int:
    hits = 0
    for kw in keywords:
        if " " in kw:
            if kw in text_lower:
                hits += 1
        elif len(kw) <= 4:
            # short/ambiguous words ("it", "ai", "hr") need an exact token
            if kw in tokens:
                hits += 1
        else:
            # longer keywords match as token prefixes so stems work
            # ("agricultur" -> "agriculture", "journalis" -> "journalism")
            if any(token.startswith(kw) for token in tokens):
                hits += 1
    return hits


def _score_fields(keyword_sets: dict[str, tuple[str, ...]],
                  prepared: list[tuple[str, set[str]]],
                  weights: list[float]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for field, keywords in keyword_sets.items():
        score = 0.0
        for (text_lower, tokens), weight in zip(prepared, weights):
            score += weight * _count_hits(keywords, text_lower, tokens)
        scores[field] = score
    return scores


def _best_field(keyword_sets: dict[str, tuple[str, ...]], sections: list[tuple[str, float]]) -> str:
    """sections: list of (text, weight). Returns the highest-scoring field."""
    prepared = [(text.lower(), _tokens(text)) for text, _ in sections]
    weights = [weight for _, weight in sections]
    scores = _score_fields(keyword_sets, prepared, weights)

    best_field = max(scores, key=lambda f: scores[f])
    if scores[best_field] <= 0:
        return "other"

    # "Computer engineering" / "software engineering" score high on the generic
    # word "engineering", but they are computing disciplines. When computing is
    # a competitive alternative, prefer computer_it over engineering.
    if best_field == "engineering" and "computer_it" in scores:
        all_tokens = set().union(*(tokens for _, tokens in prepared)) if prepared else set()
        comp, eng = scores["computer_it"], scores["engineering"]
        if comp > 0 and comp >= 0.5 * eng and (all_tokens & _COMPUTER_SIGNAL_TOKENS):
            return "computer_it"

    return best_field


def classify_text(text: str, title: str = "", department_mode: bool = False) -> str:
    """Classify free text into one of FIELDS. Returns 'other' when unclear."""
    if not text and not title:
        return "other"
    keyword_sets = FIELD_KEYWORDS
    if department_mode:
        keyword_sets = {
            field: FIELD_KEYWORDS[field] + DEPARTMENT_ALIASES.get(field, ())
            for field in FIELD_KEYWORDS
        }
    return _best_field(keyword_sets, [(title, _TITLE_WEIGHT), (text, _TEXT_WEIGHT)])


def classify_job(title: str, description: str = "", skills_json: str = "",
                 requirements: str = "") -> str:
    """Classify a job posting into a field. Title/skills weigh most.

    Description/requirements are truncated and weighted low: long postings
    mention many unrelated keywords that otherwise drown out the title.
    """
    skills_text = ""
    if skills_json:
        try:
            parsed = json.loads(skills_json)
            if isinstance(parsed, list):
                skills_text = " ".join(str(s) for s in parsed)
        except (json.JSONDecodeError, TypeError):
            skills_text = str(skills_json)

    return _best_field(FIELD_KEYWORDS, [
        (title or "", _TITLE_WEIGHT),
        (skills_text, _SKILLS_WEIGHT),
        (f"{(requirements or '')[:200]} {(description or '')[:300]}", _TEXT_WEIGHT),
    ])


def normalize_department(department: Optional[str]) -> Optional[str]:
    """Map a user-entered department/field of study to a FIELDS value.

    Returns None for empty input so callers can treat 'no department set'
    distinctly from 'other'.
    """
    if not department or not department.strip():
        return None
    return classify_text(department, department_mode=True)


def _json_to_text(value: Optional[str]) -> str:
    """Flatten a JSON list of strings or dicts into plain text."""
    if not value:
        return ""
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return str(value)
    if isinstance(parsed, list):
        parts = []
        for item in parsed:
            if isinstance(item, dict):
                parts.extend(str(v) for v in item.values() if v)
            elif item:
                parts.append(str(item))
        return " ".join(parts)
    return str(parsed)


def classify_cv(parsed_text: str = "", skills_json: str = "",
                education_json: str = "") -> str:
    """Detect a CV owner's field from their CV — no manual input needed.

    Education is weighted highest (it usually names the department, e.g.
    "BSc in Computer Science"), then skills, then the full text.
    """
    education_text = _json_to_text(education_json)
    skills_text = _json_to_text(skills_json)

    keyword_sets = {
        field: FIELD_KEYWORDS[field] + DEPARTMENT_ALIASES.get(field, ())
        for field in FIELD_KEYWORDS
    }
    return _best_field(keyword_sets, [
        (education_text, 4.0),
        (skills_text, 3.0),
        ((parsed_text or "")[:2000], 1.0),
    ])


def field_matches(job_field: Optional[str], user_field: Optional[str], strict: bool = False) -> bool:
    """Whether a job belongs in a user's feed.

    Non-strict (browsing): jobs classified as 'other' are kept for everyone
    (many postings like 'driver' or 'cleaner' are genuinely cross-field), and
    users without a detected field see everything.

    Strict (personalized "for you" feeds): when the user's field is known, only
    jobs in that exact field are shown — generic 'other' jobs are excluded so the
    feed stays highly relevant to the user's department/related field. Users with
    no detected field still see everything.
    """
    if not user_field or user_field == "other":
        return True
    if strict:
        return job_field == user_field
    if not job_field or job_field == "other":
        return True
    return job_field == user_field
