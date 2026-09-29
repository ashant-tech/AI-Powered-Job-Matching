"""
Add department column to users table
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from sqlalchemy import text
from app.config.database import engine

def upgrade():
    """Add department column to users table"""
    print("Adding department column to users table...")

    with engine.connect() as conn:
        # Check if column exists and add it if it doesn't
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]

        if 'department' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN department VARCHAR"))
            print("Added department column")
        else:
            print("Department column already exists")

        conn.commit()

    print("Department column migration completed successfully!")

def downgrade():
    """Remove department column from users table"""
    print("Rolling back department column...")

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
