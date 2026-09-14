from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.match import MatchResponse, MatchUpdate
from app.services.matching_service import MatchingService
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.post("/cv/{cv_id}", response_model=list[MatchResponse])
async def find_matches(cv_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    matching_service = MatchingService(db)
    return matching_service.find_matches_for_cv(current_user.id, cv_id)

@router.get("/user/{user_id}", response_model=list[MatchResponse])
async def get_user_matches(user_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    matching_service = MatchingService(db)
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these matches"
        )
    return matching_service.get_user_matches(user_id)

@router.put("/{match_id}", response_model=MatchResponse)
async def update_match_status(match_id: int, match_update: MatchUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    matching_service = MatchingService(db)
    
    match = matching_service.get_match(match_id)
    if not match or match.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return matching_service.update_match_status(match_id, match_update.status)
