from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("cv_id", "job_id", name="uq_cv_job"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cv_id: Mapped[int] = mapped_column(ForeignKey("cvs.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float)
    skill_score: Mapped[float] = mapped_column(Float, default=0.0)
    semantic_score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_score: Mapped[float] = mapped_column(Float, default=0.0)
    matched_skills: Mapped[list] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cv: Mapped["CV"] = relationship(back_populates="matches")
    job: Mapped["Job"] = relationship(back_populates="matches")


from app.models.cv import CV  # noqa: E402
from app.models.job import Job  # noqa: E402
