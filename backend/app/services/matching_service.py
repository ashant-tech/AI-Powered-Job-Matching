from sqlalchemy.orm import Session

import json
from typing import List
from app.models.match import Match
from app.models.job import Job
from app.models.cv import CV
from app.schemas.match import MatchResponse
from app.ai.semantic_matcher import SemanticMatcher
from app.ai.ranking import rank_matches

class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.semantic_matcher = SemanticMatcher()

    def find_matches_for_cv(self, user_id: int, cv_id: int) -> List[MatchResponse]:
        cv = self.db.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            raise ValueError("CV not found")
        
        # Get all active jobs
        jobs = self.db.query(Job).filter(Job.is_active == 1).all()
        
        # Calculate match scores for each job
        matches = []
        for job in jobs:
            match_score = self.semantic_matcher.calculate_match_score(cv, job)
            
            # Create match record
            match = Match(
                user_id=user_id,
                cv_id=cv_id,
                job_id=job.id,
                match_score=match_score,
                match_reasons=json.dumps({"score_breakdown": match_score})
            )
            
            self.db.add(match)
            matches.append(match)
        
        self.db.commit()
        
        # Rank matches
        ranked_matches = rank_matches(matches)
        
        return [MatchResponse.model_validate(match) for match in ranked_matches]

    def get_user_matches(self, user_id: int) -> List[MatchResponse]:
        matches = self.db.query(Match).filter(Match.user_id == user_id).all()
        return [MatchResponse.model_validate(match) for match in matches]

    def get_match(self, match_id: int) -> Match:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def update_match_status(self, match_id: int, status: str) -> Match:
        match = self.get_match(match_id)
        if not match:
            raise ValueError("Match not found")
        
        match.status = status
        self.db.commit()
        self.db.refresh(match)
        
        return match

    def get_top_matches(self, user_id: int, limit: int = 10) -> List[MatchResponse]:
        matches = self.db.query(Match).filter(
            Match.user_id == user_id,
            Match.status == "pending"
        ).order_by(Match.match_score.desc()).limit(limit).all()
        
        return [MatchResponse.model_validate(match) for match in matches]
