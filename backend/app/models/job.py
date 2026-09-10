from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base
from app.models.skill import Skill, job_skills


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text, default="")
    salary_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    job_type: Mapped[str] = mapped_column(String(64), default="full-time")
    source: Mapped[str] = mapped_column(String(128), default="manual")
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True, unique=True)
    min_years_experience: Mapped[float] = mapped_column(default=0.0)
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    skills: Mapped[list[Skill]] = relationship(secondary=job_skills)
    matches: Mapped[list["Match"]] = relationship(back_populates="job", cascade="all, delete-orphan")


from app.models.match import Match  # noqa: E402
