"""
Add enhanced CV analysis columns

Adds columns for achievements, certifications, projects, languages, and soft skills
to support more intelligent CV analysis.
"""

def upgrade(db):
    """Add new columns to cvs table."""
    # Add achievements column
    db.execute("ALTER TABLE cvs ADD COLUMN achievements TEXT")
    
    # Add certifications column
    db.execute("ALTER TABLE cvs ADD COLUMN certifications TEXT")
    
    # Add projects column
    db.execute("ALTER TABLE cvs ADD COLUMN projects TEXT")
    
    # Add languages column
    db.execute("ALTER TABLE cvs ADD COLUMN languages TEXT")
    
    # Add soft_skills column
    db.execute("ALTER TABLE cvs ADD COLUMN soft_skills TEXT")
    
    db.commit()


def downgrade(db):
    """Remove new columns from cvs table."""
    db.execute("ALTER TABLE cvs DROP COLUMN achievements")
    db.execute("ALTER TABLE cvs DROP COLUMN certifications")
    db.execute("ALTER TABLE cvs DROP COLUMN projects")
    db.execute("ALTER TABLE cvs DROP COLUMN languages")
    db.execute("ALTER TABLE cvs DROP COLUMN soft_skills")
    
    db.commit()
