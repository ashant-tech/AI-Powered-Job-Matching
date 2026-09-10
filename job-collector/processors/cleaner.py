import html
import re

from sources.base import RawJob

_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def strip_html(text: str) -> str:
    return _WS.sub(" ", html.unescape(_TAGS.sub(" ", text))).strip()


def clean_job(job: RawJob) -> RawJob:
    job.title = strip_html(job.title)[:255]
    job.company = strip_html(job.company)[:255] or "Unknown"
    job.description = strip_html(job.description)
    job.location = strip_html(job.location)[:255]
    job.requirements = strip_html(job.requirements)
    job.skills = sorted({s.strip().lower() for s in job.skills if s.strip()})
    return job
