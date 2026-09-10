import logging
import os
import xml.etree.ElementTree as ET

import httpx

from sources.base import JobSource, RawJob

logger = logging.getLogger(__name__)


class RssSource(JobSource):
    """Generic RSS/Atom job feed. Configure with JOB_RSS_FEEDS=url1,url2"""

    name = "rss"

    def __init__(self, feeds: list[str] | None = None):
        env = os.getenv("JOB_RSS_FEEDS", "")
        self.feeds = feeds if feeds is not None else [u.strip() for u in env.split(",") if u.strip()]

    def fetch(self, limit: int = 50) -> list[RawJob]:
        jobs: list[RawJob] = []
        for feed in self.feeds:
            try:
                root = ET.fromstring(httpx.get(feed, timeout=20).text)
            except (httpx.HTTPError, ET.ParseError) as exc:
                logger.warning("%s fetch failed for %s: %s", self.name, feed, exc)
                continue
            for item in root.iter("item"):
                link = item.findtext("link") or ""
                title = item.findtext("title") or ""
                if not link or not title:
                    continue
                jobs.append(
                    RawJob(
                        title=title,
                        company=item.findtext("author") or "Unknown",
                        description=item.findtext("description") or "",
                        source=self.name,
                        source_url=link,
                    )
                )
        return jobs[:limit]
