import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.ai.cv_analyzer import analyze_cv
from app.ai.embeddings import embed_text
from app.config.settings import settings
from app.cv_processing.text_cleaner import extract_text
from app.middleware.error_handler import AppError
from app.models.cv import CV
from app.models.skill import Skill
from app.models.user import User

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_SIZE = 10 * 1024 * 1024


def get_or_create_skills(db: Session, names: list[str]) -> list[Skill]:
    existing = {s.name: s for s in db.query(Skill).filter(Skill.name.in_(names)).all()} if names else {}
    skills = []
    for name in names:
        skill = existing.get(name)
        if skill is None:
            skill = Skill(name=name)
            db.add(skill)
        skills.append(skill)
    return skills


async def save_and_analyze_cv(db: Session, user: User, upload: UploadFile) -> CV:
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AppError("Only PDF, DOCX and TXT files are supported", 415)
    content = await upload.read()
    if len(content) > MAX_SIZE:
        raise AppError("File exceeds 10MB limit", 413)

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{user.id}_{uuid.uuid4().hex}{ext}"
    path.write_bytes(content)

    text = extract_text(str(path))
    if not text:
        path.unlink(missing_ok=True)
        raise AppError("Could not extract any text from the CV", 422)
    analysis = analyze_cv(text)

    cv = CV(
        user_id=user.id,
        file_name=upload.filename or path.name,
        file_path=str(path),
        raw_text=text,
        summary=analysis.summary,
        education=analysis.education,
        experience=analysis.experience,
        years_of_experience=analysis.years_of_experience,
        embedding=embed_text(text),
    )
    cv.skills = get_or_create_skills(db, analysis.skills)
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv


def list_user_cvs(db: Session, user: User) -> list[CV]:
    return db.query(CV).filter(CV.user_id == user.id).order_by(CV.created_at.desc(), CV.id.desc()).all()


def get_latest_cv(db: Session, user: User) -> CV | None:
    return db.query(CV).filter(CV.user_id == user.id).order_by(CV.created_at.desc(), CV.id.desc()).first()


def delete_cv(db: Session, user: User, cv_id: int) -> None:
    cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == user.id).first()
    if cv is None:
        raise AppError("CV not found", 404)
    Path(cv.file_path).unlink(missing_ok=True)
    db.delete(cv)
    db.commit()
