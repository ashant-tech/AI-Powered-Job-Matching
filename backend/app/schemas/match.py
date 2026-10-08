from pydantic import BaseModel
from typing import Literal
from typing import Optional
from datetime import datetime

class JobInfo(BaseModel):
    external_id: str
    title: str
    company: str
    description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    source: Optional[str] = None
    apply_url: str
    deadline: Optional[datetime] = None
    field: Optional[str] = None
    
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
    skill_gaps: Optional[dict] = None
    detailed_reasons: Optional[list] = None
    fit_level: Optional[str] = None
    score_confidence: Optional[float] = None
    match_caveats: Optional[list[str]] = None
    component_scores: Optional[dict[str, Optional[float]]] = None
    cv_match_score: Optional[float] = None
    feedback_adjustment: Optional[float] = None

    class Config:
        from_attributes = True

class MatchUpdate(BaseModel):
    status: Literal["pending", "viewed", "applied", "rejected", "relevant", "not_relevant"]
