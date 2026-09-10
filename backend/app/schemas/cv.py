from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CVOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_name: str
    summary: str
    education: list
    experience: list
    years_of_experience: float
    skills: list[SkillOut]
    created_at: datetime


class CVAnalysis(BaseModel):
    skills: list[str]
    education: list[str]
    experience: list[str]
    years_of_experience: float
    summary: str

    @field_validator("skills", mode="before")
    @classmethod
    def dedupe(cls, v: list[str]) -> list[str]:
        return sorted(set(v))
