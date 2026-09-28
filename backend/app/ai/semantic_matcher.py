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

    def calculate_match_with_details(self, cv: CV, job: ExternalJob) -> dict:
        """Calculate match score with detailed reasons and skill gaps."""
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
            match_score = 0.0
        else:
            match_score = round(100.0 * weighted_sum / total_weight, 2)

        # Generate detailed match reasons
        match_reasons = self._generate_match_reasons(cv, job, components)

        # Calculate skill gaps
        skill_gaps = self._calculate_skill_gaps(cv, job)

        return {
            "match_score": match_score,
            "match_reasons": match_reasons,
            "skill_gaps": skill_gaps,
            "component_scores": {
                "field": components["field"],
                "skill": components["skill"],
                "semantic": components["semantic"],
                "title": components["title"]
            }
        }

    def _generate_match_reasons(self, cv: CV, job: ExternalJob, components: dict) -> list[str]:
        """Generate human-readable reasons for the match."""
        reasons = []

        # Field alignment reason
        if components["field"] is not None and components["field"] > 0:
            cv_field = getattr(cv, "field", None)
            job_field = getattr(job, "field", None)
            if cv_field and job_field:
                reasons.append(f"Your field ({cv_field}) matches the job's field ({job_field})")

        # Skill match reason
        if components["skill"] is not None:
            cv_skills = _load_list(cv.skills)
            job_skills = _load_list(job.skills)
            if cv_skills and job_skills:
                matched_skills = self._get_matched_skills(cv_skills, job_skills)
                if matched_skills:
                    reasons.append(f"You have {len(matched_skills)} of the required skills: {', '.join(matched_skills[:5])}")

        # Semantic match reason
        if components["semantic"] is not None and components["semantic"] > 0.3:
            reasons.append("Your CV content shows strong semantic similarity to the job description")

        # Title match reason
        if components["title"] is not None and components["title"] > 0.5:
            reasons.append("Your skills align well with the job title and requirements")

        # Experience level match
        if hasattr(cv, 'experience_level') and cv.experience_level:
            reasons.append(f"Your experience level ({cv.experience_level}) is relevant for this position")

        return reasons

    def _calculate_skill_gaps(self, cv: CV, job: ExternalJob) -> dict:
        """Calculate missing skills and provide recommendations."""
        cv_skills = _load_list(cv.skills)
        job_skills = _load_list(job.skills)

        if not job_skills:
            return {
                "missing_skills": [],
                "recommended_skills": [],
                "gap_percentage": 0
            }

        missing_skills = []
        cv_skills_lower = [skill.lower() for skill in cv_skills]

        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            # Check if the job skill is in CV skills
            if not any(job_skill_lower in cv_skill or cv_skill in job_skill_lower
                      for cv_skill in cv_skills_lower):
                missing_skills.append(job_skill)

        # Generate skill recommendations based on missing skills
        recommended_skills = self._generate_skill_recommendations(missing_skills, cv_skills)

        gap_percentage = len(missing_skills) / len(job_skills) * 100 if job_skills else 0

        return {
            "missing_skills": missing_skills,
            "recommended_skills": recommended_skills,
            "gap_percentage": round(gap_percentage, 2)
        }

    def _get_matched_skills(self, cv_skills: list[str], job_skills: list[str]) -> list[str]:
        """Get the list of skills that match between CV and job."""
        matched = []
        cv_skills_lower = [skill.lower() for skill in cv_skills]

        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            if any(job_skill_lower in cv_skill or cv_skill in job_skill_lower
                  for cv_skill in cv_skills_lower):
                matched.append(job_skill)

        return matched

    def _generate_skill_recommendations(self, missing_skills: list[str], cv_skills: list[str]) -> list[str]:
        """Generate recommendations for filling skill gaps."""
        recommendations = []

        # Simple recommendations based on skill categories
        skill_categories = {
            "programming": ["python", "javascript", "java", "c++", "go", "rust"],
            "web": ["react", "angular", "vue", "html", "css", "typescript"],
            "data": ["sql", "pandas", "numpy", "spark", "hadoop"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
            "devops": ["ci/cd", "jenkins", "git", "terraform", "ansible"]
        }

        for missing_skill in missing_skills:
            missing_lower = missing_skill.lower()

            # Check if it's related to a skill the user already has
            for category, skills in skill_categories.items():
                if any(missing_lower in skill or skill in missing_lower for skill in skills):
                    if any(category_skill in cv_skill for cv_skill in cv_skills
                          for category_skill in skills):
                        recommendations.append(f"Consider learning {missing_skill} to complement your existing {category} skills")
                        break
            else:
                recommendations.append(f"Consider learning {missing_skill} to meet job requirements")

        return recommendations[:5]  # Limit to top 5 recommendations

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
