from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.match import MatchOut
from app.services import matching_service

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post("/run", response_model=list[MatchOut])
def run_matching(
    cv_id: int | None = None,
    limit: int = Query(20, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return matching_service.compute_matches(db, user, cv_id, limit)


@router.get("/recommendations", response_model=list[MatchOut])
def recommendations(limit: int = Query(20, le=100), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return matching_service.list_matches(db, user, limit)
