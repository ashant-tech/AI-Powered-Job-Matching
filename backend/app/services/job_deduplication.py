import re
from difflib import SequenceMatcher
from typing import Any


_GENERIC_COMPANIES = {
    "",
    "unknown",
    "ethiopian employer",
    "employer",
}
_PUBLISHER_NAMES = (
    "telegram",
    "ethiojobs",
    "hahujobs",
    "dereja",
    "enjera",
    "shega",
    "effoyjobs",
    "harmeejobs",
)
_GENERIC_LOCATIONS = {"", "ethiopia", "ethiopian"}
_TITLE_PREFIXES = ("job vacancy ", "vacancy ", "job opening ", "position ")
_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
_WORD_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


def are_duplicate_jobs(first: Any, second: Any) -> bool:
    """Conservatively identify the same vacancy posted by different sources."""
    first_title = _normalize_title(_value(first, "title"))
    second_title = _normalize_title(_value(second, "title"))
    if not first_title or not second_title:
        return False

    title_similarity = SequenceMatcher(None, first_title, second_title).ratio()
    first_title_words = set(first_title.split())
    second_title_words = set(second_title.split())
    title_overlap = _overlap(first_title_words, second_title_words)
    if title_similarity < 0.84 and title_overlap < 0.8:
        return False

    if not _locations_compatible(
        _normalize(_value(first, "location")),
        _normalize(_value(second, "location")),
    ):
        return False

    first_description = _description_words(first)
    second_description = _description_words(second)
    if min(len(first_description), len(second_description)) < 8:
        return False

    description_overlap = _overlap(first_description, second_description)
    description_similarity = SequenceMatcher(
        None,
        " ".join(sorted(first_description)),
        " ".join(sorted(second_description)),
    ).ratio()
    if description_overlap < 0.76 and description_similarity < 0.72:
        return False

    first_company = _normalize(_value(first, "company"))
    second_company = _normalize(_value(second, "company"))
    first_source = _normalize(_value(first, "source"))
    second_source = _normalize(_value(second, "source"))
    first_company_is_publisher = any(name in first_company or name in first_source for name in _PUBLISHER_NAMES)
    second_company_is_publisher = any(name in second_company or name in second_source for name in _PUBLISHER_NAMES)
    if (
        first_company not in _GENERIC_COMPANIES
        and second_company not in _GENERIC_COMPANIES
        and not first_company_is_publisher
        and not second_company_is_publisher
        and SequenceMatcher(None, first_company, second_company).ratio() < 0.72
    ):
        return description_overlap >= 0.92 or description_similarity >= 0.9

    return True


def deduplicate_jobs(jobs: list[Any]) -> list[Any]:
    """Return one rich, actionable record for each cross-source vacancy."""
    ranked_jobs = sorted(
        enumerate(jobs),
        key=lambda item: (_record_quality(item[1]), -item[0]),
        reverse=True,
    )
    unique_jobs: list[Any] = []
    for _, job in ranked_jobs:
        if not any(are_duplicate_jobs(job, existing) for existing in unique_jobs):
            unique_jobs.append(job)
    return unique_jobs


def _value(job: Any, key: str) -> str:
    if isinstance(job, dict):
        value = job.get(key)
    else:
        value = getattr(job, key, None)
    return str(value or "")


def _normalize(value: str) -> str:
    value = _URL_PATTERN.sub(" ", value.lower())
    return " ".join(_WORD_PATTERN.findall(value))


def _normalize_title(value: str) -> str:
    title = _normalize(value)
    for prefix in _TITLE_PREFIXES:
        if title.startswith(prefix):
            return title[len(prefix):].strip()
    return title


def _description_words(job: Any) -> set[str]:
    description = _normalize(_value(job, "description"))
    requirements = _normalize(_value(job, "requirements"))
    return set((description + " " + requirements).split())


def _overlap(first: set[str], second: set[str]) -> float:
    if not first or not second:
        return 0.0
    return len(first & second) / min(len(first), len(second))


def _locations_compatible(first: str, second: str) -> bool:
    if first in _GENERIC_LOCATIONS or second in _GENERIC_LOCATIONS:
        return True
    first_words = set(first.split())
    second_words = set(second.split())
    return bool(first_words & second_words)


def _record_quality(job: Any) -> int:
    apply_url = _value(job, "apply_url") or _value(job, "source_url") or _value(job, "url")
    source = _normalize(_value(job, "source"))
    is_direct_link = bool(apply_url) and not any(
        publisher in apply_url.lower() for publisher in ("t.me/", "telegram.me", "telegram")
    )
    return (
        (100 if is_direct_link else 0)
        + min(len(_value(job, "description")), 4000)
        + min(len(_value(job, "requirements")), 1000)
        + min(len(_value(job, "skills")), 500)
        + (50 if source and not any(name in source for name in _PUBLISHER_NAMES) else 0)
    )
