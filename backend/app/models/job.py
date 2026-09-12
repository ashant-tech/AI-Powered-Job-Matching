from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)  # JSON string
    skills = Column(Text)  # JSON string
    location = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    job_type = Column(String)  # full-time, part-time, contract, remote
    source = Column(String)  # where the job was scraped from
    source_url = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    matches = relationship("Match", back_populates="job")
