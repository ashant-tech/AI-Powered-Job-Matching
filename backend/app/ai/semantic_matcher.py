import json
import re
from app.models.cv import CV
from app.models.job import ExternalJob


def _load_list(raw: str | None) -> list[str]:
    """Parse a JSON list of skills (strings or dicts) into lowercase strings."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    items: list[str] = []
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, str):
                items.append(entry.lower().strip())
            elif isinstance(entry, dict):
                for value in entry.values():
                    if isinstance(value, str):
                        items.append(value.lower().strip())
    return [item for item in items if item]


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9+#.]+", text.lower()) if len(t) > 1}


class SemanticMatcher:
    """Rule-based CV↔job relevance scorer.

    Each component returns a score in [0, 1] or None when there is no signal to
    judge on. The final score is the weighted average over the components that
    actually have signal, scaled to 0-100. Unknown components are excluded
    rather than given a neutral baseline, so a job is never inflated just
    because we lack data about it.
    """

    WEIGHTS = {
        "field": 30.0,
        "skill": 35.0,
        "semantic": 20.0,
        "title": 15.0,
    }

    def calculate_match_score(self, cv: CV, job: ExternalJob) -> float:
        components = {
            "field": self._field_alignment(cv, job),
            "skill": self._skill_match(cv, job),
            "semantic": self._semantic_match(cv, job),
            "title": self._title_keyword_match(cv, job),
        }

        total_weight = 0.0
        weighted_sum = 0.0
        for name, value in components.items():
            if value is None:
                continue
            weight = self.WEIGHTS[name]
            weighted_sum += weight * value
            total_weight += weight

        if total_weight == 0.0:
            return 0.0
        return round(100.0 * weighted_sum / total_weight, 2)

    def _field_alignment(self, cv: CV, job: ExternalJob) -> float | None:
        """Reward jobs whose auto-detected field matches the CV's field."""
        cv_field = getattr(cv, "field", None)
        job_field = getattr(job, "field", None)
        if not job_field or job_field == "other":
            return None  # No usable field signal on the job
        if not cv_field or cv_field == "other":
            return None  # No usable field signal on the CV
        return 1.0 if cv_field == job_field else 0.0

    def _skill_match(self, cv: CV, job: ExternalJob) -> float | None:
        cv_skills = _load_list(cv.skills)
        job_skills = _load_list(job.skills)
        if not cv_skills or not job_skills:
            return None
        cv_text_tokens = set().union(*(_tokens(s) for s in cv_skills)) if cv_skills else set()
        hits = 0
        for job_skill in job_skills:
            job_skill_tokens = _tokens(job_skill)
            # Count a job skill as covered if it is an exact CV skill or shares a token.
            if job_skill in cv_skills or (job_skill_tokens & cv_text_tokens):
                hits += 1
        return hits / len(job_skills)

    def _semantic_match(self, cv: CV, job: ExternalJob) -> float | None:
        """Word-overlap similarity between the CV text and the job description."""
        if not cv.parsed_text or not job.description:
            return None
        cv_words = _tokens(cv.parsed_text)
        job_words = _tokens(job.description)
        if not cv_words or not job_words:
            return None
        overlap = len(cv_words & job_words)
        union = len(cv_words | job_words)
        return overlap / union if union else None

    def _title_keyword_match(self, cv: CV, job: ExternalJob) -> float | None:
        """Fraction of CV skills that appear in the job title or requirements."""
        cv_skills = _load_list(cv.skills)
        if not cv_skills:
            return None
        haystack = f"{job.title or ''} {job.requirements or ''}".lower()
        if not haystack.strip():
            return None
        haystack_tokens = _tokens(haystack)
        matched = 0
        for skill in cv_skills:
            skill_tokens = _tokens(skill)
            if skill in haystack or (skill_tokens and skill_tokens <= haystack_tokens):
                matched += 1
        return matched / len(cv_skills)
