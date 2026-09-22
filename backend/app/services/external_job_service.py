import hashlib
import os
from typing import Any
from urllib.parse import urlparse

import requests

from app.models.job import ExternalJob


class ExternalJobService:
    DEFAULT_TRUSTED_DOMAINS = {
        "ethiojobs.com",
        "hahujobs.com",
        "reporterethiopia.com",
        "linkedin.com",
        "indeed.com",
        "glassdoor.com",
    }

    def fetch_jobs(self) -> list[ExternalJob]:
        jobs = []
        for source_url in self._source_urls():
            if not self._is_trusted_url(source_url):
                print(f"Skipping untrusted job source: {source_url}")
                continue
            try:
                response = requests.get(source_url, timeout=15)
                response.raise_for_status()
                payload = response.json()
                records = payload.get("jobs", []) if isinstance(payload, dict) else payload
                jobs.extend(self._to_external_job(record, source_url) for record in records)
            except (requests.RequestException, ValueError, TypeError) as exc:
                print(f"Error fetching jobs from {source_url}: {exc}")

        return [job for job in jobs if job]

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

    def _to_external_job(self, record: Any, source_url: str) -> ExternalJob | None:
        if not isinstance(record, dict):
            return None

        apply_url = record.get("apply_url") or record.get("source_url") or record.get("url")
        title = record.get("title")
        company = record.get("company")
        description = record.get("description")
        if (
            not all(isinstance(value, str) and value.strip() for value in (title, company, description, apply_url))
            or not self._is_trusted_url(apply_url)
        ):
            return None

        external_id = str(record.get("external_id") or record.get("id") or apply_url)
        if external_id == apply_url:
            external_id = hashlib.sha256(apply_url.encode()).hexdigest()

        return ExternalJob(
            external_id=external_id,
            title=title,
            company=company,
            description=description,
            location=record.get("location"),
            salary_min=record.get("salary_min"),
            salary_max=record.get("salary_max"),
            job_type=record.get("job_type"),
            requirements=record.get("requirements"),
            skills=record.get("skills"),
            source=record.get("source") or source_url,
            apply_url=apply_url,
        )