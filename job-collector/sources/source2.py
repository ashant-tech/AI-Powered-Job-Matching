import logging

import httpx

from sources.base import JobSource, RawJob

logger = logging.getLogger(__name__)


class ArbeitnowSource(JobSource):
    """Public job board API: https://www.arbeitnow.com/api/job-board-api"""

    name = "arbeitnow"
    url = "https://www.arbeitnow.com/api/job-board-api"

    def fetch(self, limit: int = 50) -> list[RawJob]:
        try:
            data = httpx.get(self.url, timeout=20).json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("%s fetch failed: %s", self.name, exc)
            return []
        return [
            RawJob(
                title=j["title"],
                company=j.get("company_name", ""),
                description=j.get("description", ""),
                location=j.get("location", ""),
                job_type=", ".join(j.get("job_types", [])) or "full-time",
                source=self.name,
                source_url=j["url"],
                skills=[t.lower() for t in j.get("tags", [])],
            )
            for j in data.get("data", [])[:limit]
        ]
