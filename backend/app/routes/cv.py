from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.cv import CVOut
from app.services import cv_service

router = APIRouter(prefix="/api/cv", tags=["cv"])


@router.post("/upload", response_model=CVOut, status_code=201)
async def upload_cv(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await cv_service.save_and_analyze_cv(db, user, file)


@router.get("", response_model=list[CVOut])
def list_cvs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cv_service.list_user_cvs(db, user)


@router.get("/latest", response_model=CVOut | None)
def latest_cv(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cv_service.get_latest_cv(db, user)


@router.delete("/{cv_id}", status_code=204)
def delete_cv(cv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    cv_service.delete_cv(db, user, cv_id)
