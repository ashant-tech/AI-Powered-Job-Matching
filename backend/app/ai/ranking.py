from dataclasses import dataclass

from app.ai.semantic_matcher import experience_score, semantic_score, skill_overlap
from app.models.cv import CV
from app.models.job import Job

WEIGHTS = {"skill": 0.5, "semantic": 0.35, "experience": 0.15}


@dataclass
class MatchResult:
    job: Job
    score: float
    skill_score: float
    semantic_score: float
    experience_score: float
    matched_skills: list[str]
    missing_skills: list[str]


def score_job(cv: CV, job: Job) -> MatchResult:
    cv_skills = {s.name for s in cv.skills}
    job_skills = {s.name for s in job.skills}
    sk, matched, missing = skill_overlap(cv_skills, job_skills)
    sem = semantic_score(cv.embedding, job.embedding)
    exp = experience_score(cv.years_of_experience, job.min_years_experience)
    total = WEIGHTS["skill"] * sk + WEIGHTS["semantic"] * sem + WEIGHTS["experience"] * exp
    return MatchResult(job, round(total * 100, 2), round(sk * 100, 2), round(sem * 100, 2), round(exp * 100, 2), matched, missing)


def rank_jobs(cv: CV, jobs: list[Job], min_score: float = 0.0) -> list[MatchResult]:
    results = [score_job(cv, job) for job in jobs]
    return sorted((r for r in results if r.score >= min_score), key=lambda r: r.score, reverse=True)
