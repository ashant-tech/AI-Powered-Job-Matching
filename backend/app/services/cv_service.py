from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
import json

from app.models.cv import CV
from app.models.match import Match
from app.schemas.cv import CVCreate, CVAnalysis
from app.config.settings import settings
from app.cv_processing.pdf_parser import parse_pdf
from app.cv_processing.docx_parser import parse_docx
from app.cv_processing.text_cleaner import clean_text
from app.ai.cv_analyzer import analyze_cv_text
from app.ai.skill_extractor import extract_skills
from app.services.field_classifier import classify_cv
from app.services.matching_service import MatchingService

class CVService:
    def __init__(self, db: Session):
        self.db = db

    def upload_cv(self, user_id: int, file: UploadFile, title: str) -> CV:
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        file_bytes = file.file.read()
        file_extension = file.filename.split('.')[-1].lower()
        file_path = f"{settings.UPLOAD_DIR}/{user_id}_{title}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
        
        # Parse CV based on file type
        parsed_text = ""
        if file_extension == "pdf":
            parsed_text = parse_pdf(file_path)
        elif file_extension == "docx":
            parsed_text = parse_docx(file_path)
        else:
            parsed_text = clean_text(file_bytes.decode('utf-8'))
        
        db_cv = self.db.query(CV).filter(CV.user_id == user_id).first()
        if db_cv:
            self.db.query(Match).filter(Match.user_id == user_id, Match.cv_id == db_cv.id).delete()
            db_cv.title = title
            db_cv.file_path = file_path
            db_cv.file_name = file.filename
            db_cv.parsed_text = parsed_text
            db_cv.skills = None
            db_cv.experience = None
            db_cv.education = None
            db_cv.field = None
            db_cv.experience_level = None
            db_cv.total_years_experience = None
            db_cv.job_titles = None
            db_cv.contact_info = None
        else:
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

        # Find available jobs immediately after CV analysis so new matches notify the user.
        try:
            MatchingService(self.db).find_matches_for_cv(user_id, db_cv.id)
        except Exception as e:
            print(f"Error finding matches for CV {db_cv.id}: {e}")
        
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
        cv.experience_level = analysis.get("experience_level")
        cv.total_years_experience = analysis.get("total_years_experience")
        cv.job_titles = json.dumps(analysis.get("job_titles", []))
        cv.contact_info = json.dumps(analysis.get("contact_info", {}))
        
        # Store enhanced analysis data
        cv.achievements = json.dumps(analysis.get("achievements", []))
        cv.certifications = json.dumps(analysis.get("certifications", []))
        cv.projects = json.dumps(analysis.get("projects", []))
        cv.languages = json.dumps(analysis.get("languages", []))
        cv.soft_skills = json.dumps(analysis.get("soft_skills", []))

        # Auto-detect the user's field from the CV itself (education + skills + text)
        cv.field = classify_cv(cv.parsed_text or "", cv.skills or "", cv.education or "")
        
        self.db.commit()
        self.db.refresh(cv)
        
        return CVAnalysis(
            skills=skills,
            experience=analysis.get("experience", []),
            education=analysis.get("education", []),
            summary=analysis.get("summary", ""),
            field=cv.field,
            experience_level=analysis.get("experience_level"),
            total_years_experience=analysis.get("total_years_experience"),
            job_titles=analysis.get("job_titles"),
            contact_info=analysis.get("contact_info")
        )

    def _analyze_cv_async(self, cv_id: int):
        # This would typically be a background task
        # For now, we'll do it synchronously
        try:
            self.analyze_cv(cv_id)
        except Exception as e:
            print(f"Error analyzing CV {cv_id}: {e}")
