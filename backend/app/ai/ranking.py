from typing import List
from app.models.match import Match

def rank_matches(matches: List[Match]) -> List[Match]:
    """
    Rank matches by match score and other factors.
    """
    if not matches:
        return []
    
    # Sort by match score (descending)
    ranked = sorted(matches, key=lambda x: x.match_score, reverse=True)
    
    # Apply additional ranking factors
    ranked = _apply_time_decay(ranked)
    ranked = _apply_diversity_boost(ranked)
    
    return ranked

def _apply_time_decay(matches: List[Match]) -> List[Match]:
    """
    Apply time decay to matches - newer matches get a slight boost.
    """
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    
    for match in matches:
        if match.created_at > one_week_ago:
            # Boost recent matches by 2%
            match.match_score = min(match.match_score * 1.02, 100.0)
    
    return matches

def _apply_diversity_boost(matches: List[Match]) -> List[Match]:
    """
    Apply diversity boost to avoid clustering of similar job types.
    """
    if len(matches) <= 1:
        return matches
    
    # Simplified diversity boost - in production, would load job data
    # For now, just return matches as-is
    return matches

def calculate_match_quality_score(match: Match) -> float:
    """
    Calculate a quality score for a match considering multiple factors.
    """
    quality_score = match.match_score
    
    # Factor in match status
    if match.status == "viewed":
        quality_score *= 0.9  # Slightly lower if already viewed
    elif match.status == "applied":
        quality_score *= 0.8  # Lower if already applied
    
    return round(quality_score, 2)

def filter_low_quality_matches(matches: List[Match], threshold: float = 30.0) -> List[Match]:
    """
    Filter out matches below a quality threshold.
    """
    return [match for match in matches if match.match_score >= threshold]

def get_match_explanation(match: Match) -> dict:
    """
    Generate an explanation for why a match scored the way it did.
    """
    explanation = {
        "overall_score": match.match_score,
        "factors": []
    }
    
    # Skill matching factor
    if match.cv and match.cv.skills:
        try:
            import json
            cv_skills = json.loads(match.cv.skills)
            explanation["factors"].append({
                "factor": "Skill Alignment",
                "impact": "High",
                "details": f"Found {len(cv_skills)} relevant skills in your CV"
            })
        except:
            pass
    
    # Experience factor
    if match.cv and match.cv.experience:
        explanation["factors"].append({
            "factor": "Experience Match",
            "impact": "Medium",
            "details": "Your experience aligns with job requirements"
        })
    
    # Location factor
    if match.job and match.job.location:
        explanation["factors"].append({
            "factor": "Location",
            "impact": "Medium",
            "details": f"Job location: {match.job.location}"
        })
    
    return explanation
