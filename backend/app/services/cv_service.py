from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
import json

from app.models.cv import CV
from app.schemas.cv import CVCreate, CVAnalysis
from app.config.settings import settings
from app.cv_processing.pdf_parser import parse_pdf
from app.cv_processing.docx_parser import parse_docx
from app.cv_processing.text_cleaner import clean_text
from app.ai.cv_analyzer import analyze_cv_text
from app.ai.skill_extractor import extract_skills

class CVService:
    def __init__(self, db: Session):
        self.db = db

    def upload_cv(self, user_id: int, file: UploadFile, title: str) -> CV:
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        file_extension = file.filename.split('.')[-1].lower()
        file_path = f"{settings.UPLOAD_DIR}/{user_id}_{title}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        # Parse CV based on file type
        parsed_text = ""
        if file_extension == "pdf":
            parsed_text = parse_pdf(file_path)
        elif file_extension == "docx":
            parsed_text = parse_docx(file_path)
        else:
            parsed_text = clean_text(file.file.read().decode('utf-8'))
        
        # Create CV record
        db_cv = CV(
            user_id=user_id,
            title=title,
            file_path=file_path,
            file_name=file.filename,
            parsed_text=parsed_text
        )
        
        self.db.add(db_cv)
        self.db.commit()
        self.db.refresh(db_cv)
        
        # Analyze CV asynchronously (simplified for now)
        self._analyze_cv_async(db_cv.id)
        
        return db_cv

    def get_cv(self, cv_id: int) -> CV | None:
        return self.db.query(CV).filter(CV.id == cv_id).first()

    def get_user_cvs(self, user_id: int) -> list[CV]:
        return self.db.query(CV).filter(CV.user_id == user_id).all()

    def analyze_cv(self, cv_id: int) -> CVAnalysis:
        cv = self.get_cv(cv_id)
        if not cv:
            raise ValueError("CV not found")
        
        if not cv.parsed_text:
            raise ValueError("CV text not parsed")
        
        # Analyze CV
        analysis = analyze_cv_text(cv.parsed_text)
        skills = extract_skills(cv.parsed_text)
        
        # Update CV with analysis results
        cv.skills = json.dumps(skills)
        cv.experience = json.dumps(analysis.get("experience", []))
        cv.education = json.dumps(analysis.get("education", []))
        
        self.db.commit()
        self.db.refresh(cv)
        
        return CVAnalysis(
            skills=skills,
            experience=analysis.get("experience", []),
            education=analysis.get("education", []),
            summary=analysis.get("summary", "")
        )

    def _analyze_cv_async(self, cv_id: int):
        # This would typically be a background task
        # For now, we'll do it synchronously
        try:
            self.analyze_cv(cv_id)
        except Exception as e:
            print(f"Error analyzing CV {cv_id}: {e}")
