from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CVBase(BaseModel):
    title: str

class CVCreate(CVBase):
    pass

class CVResponse(CVBase):
    id: int
    user_id: int
    file_path: str
    file_name: str
    parsed_text: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    field: Optional[str] = None
    experience_level: Optional[str] = None
    total_years_experience: Optional[int] = None
    job_titles: Optional[str] = None
    contact_info: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CVAnalysis(BaseModel):
    skills: list
    experience: list
    education: list
    summary: str
    field: Optional[str] = None
    experience_level: Optional[str] = None
    total_years_experience: Optional[int] = None
    job_titles: Optional[list] = None
    contact_info: Optional[dict] = None


class CVProfileUpdate(BaseModel):
    skills: Optional[list[str]] = Field(default=None, max_length=100)
    field: Optional[str] = None
    experience_level: Optional[str] = None
    total_years_experience: Optional[int] = Field(default=None, ge=0, le=60)
    job_titles: Optional[list[str]] = Field(default=None, max_length=30)
    education: Optional[list[dict[str, str]]] = Field(default=None, max_length=20)
