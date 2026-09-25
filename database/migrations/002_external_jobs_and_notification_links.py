"""
Migration 002 - Persistent external jobs and notification/match job links

- Creates the external_jobs table (persistent job store with deadlines).
- Adds the external_job_ids column to notifications so expired jobs can be
  removed from match notifications.
- Rebuilds the matches table when it still carries the legacy NOT NULL job_id
  column pointing at the retired jobs table (its rows are stale).
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from sqlalchemy import inspect, text

from app.config.database import engine, Base
from app.models.user import User
from app.models.cv import CV
from app.models.skill import Skill
from app.models.job import ExternalJob
from app.models.match import Match
from app.models.notification import Notification
from app.models.collaboration import Collaboration, CollaborationMember, CollaborationInvitation


def upgrade():
    """Create external_jobs table and link notifications/matches to job ids"""
    print("Running migration 002...")

    # Creates external_jobs (and any other missing tables) without touching existing ones
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    columns = [column["name"] for column in inspector.get_columns("notifications")]
    if "external_job_ids" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE notifications ADD COLUMN external_job_ids TEXT")
            )
        print("Added notifications.external_job_ids column")
    else:
        print("notifications.external_job_ids already exists")

    match_columns = [column["name"] for column in inspector.get_columns("matches")]
    if "job_id" in match_columns:
        # Legacy matches table has a NOT NULL job_id column pointing at the
        # retired jobs table. Its rows are stale, so rebuild it cleanly.
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE matches"))
        Match.__table__.create(bind=engine)
        print("Rebuilt matches table without legacy job_id column")
    elif "external_job_id" not in match_columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE matches ADD COLUMN external_job_id VARCHAR")
            )
        print("Added matches.external_job_id column")
    else:
        print("matches.external_job_id already exists")

    print("Migration 002 completed successfully!")


def downgrade():
    """Drop external_jobs table (column removal is not supported on SQLite)"""
    print("Rolling back migration 002...")

    ExternalJob.__table__.drop(bind=engine, checkfirst=True)

    print("Rollback completed!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Database migration')
    parser.add_argument('--downgrade', action='store_true', help='Rollback migration')

    args = parser.parse_args()

    if args.downgrade:
        downgrade()
    else:
        upgrade()
