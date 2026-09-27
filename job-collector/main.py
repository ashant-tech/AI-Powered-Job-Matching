"""
Job Collector - Main entry point for collecting jobs from various sources.

Collects jobs, persists them into the shared database, removes expired jobs
from matches/notifications, and runs CV matching so users get notified of
new high-quality matches.
"""
import sys
import os
import time
import logging

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("job-collector")

# Load collector environment (must happen before backend settings import)
load_dotenv()

# Make the backend app importable so we share models and services
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
import app.models.user  # noqa: F401  (registers tables on Base.metadata)
import app.models.cv  # noqa: F401
import app.models.job  # noqa: F401
import app.models.skill  # noqa: F401
import app.models.match  # noqa: F401
import app.models.notification  # noqa: F401
import app.models.collaboration  # noqa: F401

from app.services.external_job_service import upsert_jobs
from app.services.job_service import JobService
from app.services.notification_service import NotificationService
from app.services.matching_service import MatchingService

from sources.telegram_source import TelegramJobSource
from sources.ethiojobs_source import EthiojobsSource
from processors.cleaner import JobCleaner
from processors.duplicate_detector import DuplicateDetector

DEFAULT_DATABASE_URL = "sqlite:///../backend/job_matching.db"


def get_session():
    """Build a session bound to the shared database (backend DB or Postgres in Docker)."""
    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
    )
    from app.config.database import ensure_schema
    ensure_schema(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


class JobCollector:
    def __init__(self):
        # Real sources only: public Telegram channel web previews (t.me/s/...)
        # and ethiojobs.net's JSON data route (largest Ethiopian jobs site).
        # The other website scrapers in sources/source*.py were retired: they
        # either block scraping or only produced hardcoded sample data.
        self.sources = [
            TelegramJobSource(),
            EthiojobsSource(),
        ]
        self.cleaner = JobCleaner()
        self.duplicate_detector = DuplicateDetector()
        # Consecutive bad cycles per source, for escalating silent-death alerts
        self._failed_cycles = {}

    def collect_jobs(self):
        """Collect jobs from all sources"""
        all_jobs = []

        for source in self.sources:
            try:
                logger.info("Collecting jobs from %s...", source.name)
                jobs = source.fetch_jobs()
                logger.info("Found %d jobs from %s", len(jobs), source.name)
                if jobs:
                    self._failed_cycles.pop(source.name, None)
                else:
                    self._alert_empty_source(source.name)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error("Error collecting from %s: %s", source.name, e)
                self._alert_empty_source(source.name)

        logger.info("Total jobs collected: %d", len(all_jobs))
        return all_jobs

    def _alert_empty_source(self, source_name):
        """Escalate when a source keeps returning nothing (API may have changed)."""
        count = self._failed_cycles.get(source_name, 0) + 1
        self._failed_cycles[source_name] = count
        if count >= 3:
            logger.error(
                "SOURCE DEAD: %s returned 0 jobs for %d consecutive cycles - "
                "the source may have changed or blocked us; manual check needed",
                source_name, count,
            )
        else:
            logger.warning(
                "SOURCE ALERT: %s returned 0 jobs (%d consecutive cycle(s))",
                source_name, count,
            )

    def process_jobs(self, jobs):
        """Clean collected jobs and drop duplicates"""
        logger.info("Cleaning jobs...")
        cleaned_jobs = self.cleaner.clean_jobs(jobs)
        logger.info("Cleaned %d jobs", len(cleaned_jobs))

        logger.info("Detecting duplicates...")
        unique_jobs = self.duplicate_detector.remove_duplicates(cleaned_jobs)
        logger.info("Found %d unique jobs", len(unique_jobs))

        return unique_jobs

    def persist_and_notify(self, processed_jobs):
        """Persist jobs, expire stale data, and match all CVs (sends notifications)."""
        db = get_session()
        try:
            counts = upsert_jobs(db, processed_jobs)
            logger.info(
                "Persisted jobs: %d created, %d updated, %d skipped",
                counts['created'], counts['updated'], counts['skipped'],
            )

            deactivated = JobService(db).deactivate_expired_jobs()
            purged_matches = JobService(db).purge_expired_matches()
            purged_notifications = NotificationService(db).purge_expired_notifications()
            logger.info(
                "Expiry: %d jobs deactivated, %d matches purged, %d notifications purged",
                deactivated, purged_matches, purged_notifications,
            )

            matched_cvs = MatchingService(db).find_matches_for_all_users()
            logger.info("Matching: %d CVs processed", matched_cvs)
        finally:
            db.close()

    def run_cycle(self):
        """Full collection cycle: collect -> process -> persist -> match"""
        jobs = self.collect_jobs()
        processed_jobs = self.process_jobs(jobs)
        self.persist_and_notify(processed_jobs)
        logger.info("Job collection cycle completed")

    def run(self):
        """Main run loop"""
        logger.info("Starting job collector...")

        while True:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error("Error in job collection cycle: %s", e)

            # Wait for next scheduled run
            time.sleep(3600)  # Run every hour

    def run_once(self):
        """Run job collection once"""
        logger.info("Running job collection once...")
        self.run_cycle()
        logger.info("Job collection completed.")

if __name__ == "__main__":
    collector = JobCollector()

    if "--loop" in sys.argv:
        # Persistent hourly service mode (used by docker-compose)
        collector.run()
    else:
        collector.run_once()
