from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

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
    apply_url: str = Field(..., alias="source_url")

    model_config = ConfigDict(populate_by_name=True)
