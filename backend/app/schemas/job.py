from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None

class JobCreate(JobBase):
    requirements: Optional[str] = None
    skills: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None

class JobResponse(JobBase):
    id: int
    requirements: Optional[str] = None
    skills: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
