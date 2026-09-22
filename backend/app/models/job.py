from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExternalJob:
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
    apply_url: str = ""
