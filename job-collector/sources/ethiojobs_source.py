"""
Ethiojobs Website Source - real collection from ethiojobs.net.

The site renders job listings client-side (Next.js), but the same data is
served as JSON by its data route: /_next/data/<buildId>/en/jobs.json?page=N.
The buildId changes whenever the site is redeployed, so it is re-read from
the /jobs HTML on every run.
"""
import logging
import re
import time
from html import unescape
from typing import Dict, List, Optional

import requests
import urllib3
from bs4 import BeautifulSoup

from sources.telegram_source import (
    _extract_requirements,
    _find_skills,
    _job_type_from_text,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://ethiojobs.net"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}

# 12 jobs per page; new vacancies appear at the top of page 1.
PAGES_PER_RUN = 2


class EthiojobsSource:
    """Collects real job posts from ethiojobs.net's public JSON data route."""

    def __init__(self, pages: int = PAGES_PER_RUN):
        self.pages = pages

    @property
    def name(self):
        return "Ethiojobs Website"

    def fetch_jobs(self) -> List[Dict]:
        build_id = self._build_id()
        jobs: List[Dict] = []
        for page in range(1, self.pages + 1):
            try:
                records = self._fetch_page(build_id, page)
                page_jobs = [j for j in (self._parse_job(r) for r in records) if j]
                jobs.extend(page_jobs)
                logger.info("ethiojobs.net page %d: collected %d jobs", page, len(page_jobs))
            except requests.RequestException as exc:
                logger.error("Failed to fetch ethiojobs.net page %d: %s", page, exc)
            except Exception as exc:
                logger.exception("Unexpected error on ethiojobs.net page %d: %s", page, exc)
            time.sleep(1)
        logger.info("Total jobs collected from ethiojobs.net: %d", len(jobs))
        return jobs

    def _build_id(self) -> str:
        html = _get(f"{BASE_URL}/jobs").text
        match = re.search(r'"buildId":"([^"]+)"', html)
        if not match:
            raise ValueError("buildId not found in ethiojobs.net HTML")
        return match.group(1)

    def _fetch_page(self, build_id: str, page: int) -> List[Dict]:
        url = f"{BASE_URL}/_next/data/{build_id}/en/jobs.json?page={page}"
        response = _get(url)
        response.raise_for_status()
        payload = response.json().get("pageProps", {})
        return payload.get("jobs", {}).get("data", [])

    def _parse_job(self, record: Dict) -> Optional[Dict]:
        slug = record.get("slug")
        title = (record.get("title") or "").strip()
        if not slug or not title:
            return None

        text = _html_to_text(record.get("description") or "")
        if len(text) < 60:
            return None

        company = ((record.get("company") or {}).get("name") or "").strip() or "Ethiopian Employer"
        location = (record.get("state") or "").strip() or "Ethiopia"
        location_type = (record.get("location_type") or "").strip()
        lowered = text.lower()

        job_type = "remote" if "remote" in location_type.lower() else None
        job_type = job_type or _job_type_from_text(lowered)

        skills = _find_skills(lowered, text, company_tag=None)
        for catalog in record.get("catalogs") or []:
            category = (catalog.get("name") or "").strip().lower()
            if category and category not in skills:
                skills.append(category)

        return {
            "title": title,
            "company": company,
            "description": text if len(text) <= 4000 else text[:3997] + "...",
            "requirements": _extract_requirements(text),
            "skills": skills,
            "location": location,
            "job_type": job_type,
            "source": "Ethiojobs Website",
            "source_url": f"{BASE_URL}/job/{slug}",
            "external_id": f"ej-{slug}",
            "deadline": record.get("date_expiry"),
        }


def _html_to_text(html: str) -> str:
    text = BeautifulSoup(unescape(html), "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _get(url: str) -> requests.Response:
    try:
        return requests.get(url, headers=_HEADERS, timeout=30)
    except requests.exceptions.SSLError:
        # Corporate TLS interception; payload is public job listings.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warning("TLS verification failed for %s; retrying unverified", url)
        return requests.get(url, headers=_HEADERS, timeout=30, verify=False)
