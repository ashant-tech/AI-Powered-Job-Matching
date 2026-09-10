from app.ai.embeddings import cosine_similarity


def semantic_score(cv_embedding: list[float] | None, job_embedding: list[float] | None) -> float:
    sim = cosine_similarity(cv_embedding, job_embedding)
    return max(0.0, min(1.0, (sim + 1) / 2))


def skill_overlap(cv_skills: set[str], job_skills: set[str]) -> tuple[float, list[str], list[str]]:
    if not job_skills:
        return 0.5, [], []
    matched = sorted(cv_skills & job_skills)
    missing = sorted(job_skills - cv_skills)
    return len(matched) / len(job_skills), matched, missing


def experience_score(cv_years: float, required_years: float) -> float:
    if required_years <= 0:
        return 1.0
    return max(0.0, min(1.0, cv_years / required_years))
