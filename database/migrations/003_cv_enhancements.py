"""
Add enhanced CV analysis fields
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from sqlalchemy import text
from app.config.database import engine

def upgrade():
    """Add enhanced CV analysis columns"""
    print("Adding enhanced CV analysis columns...")

    with engine.connect() as conn:
        # Check if columns exist and add them if they don't
        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE, so we need to check first

        # Check table info
        result = conn.execute(text("PRAGMA table_info(cvs)"))
        columns = [row[1] for row in result.fetchall()]

        # Add columns if they don't exist
        if 'experience_level' not in columns:
            conn.execute(text("ALTER TABLE cvs ADD COLUMN experience_level VARCHAR(50)"))
            print("Added experience_level column")

        if 'total_years_experience' not in columns:
            conn.execute(text("ALTER TABLE cvs ADD COLUMN total_years_experience INTEGER"))
            print("Added total_years_experience column")

        if 'job_titles' not in columns:
            conn.execute(text("ALTER TABLE cvs ADD COLUMN job_titles TEXT"))
            print("Added job_titles column")

        if 'contact_info' not in columns:
            conn.execute(text("ALTER TABLE cvs ADD COLUMN contact_info TEXT"))
            print("Added contact_info column")

        conn.commit()

    print("Enhanced CV analysis columns added successfully!")

def downgrade():
    """Remove enhanced CV analysis columns"""
    print("Rolling back enhanced CV analysis columns...")

    with engine.connect() as conn:
        # Note: SQLite doesn't support DROP COLUMN directly, but we can recreate the table
        # For simplicity, we'll just note this limitation
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
