from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.config.database import Base


class ExternalJob(Base):
    __tablename__ = "external_jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    job_type = Column(String)
    requirements = Column(Text)
    skills = Column(Text)  # JSON string
    source = Column(String)
    apply_url = Column(String, nullable=False, default="")
    deadline = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    posted_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
