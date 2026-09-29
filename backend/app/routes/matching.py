from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.config.database import get_db
from app.schemas.match import MatchResponse, MatchUpdate
from app.services.matching_service import MatchingService
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.models.match import Match
from app.models.notification import Notification
from app.models.job import ExternalJob

router = APIRouter()

@router.get("/stats", response_model=dict)
async def get_user_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get real user statistics for dashboard"""
    try:
        # Count total matches for user
        total_matches = db.query(Match).filter(Match.user_id == current_user.id).count()
        # Count pending applications (matches with status 'pending')
        pending_applications = db.query(Match).filter(
            Match.user_id == current_user.id,
            Match.status == "pending"
        ).count()
        # Count unread notifications
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()
        # For viewed jobs, we'll use matches with status 'viewed' as a proxy
        viewed_jobs = db.query(Match).filter(
            Match.user_id == current_user.id,
            Match.status == "viewed"
        ).count()
        return {
            "totalMatches": total_matches,
            "pendingApplications": pending_applications,
            "viewedJobs": viewed_jobs,
            "unreadNotifications": unread_notifications
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/recent-activity", response_model=list)
async def get_recent_activity(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recent activity for the user"""
    try:
        # Get recent notifications
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(desc(Notification.created_at)).limit(5).all()
        # Get recent matches
        recent_matches = db.query(Match).filter(
            Match.user_id == current_user.id
        ).order_by(desc(Match.created_at)).limit(5).all()
        # Combine and format activity
        activities = []

        for notification in notifications:
            activities.append({
                'type': 'notification',
                'title': notification.title,
                'message': notification.message,
                'time': notification.created_at,
                'is_read': notification.is_read
            })
        for match in recent_matches:
            job = db.query(ExternalJob).filter(ExternalJob.external_id == match.external_job_id).first()
            if job:
                activities.append({
                    'type': 'match',
                    'title': f"New match: {job.title}",
                    'message': f"Match score: {match.match_score}%",
                    'company': job.company,
                    'time': match.created_at,
                    'status': match.status
                })
        # Sort by time and return top 5
        activities.sort(key=lambda x: x['time'], reverse=True)
        return activities[:5]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.post("/cv/{cv_id}", response_model=list[MatchResponse])
async def find_matches(cv_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    matching_service = MatchingService(db)
    try:
        return matching_service.find_matches_for_cv(current_user.id, cv_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

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
    try:
        return matching_service.update_match_status(match_id, match_update.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
