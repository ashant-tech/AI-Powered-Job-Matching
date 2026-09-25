from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ExternalJob(BaseModel):
    external_id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    requirements: Optional[str] = None
    skills: Optional[str] = None
    source: Optional[str] = None
    apply_url: str
    deadline: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
