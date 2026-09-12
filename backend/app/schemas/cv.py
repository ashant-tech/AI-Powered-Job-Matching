from pydantic import BaseModel
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
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CVAnalysis(BaseModel):
    skills: list
    experience: list
    education: list
    summary: str
