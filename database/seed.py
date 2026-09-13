"""
Database seed script - populate database with initial data
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from app.config.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.job import Job
from app.models.skill import Skill
from app.models.notification import Notification

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        print("Seeding database...")
        
        # Create sample users
        print("Creating sample users...")
        users = [
            User(
                email="john@example.com",
                username="johndoe",
                hashed_password="$2b$12$example_hash",  # This should be a real bcrypt hash
                full_name="John Doe",
                phone="+1234567890",
                is_seeker=True,
                is_active=True
            ),
            User(
                email="jane@example.com",
                username="janedoe",
                hashed_password="$2b$12$example_hash",
                full_name="Jane Smith",
                phone="+0987654321",
                is_seeker=True,
                is_active=True
            ),
            User(
                email="company@example.com",
                username="techcompany",
                hashed_password="$2b$12$example_hash",
                full_name="Tech Company",
                phone="+1555555555",
                is_seeker=False,  # Employer
                is_active=True
            )
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        print(f"Created {len(users)} users")
        
        # Create sample skills
        print("Creating sample skills...")
        skills_data = [
            ("Python", "technical", "General-purpose programming language"),
            ("JavaScript", "technical", "Web programming language"),
            ("React", "technical", "JavaScript library for building user interfaces"),
            ("Machine Learning", "technical", "AI and ML technologies"),
            ("Data Analysis", "technical", "Data processing and analysis"),
            ("Communication", "soft", "Effective verbal and written communication"),
            ("Leadership", "soft", "Team leadership and management"),
            ("Problem Solving", "soft", "Analytical problem-solving skills"),
        ]
        
        for name, category, description in skills_data:
            skill = Skill(name=name, category=category, description=description)
            db.add(skill)
        
        db.commit()
        print(f"Created {len(skills_data)} skills")
        
        # Create sample jobs
        print("Creating sample jobs...")
        jobs = [
            Job(
                title="Senior Software Engineer",
                company="Tech Company Inc",
                description="We are looking for a senior software engineer to join our growing team. You will be responsible for developing and maintaining high-quality software solutions.",
                requirements='5+ years of experience, Proficiency in Python and JavaScript, Experience with cloud platforms',
                skills='python, javascript, cloud, api development',
                location="San Francisco, CA",
                salary_min=120000,
                salary_max=180000,
                job_type="full-time",
                source="manual",
                source_url="https://example.com/job/1",
                is_active=1
            ),
            Job(
                title="Data Scientist",
                company="Data Corp",
                description="Join our data science team to work on cutting-edge machine learning projects. You will analyze large datasets and build predictive models.",
                requirements='3+ years of experience, Strong Python skills, Experience with ML frameworks',
                skills='python, machine learning, data analysis, statistics',
                location="New York, NY",
                salary_min=100000,
                salary_max=150000,
                job_type="full-time",
                source="manual",
                source_url="https://example.com/job/2",
                is_active=1
            ),
            Job(
                title="Frontend Developer",
                company="Web Solutions",
                description="We need a skilled frontend developer to build responsive and user-friendly web applications using modern frameworks.",
                requirements='2+ years of experience, Strong React skills, CSS/HTML expertise',
                skills='javascript, react, css, html, frontend',
                location="Remote",
                salary_min=80000,
                salary_max=120000,
                job_type="remote",
                source="manual",
                source_url="https://example.com/job/3",
                is_active=1
            ),
            Job(
                title="DevOps Engineer",
                company="Cloud Systems",
                description="Looking for a DevOps engineer to manage our cloud infrastructure and implement CI/CD pipelines.",
                requirements='3+ years of experience, AWS/GCP experience, Docker and Kubernetes',
                skills='docker, kubernetes, aws, ci/cd, linux',
                location="Austin, TX",
                salary_min=110000,
                salary_max=160000,
                job_type="full-time",
                source="manual",
                source_url="https://example.com/job/4",
                is_active=1
            ),
            Job(
                title="Product Manager",
                company="StartupXYZ",
                description="Join our product team to drive product strategy and work closely with engineering and design teams.",
                requirements='2+ years of product management experience, Agile methodology, Strong communication skills',
                skills='product management, agile, communication, user research',
                location="Remote",
                salary_min=90000,
                salary_max=130000,
                job_type="remote",
                source="manual",
                source_url="https://example.com/job/5",
                is_active=1
            )
        ]
        
        for job in jobs:
            db.add(job)
        db.commit()
        
        print(f"Created {len(jobs)} jobs")
        
        # Create sample notifications
        print("Creating sample notifications...")
        if users:
            notification = Notification(
                user_id=users[0].id,
                type="match",
                title="Welcome to AI Job Matching!",
                message="Your account has been created successfully. Upload your CV to start finding job matches.",
                is_read=False
            )
            db.add(notification)
            db.commit()
            print("Created 1 notification")
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # Seed data
    seed_database()
