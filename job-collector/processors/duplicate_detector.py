import hashlib
import re

from sources.base import RawJob

_NORMALISE = re.compile(r"[^a-z0-9]+")


def fingerprint(job: RawJob) -> str:
    key = _NORMALISE.sub("", f"{job.title}{job.company}".lower())
    return hashlib.sha1(key.encode()).hexdigest()


def deduplicate(jobs: list[RawJob], known_urls: set[str] | None = None) -> list[RawJob]:
    seen_urls = set(known_urls or set())
    seen_fingerprints: set[str] = set()
    unique: list[RawJob] = []
    for job in jobs:
        fp = fingerprint(job)
        if job.source_url in seen_urls or fp in seen_fingerprints:
            continue
        seen_urls.add(job.source_url)
        seen_fingerprints.add(fp)
        unique.append(job)
    return unique
