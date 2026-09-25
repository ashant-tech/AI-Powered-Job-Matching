"""
Job Collector - Main entry point for collecting jobs from various sources.

Collects jobs, persists them into the shared database, removes expired jobs
from matches/notifications, and runs CV matching so users get notified of
new high-quality matches.
"""
import sys
import os
import time

from dotenv import load_dotenv

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
    Base.metadata.create_all(bind=engine)
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

    def collect_jobs(self):
        """Collect jobs from all sources"""
        all_jobs = []

        for source in self.sources:
            try:
                print(f"Collecting jobs from {source.name}...")
                jobs = source.fetch_jobs()
                print(f"Found {len(jobs)} jobs from {source.name}")
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error collecting from {source.name}: {e}")

        print(f"Total jobs collected: {len(all_jobs)}")
        return all_jobs

    def process_jobs(self, jobs):
        """Clean collected jobs and drop duplicates"""
        print("Cleaning jobs...")
        cleaned_jobs = self.cleaner.clean_jobs(jobs)
        print(f"Cleaned {len(cleaned_jobs)} jobs")

        print("Detecting duplicates...")
        unique_jobs = self.duplicate_detector.remove_duplicates(cleaned_jobs)
        print(f"Found {len(unique_jobs)} unique jobs")

        return unique_jobs

    def persist_and_notify(self, processed_jobs):
        """Persist jobs, expire stale data, and match all CVs (sends notifications)."""
        db = get_session()
        try:
            counts = upsert_jobs(db, processed_jobs)
            print(
                f"Persisted jobs: {counts['created']} created, "
                f"{counts['updated']} updated, {counts['skipped']} skipped"
            )

            deactivated = JobService(db).deactivate_expired_jobs()
            purged_matches = JobService(db).purge_expired_matches()
            purged_notifications = NotificationService(db).purge_expired_notifications()
            print(
                f"Expiry: {deactivated} jobs deactivated, "
                f"{purged_matches} matches purged, {purged_notifications} notifications purged"
            )

            matched_cvs = MatchingService(db).find_matches_for_all_users()
            print(f"Matching: {matched_cvs} CVs processed")
        finally:
            db.close()

    def run_cycle(self):
        """Full collection cycle: collect -> process -> persist -> match"""
        jobs = self.collect_jobs()
        processed_jobs = self.process_jobs(jobs)
        self.persist_and_notify(processed_jobs)
        print("Job collection cycle completed")

    def run(self):
        """Main run loop"""
        print("Starting job collector...")

        while True:
            try:
                self.run_cycle()
            except Exception as e:
                print(f"Error in job collection cycle: {e}")

            # Wait for next scheduled run
            time.sleep(3600)  # Run every hour

    def run_once(self):
        """Run job collection once"""
        print("Running job collection once...")
        self.run_cycle()
        print("Job collection completed.")

if __name__ == "__main__":
    collector = JobCollector()

    # Run once for testing
    collector.run_once()

    # Or run continuously with scheduler
    # schedule.every(1).hours.do(collector.run_once)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
