from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.job import JobOut


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cv_id: int
    job_id: int
    score: float
    skill_score: float
    semantic_score: float
    experience_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime
    job: JobOut


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int | None
    title: str
    message: str
    channel: str
    is_read: bool
    created_at: datetime
