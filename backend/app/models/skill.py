from sqlalchemy import Column, Integer, String, Text
from app.config.database import Base

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String)  # technical, soft, language, etc.
    description = Column(Text)
