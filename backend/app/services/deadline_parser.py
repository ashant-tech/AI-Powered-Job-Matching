import re
from datetime import datetime

DEADLINE_LABELS = (
    r"(?:deadline(?:\s+date)?|closing\s+date|last\s+(?:date|day)|"
    r"apply\s+(?:by|before)|application\s+deadline|apply\s+no\s+later\s+than|"
    r"የሥራ\s*መዘጊያ|መዘጊያ)"
)

# Named-group date patterns; for numeric d/m ambiguity, Ethiopian convention (DD/MM) is assumed.
DATE_PATTERNS = [
    r"(?P<y>\d{4})[-/.](?P<m>\d{1,2})[-/.](?P<d>\d{1,2})",
    r"(?P<d>\d{1,2})[-/.](?P<m>\d{1,2})[-/.](?P<y>\d{2,4})",
    r"(?P<m>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?\s+"
    r"(?P<d>\d{1,2})(?:st|nd|rd|th)?,?\s+(?P<y>\d{4})",
    r"(?P<d>\d{1,2})(?:st|nd|rd|th)?\s+(?P<m>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
    r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\.?,?\s+(?P<y>\d{4})",
]

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# How far after the label we look for a date
_WINDOW_CHARS = 50


def extract_deadline(text: str) -> datetime | None:
    """Extract an application deadline from free text.

    Looks for a date near a deadline label (English or Amharic) and returns it
    as a naive UTC datetime, or None when no deadline is found.
    """
    if not text:
        return None

    for label_match in re.finditer(DEADLINE_LABELS, text, re.IGNORECASE):
        window = text[label_match.end():label_match.end() + _WINDOW_CHARS]
        deadline = _find_date(window)
        if deadline:
            return deadline

    return None


def _find_date(window: str) -> datetime | None:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, window, re.IGNORECASE)
        if not match:
            continue

        month = _parse_month(match.group("m"))
        day = int(match.group("d"))
        year = int(match.group("y"))
        if year < 100:
            year += 2000

        if not month:
            continue

        try:
            return datetime(year, month, day)
        except ValueError:
            continue

    return None


def _parse_month(value: str) -> int | None:
    if value.isdigit():
        month = int(value)
        return month if 1 <= month <= 12 else None
    return _MONTHS.get(value[:3].lower())
