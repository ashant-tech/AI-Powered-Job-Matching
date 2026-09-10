"""Collect jobs from external sources, dedupe, and push them to the backend API.

Usage:
    API_URL=http://localhost:8000 API_TOKEN=<jwt> python main.py [--limit 50] [--interval 3600]
"""

import argparse
import logging
import os
import time
from dataclasses import asdict

import httpx

from processors.cleaner import clean_job
from processors.duplicate_detector import deduplicate
from sources import ALL_SOURCES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("job-collector")

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN", "")


def known_job_urls(client: httpx.Client) -> set[str]:
    try:
        jobs = client.get("/api/jobs", params={"limit": 200}).json()
    except (httpx.HTTPError, ValueError):
        return set()
    return {j["source_url"] for j in jobs if j.get("source_url")}


def run_once(limit: int) -> int:
    headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}
    with httpx.Client(base_url=API_URL, headers=headers, timeout=30) as client:
        raw = [clean_job(j) for source in ALL_SOURCES for j in source.fetch(limit)]
        jobs = deduplicate(raw, known_job_urls(client))
        logger.info("fetched %d jobs, %d new after dedupe", len(raw), len(jobs))
        created = 0
        for job in jobs:
            resp = client.post("/api/jobs", json=asdict(job))
            if resp.status_code == 201:
                created += 1
            elif resp.status_code != 409:
                logger.warning("failed to create %s: %s %s", job.source_url, resp.status_code, resp.text[:200])
        logger.info("created %d jobs", created)
        return created


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--interval", type=int, default=0, help="seconds between runs; 0 runs once")
    args = parser.parse_args()
    while True:
        run_once(args.limit)
        if args.interval <= 0:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
