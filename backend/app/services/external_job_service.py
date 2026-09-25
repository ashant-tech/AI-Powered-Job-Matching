import hashlib
import os
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlparse

import requests
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.job import ExternalJob
from app.services.deadline_parser import extract_deadline

DEFAULT_JOB_TTL_DAYS = 30


def upsert_jobs(db: Session, records: list[dict], default_ttl_days: int = DEFAULT_JOB_TTL_DAYS) -> dict:
    """Insert or update jobs by external_id. Jobs whose deadline already passed are stored inactive."""
    now = datetime.utcnow()
    counts = {"created": 0, "updated": 0, "skipped": 0}

    for record in records:
        if not isinstance(record, dict):
            counts["skipped"] += 1
            continue

        title = _clean_str(record.get("title"))
        company = _clean_str(record.get("company"))
        description = _clean_str(record.get("description"))
        if not (title and company and description):
            counts["skipped"] += 1
            continue

        apply_url = _clean_str(record.get("apply_url") or record.get("source_url") or record.get("url"))
        external_id = _clean_str(record.get("external_id") or record.get("id"))
        if not external_id:
            external_id = hashlib.sha256(
                (apply_url or f"{title}|{company}|{description}").encode()
            ).hexdigest()

        deadline = _coerce_deadline(record.get("deadline"))
        if deadline is None:
            deadline = extract_deadline(f"{description} {record.get('requirements') or ''}")
        if deadline is None:
            deadline = now + timedelta(days=default_ttl_days)

        job = db.query(ExternalJob).filter(ExternalJob.external_id == external_id).first()
        if job is None:
            job = ExternalJob(external_id=external_id, title=title, company=company)
            db.add(job)
            counts["created"] += 1
        else:
            counts["updated"] += 1

        job.title = title
        job.company = company
        job.description = description
        job.location = _clean_str(record.get("location")) or None
        job.salary_min = _salary(record.get("salary_min"))
        job.salary_max = _salary(record.get("salary_max"))
        job.job_type = _clean_str(record.get("job_type")) or None
        job.requirements = _clean_str(record.get("requirements")) or None
        job.skills = record.get("skills") if isinstance(record.get("skills"), str) else None
        job.source = _clean_str(record.get("source")) or None
        job.apply_url = apply_url
        job.deadline = deadline
        job.is_active = deadline > now if record.get("is_active", True) else False

    db.commit()
    return counts


class ExternalJobService:
    DEFAULT_TRUSTED_DOMAINS = {
        "ethiojobs.com",
        "hahujobs.com",
        "reporterethiopia.com",
        "linkedin.com",
        "indeed.com",
        "glassdoor.com",
    }

    def __init__(self, db: Session | None = None):
        self.db = db

    def fetch_jobs(self) -> list[ExternalJob]:
        """Active, non-expired jobs from the database (plus trusted external feeds when configured)."""
        if self.db is None:
            return []

        self.ingest_external_api_jobs()

        now = datetime.utcnow()
        return self.db.query(ExternalJob).filter(
            ExternalJob.is_active == True,  # noqa: E712
            or_(ExternalJob.deadline.is_(None), ExternalJob.deadline > now),
        ).order_by(ExternalJob.posted_at.desc()).all()

    def ingest_external_api_jobs(self) -> dict:
        """Pull jobs from EXTERNAL_JOB_API_URLS (comma-separated) and upsert them."""
        if self.db is None:
            return {"created": 0, "updated": 0, "skipped": 0}

        records = []
        for source_url in self._source_urls():
            if not self._is_trusted_url(source_url):
                print(f"Skipping untrusted job source: {source_url}")
                continue
            try:
                response = requests.get(source_url, timeout=15)
                response.raise_for_status()
                payload = response.json()
                records.extend(payload.get("jobs", []) if isinstance(payload, dict) else payload)
            except (requests.RequestException, ValueError, TypeError) as exc:
                print(f"Error fetching jobs from {source_url}: {exc}")

        trusted_records = [
            record for record in records
            if isinstance(record, dict) and self._is_trusted_url(
                record.get("apply_url") or record.get("source_url") or record.get("url")
            )
        ]
        return upsert_jobs(self.db, trusted_records)

    def _source_urls(self) -> list[str]:
        configured = os.getenv("EXTERNAL_JOB_API_URLS", "")
        return [url.strip() for url in configured.split(",") if url.strip()]

    def _trusted_domains(self) -> set[str]:
        configured = os.getenv("TRUSTED_JOB_DOMAINS", "")
        if configured:
            return {domain.strip().lower().lstrip(".") for domain in configured.split(",") if domain.strip()}
        return self.DEFAULT_TRUSTED_DOMAINS

    def _is_trusted_url(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        parsed = urlparse(value)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        return (
            parsed.scheme == "https"
            and bool(hostname)
            and any(hostname == domain or hostname.endswith(f".{domain}") for domain in self._trusted_domains())
        )


def _clean_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _salary(value: Any) -> float | None:
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    if isinstance(value, str):
        try:
            parsed = float(value.replace(",", ""))
            return parsed if parsed > 0 else None
        except ValueError:
            return None
    return None


def _coerce_deadline(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None
