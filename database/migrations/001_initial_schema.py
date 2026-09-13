"""
Initial database migration - Create all tables
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.config.database import engine, Base
from app.models.user import User
from app.models.cv import CV
from app.models.job import Job
from app.models.skill import Skill
from app.models.match import Match
from app.models.notification import Notification

def upgrade():
    """Create initial database schema"""
    print("Running initial migration...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Initial migration completed successfully!")

def downgrade():
    """Drop all tables"""
    print("Rolling back initial migration...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    print("Rollback completed successfully!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration')
    parser.add_argument('--downgrade', action='store_true', help='Rollback migration')
    
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()
