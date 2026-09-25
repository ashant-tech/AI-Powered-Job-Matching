from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobInfo(BaseModel):
    external_id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    source: Optional[str] = None
    apply_url: str
    deadline: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    user_id: int
    cv_id: int
    external_job_id: str

class MatchResponse(MatchBase):
    id: int
    match_score: float
    match_reasons: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    job: Optional[JobInfo] = None
    
    class Config:
        from_attributes = True

class MatchUpdate(BaseModel):
    status: str
