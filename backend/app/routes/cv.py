from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.cv import CVCreate, CVResponse, CVAnalysis
from app.services.cv_service import CVService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/upload", response_model=CVResponse)
async def upload_cv(
    file: UploadFile = File(...),
    title: str = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    cv_service = CVService(db)
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not title:
        title = file.filename
    
    return cv_service.upload_cv(user.id, file, title)

@router.get("/{cv_id}", response_model=CVResponse)
async def get_cv(cv_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cv_service = CVService(db)
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    cv = cv_service.get_cv(cv_id)
    if not cv or cv.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    return cv

@router.get("/user/{user_id}", response_model=list[CVResponse])
async def get_user_cvs(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cv_service = CVService(db)
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these CVs"
        )
    return cv_service.get_user_cvs(user_id)

@router.post("/{cv_id}/analyze", response_model=CVAnalysis)
async def analyze_cv(cv_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cv_service = CVService(db)
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    cv = cv_service.get_cv(cv_id)
    if not cv or cv.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    return cv_service.analyze_cv(cv_id)
