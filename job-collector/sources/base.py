from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RawJob:
    title: str
    company: str
    description: str
    source: str
    source_url: str
    location: str = ""
    requirements: str = ""
    salary_range: str | None = None
    job_type: str = "full-time"
    skills: list[str] = field(default_factory=list)


class JobSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, limit: int = 50) -> list[RawJob]: ...
