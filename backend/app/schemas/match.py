from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchBase(BaseModel):
    user_id: int
    cv_id: int
    job_id: int

class MatchResponse(MatchBase):
    id: int
    match_score: float
    match_reasons: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchUpdate(BaseModel):
    status: str
