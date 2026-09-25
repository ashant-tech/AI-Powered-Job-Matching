"""
Telegram Job Source - real collection via public t.me/s/<channel> web previews.

Each channel's web preview page (https://t.me/s/<username>) serves the ~20 most
recent posts as plain HTML, so no bot token or Telegram API access is required.
Only verified channels that publish structured Ethiopian vacancy posts are kept.
"""
import json
import logging
import os
import re
import sys
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
import urllib3

# Share the backend deadline parser (label + date extraction, Amharic aware)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.deadline_parser import extract_deadline

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Channels verified to respond with structured vacancy posts (2026-09).
# Deliberately small: a few high-quality feeds beat many noisy ones.
CHANNELS = [
    {"name": "Ethiojobs Official", "username": "ethiojobsofficial"},
    {"name": "HaHuJobs", "username": "hahujobs"},
    {"name": "Dereja", "username": "Derejaofficial"},
    {"name": "Enjera Jobs", "username": "enjerajobs"},
    {"name": "Shega Jobs", "username": "shegajobs"},
    {"name": "Ethio Job Vacancy", "username": "ethio_job_vacancy1"},
]

# A message must mention at least one of these to count as a vacancy post
# (filters out promos, greetings and channel advertisements).
_JOB_SIGNALS = (
    "deadline", "position", "qualification", "requirement", "experience",
    "responsibilit", "employment type", "career level", "how to apply",
    "salary", "vacancy", "መዘጊያ", "ሥራ", "ስራ",
)

_LABEL_KEYS = {
    "company": "company", "company name": "company", "organization": "company",
    "organisation": "company", "employer": "company", "institution": "company",
    "location": "location", "place": "location", "city": "location",
    "job location": "location", "work location": "location", "address": "location",
    "employment type": "job_type", "job type": "job_type", "employment": "job_type",
    "position": "title", "job title": "title", "vacancy title": "title",
}

_CITY_TAGS = {
    "addis ababa", "addisababa", "adama", "nazret", "hawassa", "awassa",
    "dire dawa", "diredawa", "bahir dar", "bahirdar", "mekelle", "gondar",
    "jimma", "dessie", "arba minch", "arbaminch", "jijiga", "harar",
    "semera", "assosa", "asossa", "wolkite", "hodan", "bole", "piassa",
}

# Tags that describe the vacancy category, not the employer
_GENERIC_TAGS = {
    "job", "jobs", "vacancy", "vacancies", "hiring", "hire", "ethiopia",
    "ethiopian", "ethiojobs", "hahujobs", "career", "careers", "employment",
    "recruitment", "recruit", "apply", "application", "fulltime", "full time",
    "parttime", "part time", "contract", "internship", "ngo", "remote",
    "banking", "finance", "accounting", "accountant", "it", "technology",
    "tech", "sales", "marketing", "management", "engineering", "health",
    "education", "construction", "logistics", "procurement", "hr",
    "administrative", "admin", "customer service", "manufacturing",
    "agriculture", "media", "communication", "legal", "security", "fresh",
    "graduate", "experience", "experienced", "urgent", "new", "business",
    "skilled worker", "medium skilled worker",
}

_SKILL_KEYWORDS = (
    "accounting", "finance", "audit", "taxation", "banking", "procurement",
    "logistics", "supply chain", "marketing", "sales", "customer service",
    "communication", "project management", "monitoring and evaluation", "m&e",
    "grants", "fundraising", "human resources", "recruitment", "administration",
    "data entry", "excel", "powerpoint", "ms office", "quickbooks", "peachtree",
    "python", "java", "javascript", "sql", "web development",
    "mobile development", "networking", "it support", "software", "engineering",
    "civil engineering", "electrical", "mechanical", "autocad", "construction",
    "architecture", "surveying", "teaching", "lecturing", "education", "nursing",
    "midwifery", "pharmacy", "public health", "laboratory", "agriculture",
    "agronomy", "veterinary", "driving", "security", "journalism", "media",
    "graphic design", "video editing", "translation", "amharic", "english",
    "french", "leadership", "problem solving", "teamwork", "time management",
    "negotiation", "report writing", "business development", "business analysis",
    "quality assurance", "quality control", "hospitality", "maintenance",
)

_JOB_TYPE_PATTERNS = (
    ("full time", "full-time"), ("full-time", "full-time"),
    ("part time", "part-time"), ("part-time", "part-time"),
    ("contract", "contract"), ("internship", "internship"),
    ("temporary", "temporary"), ("consultant", "contract"),
)

_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF"
    "\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF"
    "\U0001F1E6-\U0001F1FF\u2B00-\u2BFF\uFE0F\u200D\u20E3]+"
)

_REQUIREMENTS_RE = re.compile(
    r"(?:(?:job\s+)?(?:requirements?|qualifications?)|duties\s+and\s+responsibilities?|"
    r"required\s+(?:skills|qualifications)|responsibilit(?:y|ies))"
    r"[^\S\n]*:?\s*\n?",
    re.IGNORECASE,
)


class TelegramJobSource:
    """Collects real job posts from public Telegram channel web previews."""

    def __init__(self, channels: Optional[List[Dict]] = None):
        self.channels = channels or CHANNELS

    @property
    def name(self):
        return "Telegram Channels"

    def fetch_jobs(self) -> List[Dict]:
        jobs: List[Dict] = []
        for channel in self.channels:
            try:
                channel_jobs = self._fetch_channel(channel)
                jobs.extend(channel_jobs)
                logger.info("@%s: collected %d jobs", channel["username"], len(channel_jobs))
            except requests.RequestException as exc:
                logger.error("Failed to fetch @%s: %s", channel["username"], exc)
            except Exception as exc:
                logger.exception("Unexpected error on @%s: %s", channel["username"], exc)
            time.sleep(1)  # be polite to t.me between channels
        logger.info("Total jobs collected from Telegram: %d", len(jobs))
        return jobs

    def _fetch_channel(self, channel: Dict) -> List[Dict]:
        response = self._get(f"https://t.me/s/{channel['username']}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = []
        for message in soup.find_all(attrs={"data-post": True}):
            text_el = message.select_one(".tgme_widget_message_text")
            if text_el is None:
                continue
            text = text_el.get_text("\n", strip=True)
            post_id = str(message.get("data-post", "")).rsplit("/", 1)[-1]
            job = self._parse_message(text, channel, post_id)
            if job:
                jobs.append(job)
        return jobs

    @staticmethod
    def _get(url: str) -> requests.Response:
        try:
            return requests.get(url, headers=_HEADERS, timeout=30)
        except requests.exceptions.SSLError:
            # Some corporate networks intercept TLS with their own CA; the
            # payload here is public job listings, so retry without verification.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("TLS verification failed for %s; retrying unverified", url)
            return requests.get(url, headers=_HEADERS, timeout=30, verify=False)

    def _parse_message(self, text: str, channel: Dict, post_id: str) -> Optional[Dict]:
        if not text or not post_id.isdigit():
            return None
        lowered = text.lower()
        if not any(signal in lowered for signal in _JOB_SIGNALS):
            return None

        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        if len(lines) < 3:
            return None

        merged = _merge_label_lines(lines)
        fields, body_lines = _split_fields(merged)

        title = _clean_title(fields.get("title") or (body_lines[0] if body_lines else lines[0]))
        if not title:
            return None

        company = _extract_company(fields, body_lines, text) or channel["name"]
        company_tag = _company_hashtag(text)
        location = fields.get("location") or _city_from_hashtags(text) or _city_from_text(lowered) or "Ethiopia"
        job_type = _normalize_job_type(fields.get("job_type")) or _job_type_from_text(lowered)
        skills = _extract_skills(lowered, text, company_tag)

        description = text if len(text) <= 4000 else text[:3997] + "..."
        requirements = _extract_requirements(text) or _requirements_fallback(body_lines, title)
        return {
            "title": title,
            "company": company,
            "description": description,
            "requirements": requirements,
            "skills": skills,
            "location": location,
            "job_type": job_type,
            "source": f"Telegram: @{channel['username']}",
            "source_url": f"https://t.me/{channel['username']}/{post_id}",
            "external_id": f"tg-{channel['username'].lower()}-{post_id}",
        }


def _merge_label_lines(lines: List[str]) -> List[str]:
    """Join 'Label' + ': value' and 'Label:' + 'value' line pairs so label
    parsing works across both posting styles."""
    merged = []
    i = 0
    while i < len(lines):
        current = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if nxt and nxt.startswith(":") and len(current) <= 40:
            merged.append(f"{current} {nxt}")
            i += 2
        elif current.endswith(":") and nxt and not nxt.endswith(":") and len(current) <= 40:
            merged.append(f"{current} {nxt}")
            i += 2
        else:
            merged.append(current)
            i += 1
    return merged


def _split_fields(merged: List[str]) -> tuple[Dict[str, str], List[str]]:
    fields: Dict[str, str] = {}
    body: List[str] = []
    for line in merged:
        label, sep, value = line.partition(":")
        key = _LABEL_KEYS.get(label.strip().lower())
        value = value.strip()
        if sep and key and value and len(label.strip()) <= 40:
            fields[key] = value
        else:
            body.append(line)
    return fields, body


def _clean_title(raw: str) -> Optional[str]:
    title = _EMOJI_RE.sub("", raw or "")
    title = re.sub(r"^[\s#*\-–—•·!.:]+", "", title)
    title = re.sub(r"[\s\-–—:·.!]+$", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    if 4 <= len(title) <= 120:
        return title
    return None


def _company_hashtag(text: str) -> Optional[str]:
    """First hashtag that names the employer (not a category, city or filler)."""
    for tag in re.findall(r"#(\w+)", text):
        if _tag_is_noise(tag):
            continue
        value = _camel_to_words(tag)
        if value and value.lower() not in _GENERIC_TAGS and value.lower() not in _CITY_TAGS:
            return value
    return None


def _tag_is_noise(tag: str) -> bool:
    """Experience counters (#3_years) and similar meta hashtags."""
    return bool(re.search(r"\d", tag)) or tag.lower().endswith(("year", "years"))


def _extract_company(fields: Dict[str, str], body_lines: List[str], text: str) -> Optional[str]:
    if fields.get("company"):
        return _clean_title(fields["company"])
    # ethiojobsofficial style: second line reads "at Company Name"
    for line in body_lines[:3]:
        match = re.match(r"(?i)^at\s+(.{3,80})$", line.strip())
        if match:
            company = _clean_title(match.group(1))
            if company:
                return company
    # hahujobs style: employer is the first non-generic hashtag
    return _company_hashtag(text)


def _camel_to_words(tag: str) -> str:
    words = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z]+|[a-z]+|\d+", tag)
    return " ".join(words)


def _city_from_hashtags(text: str) -> Optional[str]:
    for tag in re.findall(r"#(\w+)", text):
        value = _camel_to_words(tag)
        if value.lower() in _CITY_TAGS:
            return value
    return None


def _city_from_text(lowered: str) -> Optional[str]:
    for city in _CITY_TAGS:
        if city in lowered:
            return city.title() if city.islower() else city
    return None


def _normalize_job_type(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    lowered = value.lower()
    for needle, job_type in _JOB_TYPE_PATTERNS:
        if needle in lowered:
            return job_type
    return value.strip().lower() or None


def _job_type_from_text(lowered: str) -> Optional[str]:
    for needle, job_type in _JOB_TYPE_PATTERNS:
        if needle in lowered:
            return job_type
    return None


def _extract_requirements(text: str) -> Optional[str]:
    match = _REQUIREMENTS_RE.search(text)
    if not match:
        return None
    chunk = text[match.end():match.end() + 800].strip()
    return chunk[:800] or None


def _requirements_fallback(body_lines: List[str], title: str) -> Optional[str]:
    """hahujobs posts state the qualification right after the hashtag block."""
    for line in body_lines:
        if line.startswith("#") or line.lower() == (title or "").lower():
            continue
        if len(line) > 20:
            return line[:800]
    return None


def _extract_skills(lowered: str, text: str, company_tag: Optional[str]) -> Optional[str]:
    skills = _find_skills(lowered, text, company_tag)
    return json.dumps(skills) if skills else None


def _find_skills(lowered: str, text: str, company_tag: Optional[str]) -> List[str]:
    skills: List[str] = []
    for skill in _SKILL_KEYWORDS:
        if skill not in skills and _text_mentions_skill(lowered, skill):
            skills.append(skill)
    for tag in re.findall(r"#(\w+)", text):
        if _tag_is_noise(tag):
            continue
        value = _camel_to_words(tag).lower()
        if (
            value
            and len(value.split()) <= 3
            and value not in skills
            and value not in _GENERIC_TAGS
            and value not in _CITY_TAGS
            and (not company_tag or value != company_tag.lower())
        ):
            skills.append(value)
    return skills


def _text_mentions_skill(lowered: str, skill: str) -> bool:
    if re.fullmatch(r"[\w\s&]+", skill):
        return re.search(rf"\b{re.escape(skill)}\b", lowered) is not None
    return skill in lowered
