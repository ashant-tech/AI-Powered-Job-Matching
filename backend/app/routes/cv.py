from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.cv import CVCreate, CVResponse, CVAnalysis
from app.services.cv_service import CVService
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.post("/upload", response_model=CVResponse)
async def upload_cv(
    file: UploadFile = File(...),
    title: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cv_service = CVService(db)
    
    if not title:
        title = file.filename
    
    return cv_service.upload_cv(current_user.id, file, title)

@router.get("/{cv_id}", response_model=CVResponse)
async def get_cv(cv_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    cv_service = CVService(db)
    
    cv = cv_service.get_cv(cv_id)
    if not cv or cv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    return cv

@router.get("/user/{user_id}", response_model=list[CVResponse])
async def get_user_cvs(user_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    cv_service = CVService(db)
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these CVs"
        )
    return cv_service.get_user_cvs(user_id)

@router.post("/{cv_id}/analyze", response_model=CVAnalysis)
async def analyze_cv(cv_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    cv_service = CVService(db)
    
    cv = cv_service.get_cv(cv_id)
    if not cv or cv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    return cv_service.analyze_cv(cv_id)
