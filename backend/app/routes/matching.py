from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.config.database import get_db
from app.schemas.match import MatchResponse, MatchUpdate
from app.services.matching_service import MatchingService
from app.services.auth_service import AuthService
from app.services.career_guidance_service import CareerGuidanceService
from app.services.resume_analysis_service import ResumeAnalysisService
from app.services.interview_preparation_service import InterviewPreparationService
from app.services.company_culture_service import CompanyCultureService
from app.services.career_transition_service import CareerTransitionService
from app.services.learning_service import LearningService
from app.services.salary_negotiation_service import SalaryNegotiationService
from app.services.network_analysis_service import NetworkAnalysisService
from app.middleware.auth import get_current_user
from app.models.match import Match
from app.models.notification import Notification
from app.models.job import ExternalJob
from app.models.cv import CV
from app.models.user import User

router = APIRouter()

@router.get("/stats", response_model=dict)
async def get_user_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get real user statistics for dashboard"""
    try:
        # Count total matches for user
        total_matches = db.query(Match).filter(Match.user_id == current_user.id).count()
        # Pending applications = matches the user hasn't applied to yet (still
        # actionable). Viewing a job doesn't clear it from this funnel.
        pending_applications = db.query(Match).filter(
            Match.user_id == current_user.id,
            Match.status.in_(["pending", "viewed"])
        ).count()
        # Count unread notifications
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()
        # Viewed jobs = opened the detail; applying implies it was viewed too.
        viewed_jobs = db.query(Match).filter(
            Match.user_id == current_user.id,
            Match.status.in_(["viewed", "applied"])
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

@router.get("/career-guidance", response_model=dict)
async def get_career_guidance(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get career path guidance for the current user."""
    try:
        career_service = CareerGuidanceService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Get career path guidance
        career_path = career_service.get_career_path(current_user, cv)

        return career_path
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/career-guidance/skill-gaps", response_model=dict)
async def get_skill_gaps(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get skill gaps analysis for reaching the next career level."""
    try:
        career_service = CareerGuidanceService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Get skill gaps analysis
        skill_gaps = career_service.get_skill_gaps_for_next_level(current_user, cv)

        return skill_gaps
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/career-guidance/roadmap", response_model=list)
async def get_career_roadmap(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get complete career roadmap from current level to executive."""
    try:
        career_service = CareerGuidanceService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Get career roadmap
        roadmap = career_service.get_career_roadmap(current_user, cv)

        return roadmap
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/resume-analysis", response_model=dict)
async def get_resume_analysis(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get AI-powered resume analysis and improvement suggestions."""
    try:
        resume_service = ResumeAnalysisService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CV found. Please upload your CV first."
            )

        # Analyze resume
        analysis = resume_service.analyze_resume(cv)

        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/resume-analysis/tips", response_model=list)
async def get_resume_optimization_tips(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get general resume optimization tips for user's field."""
    try:
        resume_service = ResumeAnalysisService()

        # Get user's CV to determine field
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CV found. Please upload your CV first."
            )

        # Determine field
        field = cv.field if cv.field and cv.field != "other" else "computer_it"

        # Get optimization tips
        tips = resume_service.get_resume_optimization_tips(field)

        return tips
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

# Interview Preparation Endpoints
@router.get("/interview-preparation/{job_id}", response_model=dict)
async def get_interview_preparation(job_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get interview preparation for a specific job."""
    try:
        interview_service = InterviewPreparationService()

        # Get job
        job = db.query(ExternalJob).filter(ExternalJob.external_id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Generate interview questions
        questions = interview_service.generate_interview_questions(job, cv)

        return questions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/interview-preparation/mock/{job_id}", response_model=dict)
async def get_mock_interview(job_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a complete mock interview session."""
    try:
        interview_service = InterviewPreparationService()

        # Get job
        job = db.query(ExternalJob).filter(ExternalJob.external_id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Generate mock interview
        mock_interview = interview_service.generate_mock_interview(job, cv)

        return mock_interview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.post("/interview-preparation/analyze-answer", response_model=dict)
async def analyze_answer(question: str, answer: str):
    """Analyze the quality of an interview answer."""
    try:
        interview_service = InterviewPreparationService()

        # Analyze answer
        analysis = interview_service.analyze_answer_quality(question, answer)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/interview-preparation/salary-scenarios", response_model=list)
async def get_salary_scenarios():
    """Get salary negotiation scenarios for practice."""
    try:
        interview_service = InterviewPreparationService()

        # Get all scenarios
        scenarios = interview_service.get_all_salary_scenarios()

        return scenarios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

# Company Culture Matching Endpoints
@router.get("/company-culture/{job_id}", response_model=dict)
async def analyze_company_culture(job_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analyze company culture for a specific job."""
    try:
        culture_service = CompanyCultureService()

        # Get job
        job = db.query(ExternalJob).filter(ExternalJob.external_id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Analyze company culture
        culture_analysis = culture_service.analyze_company_culture(job)

        return culture_analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/company-culture/match/{job_id}", response_model=dict)
async def match_company_culture(job_id: str, work_style: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Match company culture with user's work style."""
    try:
        culture_service = CompanyCultureService()

        # Get job
        job = db.query(ExternalJob).filter(ExternalJob.external_id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Match culture
        culture_match = culture_service.match_culture_fit(job, work_style)

        return culture_match
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

# Career Transition Endpoints
@router.get("/career-transition/{target_field}", response_model=dict)
async def analyze_career_transition(target_field: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analyze career transition to a different field."""
    try:
        transition_service = CareerTransitionService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CV found. Please upload your CV first."
            )

        # Analyze transition
        transition_analysis = transition_service.analyze_transferable_skills(cv, target_field)

        return transition_analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/career-transition/paths", response_model=list)
async def get_transition_paths(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all possible career transition paths."""
    try:
        transition_service = CareerTransitionService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CV found. Please upload your CV first."
            )

        # Get all transition paths
        paths = transition_service.get_all_transition_paths(cv)

        return paths
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/career-transition/timeline/{target_field}", response_model=dict)
async def get_transition_timeline(target_field: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get estimated timeline for career transition."""
    try:
        transition_service = CareerTransitionService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CV found. Please upload your CV first."
            )

        # Get timeline
        timeline = transition_service.get_transition_timeline(cv, target_field)

        return timeline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

# Learning Service Endpoints
@router.get("/learning/plan", response_model=dict)
async def get_learning_plan(career_goal: Optional[str] = None, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get personalized learning plan."""
    try:
        learning_service = LearningService()

        # Get user and CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No CV found. Please upload your CV first."
            )

        # Create learning plan
        learning_plan = learning_service.create_personalized_learning_plan(current_user, cv, career_goal)

        return learning_plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/learning/courses/{skill}", response_model=dict)
async def get_course_recommendations(skill: str, field: str = "computer_it"):
    """Get course recommendations for a specific skill."""
    try:
        learning_service = LearningService()

        # Get course recommendations
        courses = learning_service.recommend_courses(skill, field)

        return courses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.post("/learning/progress", response_model=dict)
async def track_learning_progress(user_progress: dict):
    """Track and analyze learning progress."""
    try:
        learning_service = LearningService()

        # Track progress
        progress = learning_service.track_learning_progress(user_progress)

        return progress
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/learning/quiz/{skill}", response_model=dict)
async def get_skill_quiz(skill: str):
    """Get micro-assessment quiz for skill validation."""
    try:
        learning_service = LearningService()

        # Get quiz
        quiz = learning_service.get_skill_validation_quizzes(skill)

        return quiz
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

# Salary Negotiation Endpoints
@router.get("/salary-analysis/{job_id}", response_model=dict)
async def analyze_job_offer(job_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Evaluate a job offer against market rates."""
    try:
        salary_service = SalaryNegotiationService()

        # Get job
        job = db.query(ExternalJob).filter(ExternalJob.external_id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Evaluate offer
        offer_analysis = salary_service.evaluate_job_offer(job, cv)

        return offer_analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/salary/market-analysis", response_model=dict)
async def get_market_salary_analysis(field: str, experience_level: str, location: str = "other"):
    """Get market salary analysis for a field and experience level."""
    try:
        salary_service = SalaryNegotiationService()

        # Analyze market salary
        market_analysis = salary_service.analyze_market_salary(field, experience_level, location)

        return market_analysis
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.post("/salary/negotiation-script", response_model=dict)
async def generate_negotiation_script(job_id: str, target_salary: int, user_strengths: list, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate personalized salary negotiation script."""
    try:
        salary_service = SalaryNegotiationService()

        # Get job
        job = db.query(ExternalJob).filter(ExternalJob.external_id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Generate script
        script = salary_service.generate_negotiation_script(job, target_salary, user_strengths)

        return script
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.post("/salary/benefits-analysis", response_model=dict)
async def analyze_benefits_package(benefits: dict):
    """Analyze and score a benefits package."""
    try:
        salary_service = SalaryNegotiationService()

        # Analyze benefits
        benefits_analysis = salary_service.analyze_benefits_package(benefits)

        return benefits_analysis
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

# Network Analysis Endpoints
@router.get("/network/analysis", response_model=dict)
async def analyze_network(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analyze user's networking potential and provide recommendations."""
    try:
        network_service = NetworkAnalysisService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Analyze network
        network_analysis = network_service.analyze_network_potential(current_user, cv)

        return network_analysis
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/network/weak-ties", response_model=dict)
async def identify_weak_ties(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Identify potential weak ties from CV that could lead to opportunities."""
    try:
        network_service = NetworkAnalysisService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Identify weak ties
        weak_ties = network_service.identify_weak_ties(cv)

        return weak_ties
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.get("/network/action-plan", response_model=dict)
async def get_networking_action_plan(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a comprehensive networking action plan."""
    try:
        network_service = NetworkAnalysisService()

        # Get user's CV
        cv = db.query(CV).filter(CV.user_id == current_user.id).first()

        # Generate action plan
        action_plan = network_service.generate_networking_action_plan(current_user, cv)

        return action_plan
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))
