"""
Add external_job_ids column to notifications table
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from sqlalchemy import text
from app.config.database import engine

def upgrade():
    """Add external_job_ids column to notifications table"""
    print("Adding external_job_ids column to notifications table...")

    with engine.connect() as conn:
        # Check if column exists and add it if it doesn't
        result = conn.execute(text("PRAGMA table_info(notifications)"))
        columns = [row[1] for row in result.fetchall()]

        if 'external_job_ids' not in columns:
            conn.execute(text("ALTER TABLE notifications ADD COLUMN external_job_ids TEXT"))
            print("Added external_job_ids column")
        else:
            print("external_job_ids column already exists")

        conn.commit()

    print("external_job_ids column migration completed successfully!")

def downgrade():
    """Remove external_job_ids column from notifications table"""
    print("Rolling back external_job_ids column...")

    # Note: SQLite doesn't support DROP COLUMN directly
    print("Note: SQLite doesn't support DROP COLUMN directly. Manual intervention may be required.")

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
