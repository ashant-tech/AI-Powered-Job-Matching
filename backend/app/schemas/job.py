from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.cv import SkillOut


class JobCreate(BaseModel):
    title: str
    company: str
    location: str = ""
    description: str
    requirements: str = ""
    salary_range: str | None = None
    job_type: str = "full-time"
    source: str = "manual"
    source_url: str | None = None
    min_years_experience: float = 0.0
    skills: list[str] = []


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str
    description: str
    requirements: str
    salary_range: str | None
    job_type: str
    source: str
    source_url: str | None
    min_years_experience: float
    is_active: bool
    posted_at: datetime
    skills: list[SkillOut]
