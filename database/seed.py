"""Seed the database with a demo user and sample jobs.

Run from the backend directory:  python ../database/seed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import app.models  # noqa: E402,F401
from app.config.database import Base, SessionLocal, engine  # noqa: E402
from app.models.user import User  # noqa: E402
from app.schemas.job import JobCreate  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402
from app.services.auth_service import register_user  # noqa: E402
from app.services.job_service import create_job  # noqa: E402

SAMPLE_JOBS = [
    JobCreate(
        title="Backend Engineer (Python)",
        company="Addis Tech",
        location="Addis Ababa, Ethiopia",
        description="Build REST APIs with FastAPI and PostgreSQL. Deploy with Docker on AWS. 3+ years experience required.",
        requirements="Python, FastAPI, SQL, Docker, AWS, Git",
        salary_range="ETB 40,000 - 60,000",
    ),
    JobCreate(
        title="Frontend Developer",
        company="Sheba Digital",
        location="Remote",
        description="Develop modern web apps with React, Next.js, TypeScript and Tailwind CSS. 2 years experience.",
        requirements="React, Next.js, TypeScript, HTML, CSS",
    ),
    JobCreate(
        title="Machine Learning Engineer",
        company="Nile AI Labs",
        location="Nairobi, Kenya",
        description="Train and deploy NLP models using PyTorch and transformers. Experience with Python, pandas and MLOps.",
        requirements="Python, Machine Learning, Deep Learning, NLP, Docker, Kubernetes",
        min_years_experience=4,
    ),
    JobCreate(
        title="Accountant",
        company="Blue Nile Trading",
        location="Addis Ababa, Ethiopia",
        description="Manage bookkeeping, monthly reports and tax filing using QuickBooks and Excel.",
        requirements="Accounting, Excel, Communication",
    ),
    JobCreate(
        title="Digital Marketing Specialist",
        company="Habesha Media",
        location="Hybrid - Addis Ababa",
        description="Run SEO, social campaigns and analytics. Strong communication and data analysis skills.",
        requirements="Marketing, SEO, Data Analysis, Communication",
    ),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "demo@example.com").first():
            register_user(db, UserCreate(email="demo@example.com", full_name="Demo User", password="password123"))
            print("created demo user demo@example.com / password123")
        for job in SAMPLE_JOBS:
            try:
                create_job(db, job)
                print(f"created job: {job.title}")
            except Exception as exc:  # duplicate etc.
                db.rollback()
                print(f"skipped {job.title}: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
