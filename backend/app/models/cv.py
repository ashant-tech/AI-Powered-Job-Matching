from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.config.database import Base

class CV(Base):
    __tablename__ = "cvs"
    __table_args__ = (UniqueConstraint("user_id", name="uq_cvs_user_id"),)
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    parsed_text = Column(Text)
    skills = Column(Text)  # JSON string
    experience = Column(Text)  # JSON string
    education = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
