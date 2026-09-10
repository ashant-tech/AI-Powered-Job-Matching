import logging

import httpx

from sources.base import JobSource, RawJob

logger = logging.getLogger(__name__)


class RemotiveSource(JobSource):
    """Public remote-jobs API: https://remotive.com/api/remote-jobs"""

    name = "remotive"
    url = "https://remotive.com/api/remote-jobs"

    def fetch(self, limit: int = 50) -> list[RawJob]:
        try:
            data = httpx.get(self.url, params={"limit": limit}, timeout=20).json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("%s fetch failed: %s", self.name, exc)
            return []
        return [
            RawJob(
                title=j["title"],
                company=j.get("company_name", ""),
                description=j.get("description", ""),
                location=j.get("candidate_required_location", "Remote"),
                salary_range=j.get("salary") or None,
                job_type=j.get("job_type", "full_time").replace("_", "-"),
                source=self.name,
                source_url=j["url"],
                skills=[t.lower() for t in j.get("tags", [])],
            )
            for j in data.get("jobs", [])[:limit]
        ]
