import hashlib
import json
import re
from app.models.cv import CV
from app.models.job import ExternalJob

# Embedding models like all-MiniLM-L6-v2 truncate input at 256 word-piece
# tokens, so a full multi-page CV is silently cut off. Chunking keeps every
# part in play; ~120 words stays safely under the token cap.
_CHUNK_WORDS = 120
_CHUNK_OVERLAP = 20
_MAX_CHUNKS = 16

# Re-encoding the same CV/job text for every candidate pair dominates the cost
# of matching all users against all jobs, so cache normalized chunk embeddings.
_EMBED_CACHE: dict[str, object] = {}
_EMBED_CACHE_MAX = 512


def _chunk_text(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    if len(words) <= _CHUNK_WORDS:
        return [text]
    chunks: list[str] = []
    step = _CHUNK_WORDS - _CHUNK_OVERLAP
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + _CHUNK_WORDS]))
        if len(chunks) >= _MAX_CHUNKS or start + _CHUNK_WORDS >= len(words):
            break
    return chunks


def _load_list(raw: object) -> list[str]:
    """Parse a JSON list of skills (strings or dicts) into lowercase strings."""
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            data = re.split(r"[,;\n]", raw)
    else:
        data = raw
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


def _structured_entries(raw: object) -> list[dict]:
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
    if isinstance(raw, list):
        return [entry for entry in raw if isinstance(entry, dict)]
    return []


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9+#.]+", text.lower()) if len(t) > 1}


_SKILL_ALIASES = {
    "js": "javascript",
    "ecmascript": "javascript",
    "py": "python",
    "python3": "python",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node js": "node.js",
    "postgres": "postgresql",
    "k8s": "kubernetes",
}
_ROLE_STOP_WORDS = {"and", "at", "for", "of", "the", "with", "senior", "junior", "lead", "principal"}
_EXPERIENCE_LEVELS = {
    "intern": 0,
    "trainee": 0,
    "entry": 0,
    "junior": 1,
    "associate": 1,
    "mid": 2,
    "intermediate": 2,
    "senior": 3,
    "lead": 4,
    "principal": 4,
    "manager": 4,
    "director": 5,
}


def _canonical_skill(skill: str) -> str:
    normalized = " ".join(token for token in re.split(r"[^a-z0-9+#.]+", skill.lower()) if token)
    return _SKILL_ALIASES.get(normalized, normalized)


def _role_tokens(title: str) -> set[str]:
    return _tokens(title) - _ROLE_STOP_WORDS


# The embedding model is loaded at most once per process. MatchingService (and
# therefore SemanticMatcher) is constructed per request, so an instance-level
# load would re-import torch on every request and exhaust memory on small hosts
# like Render's free tier - which surfaces as health-check timeouts.
_SHARED_MODEL = None
_SHARED_MODEL_TRIED = False


def _get_shared_embedding_model():
    global _SHARED_MODEL, _SHARED_MODEL_TRIED
    if _SHARED_MODEL_TRIED:
        return _SHARED_MODEL
    _SHARED_MODEL_TRIED = True
    from app.config.settings import settings
    if not settings.SEMANTIC_EMBEDDINGS:
        # Disabled by default: torch + the model exceed small-host memory and
        # stall match requests. Use the synonym word-overlap path instead.
        return None
    try:
        from sentence_transformers import SentenceTransformer
        _SHARED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as exc:
        print(f"Warning: embedding model unavailable ({exc}); falling back to synonym word overlap")
        _SHARED_MODEL = None
    return _SHARED_MODEL


class SemanticMatcher:
    """CV↔job relevance scorer using actual semantic similarity (embeddings).

    Uses sentence-transformers for true semantic matching, not just word overlap.
    "Software engineer" and "developer" will now match because they have similar meanings,
    not because they share words.
    """

    WEIGHTS = {
        "field": 10.0,
        "skill": 40.0,
        "semantic": 20.0,
        "title": 10.0,
        "role": 12.0,
        "experience": 5.0,
        "education": 3.0,
    }

    def __init__(self):
        self.synonym_map = {}
        self.embedding_model = _get_shared_embedding_model()
        if self.embedding_model is None:
            self._build_synonym_map()

    def _build_synonym_map(self):
        """Build a synonym map for enhanced semantic matching without embeddings."""
        self.synonym_map = {
            # Software/Development synonyms
            "software": ["software engineer", "developer", "programmer", "coding", "programming"],
            "developer": ["software engineer", "programmer", "coder", "developer"],
            "engineer": ["software engineer", "developer", "programmer", "architect"],
            "programmer": ["developer", "software engineer", "coder", "software"],
            "coding": ["programming", "development", "software development"],
            "programming": ["coding", "software development", "development"],
            
            # Web development
            "web": ["frontend", "backend", "full stack", "web development"],
            "frontend": ["ui", "user interface", "client-side", "front-end"],
            "backend": ["server-side", "api", "server", "back-end"],
            "full stack": ["fullstack", "full-stack", "frontend and backend"],
            
            # Data
            "data": ["analytics", "data science", "database", "data analysis"],
            "analytics": ["data analysis", "data science", "business intelligence"],
            "database": ["db", "sql", "nosql", "data storage"],
            
            # Cloud/DevOps
            "cloud": ["aws", "azure", "gcp", "infrastructure", "cloud computing"],
            "devops": ["deployment", "ci/cd", "operations", "infrastructure"],
            "aws": ["amazon web services", "cloud", "infrastructure"],
            "docker": ["container", "containers", "virtualization"],
            "kubernetes": ["k8s", "orchestration", "containers"],
            
            # Management
            "manager": ["management", "lead", "supervisor", "team lead"],
            "leadership": ["manager", "team lead", "supervisor", "management"],
            "team": ["group", "squad", "department", "unit"],
            
            # Business
            "business": ["finance", "accounting", "marketing", "sales", "operations"],
            "finance": ["accounting", "financial", "money", "budget"],
            "marketing": ["promotion", "advertising", "branding", "sales"],
            "sales": ["revenue", "business development", "selling"],
            
            # Common skill synonyms
            "javascript": ["js", "ecmascript", "scripting"],
            "python": ["py", "python3", "scripting"],
            "java": ["jvm", "object-oriented"],
            "react": ["reactjs", "ui framework", "frontend"],
            "angular": ["angularjs", "framework", "typescript"],
            "sql": ["database", "query", "relational database"],
            "api": ["rest", "restful", "interface", "web service"],
        }

    def _get_embedding(self, text: str) -> list:
        """Get embedding for text using the model."""
        if self.embedding_model is None:
            return None
        try:
            return self.embedding_model.encode(text)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two embedding vectors."""
        if not vec1 or not vec2:
            return 0.0
        try:
            import numpy as np
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot_product / (norm1 * norm2)
        except ImportError:
            # Fallback if numpy not available
            return 0.0

    def _embed_chunks(self, text: str):
        """Return L2-normalized embeddings for each chunk of text (cached)."""
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cached = _EMBED_CACHE.get(key)
        if cached is not None:
            return cached
        import numpy as np
        chunks = _chunk_text(text)
        if not chunks:
            return None
        vectors = np.asarray(self.embedding_model.encode(chunks), dtype=float)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0.0] = 1e-8
        vectors = vectors / norms
        if len(_EMBED_CACHE) >= _EMBED_CACHE_MAX:
            _EMBED_CACHE.clear()
        _EMBED_CACHE[key] = vectors
        return vectors

    def _chunked_similarity(self, cv_text: str, job_text: str) -> float | None:
        """Mean over job chunks of the best-matching CV chunk (cosine).

        Scoring the job description segment-by-segment beats a single
        whole-text cosine, which the model's token cap would truncate anyway.
        """
        cv_vectors = self._embed_chunks(cv_text)
        job_vectors = self._embed_chunks(job_text)
        if cv_vectors is None or job_vectors is None:
            return None
        sim = job_vectors @ cv_vectors.T  # (n_job, n_cv)
        return float(sim.max(axis=1).mean())

    def calculate_match_score(self, cv: CV, job: ExternalJob) -> float:
        return self.calculate_match_with_details(cv, job)["match_score"]

    def _calculate_components(self, cv: CV, job: ExternalJob) -> dict[str, float | None]:
        components = {
            "field": self._field_alignment(cv, job),
            "skill": self._skill_match(cv, job),
            "semantic": self._semantic_match(cv, job),
            "title": self._title_keyword_match(cv, job),
            "role": self._role_match(cv, job),
            "experience": self._experience_match(cv, job),
            "education": self._education_match(cv, job),
        }
        return components

    def calculate_match_with_details(self, cv: CV, job: ExternalJob) -> dict:
        """Calculate match score with detailed reasons and skill gaps."""
        components = self._calculate_components(cv, job)

        total_weight = sum(self.WEIGHTS.values())
        weighted_sum = sum(
            self.WEIGHTS[name] * value
            for name, value in components.items()
            if value is not None
        )
        match_score = round(100.0 * weighted_sum / total_weight, 2) if total_weight else 0.0
        confidence = round(
            100.0 * sum(self.WEIGHTS[name] for name, value in components.items() if value is not None)
            / total_weight,
            2,
        ) if total_weight else 0.0

        match_reasons = self._generate_match_reasons(cv, job, components)
        skill_gaps = self._calculate_skill_gaps(cv, job)
        if match_score >= 75 and confidence >= 60:
            fit_level = "Strong"
        elif match_score >= 55 and confidence >= 40:
            fit_level = "Good"
        else:
            fit_level = "Possible"

        caveats = []
        if confidence < 40:
            caveats.append("This estimate is based on limited CV or job details.")
        if not job.description and not job.requirements:
            caveats.append("The employer provided little role detail, so this fit may be incomplete.")

        return {
            "match_score": match_score,
            "match_reasons": match_reasons,
            "skill_gaps": skill_gaps,
            "fit_level": fit_level,
            "score_confidence": confidence,
            "match_caveats": caveats,
            "component_scores": components,
        }

    def _generate_match_reasons(self, cv: CV, job: ExternalJob, components: dict) -> list[str]:
        reasons = []
        if components["field"] is not None and components["field"] > 0:
            cv_field = getattr(cv, "field", None)
            job_field = getattr(job, "field", None)
            if cv_field and job_field:
                reasons.append(f"Your CV field ({cv_field}) aligns with this job's field ({job_field}).")

        cv_skills = _load_list(cv.skills)
        job_skills = _load_list(job.skills)
        matched_skills = self._get_matched_skills(cv_skills, job_skills)
        if job_skills:
            reasons.append(
                f"{len(matched_skills)} of {len(job_skills)} skills mentioned by the employer "
                f"also appear in your CV"
                + (f": {', '.join(matched_skills[:5])}." if matched_skills else ".")
            )

        role_titles = self._cv_role_titles(cv)
        if role_titles and components["role"] is not None and components["role"] > 0:
            reasons.append(
                f"Your previous role{'' if len(role_titles) == 1 else 's'} "
                f"({', '.join(role_titles[:2])}) overlap with this position."
            )

        if components["experience"] is not None:
            required_years = self._required_years(job)
            if required_years is not None:
                cv_years = getattr(cv, "total_years_experience", None)
                reasons.append(
                    f"The job asks for about {required_years}+ years of experience; "
                    f"your CV lists {cv_years}."
                )
            elif self._job_experience_level(job) is not None:
                reasons.append(
                    f"Your listed experience level ({cv.experience_level}) is considered "
                    "alongside this role's seniority."
                )

        if components["education"] is not None and components["education"] > 0:
            reasons.append("Your listed education aligns with the education requested in the job.")

        if components["semantic"] is not None and components["semantic"] >= 0.25:
            reasons.append("Your CV experience and the job description cover related work.")
        return reasons

    def _calculate_skill_gaps(self, cv: CV, job: ExternalJob) -> dict:
        cv_skills = _load_list(cv.skills)
        job_skills = _load_list(job.skills)

        if not job_skills:
            return {
                "missing_skills": [],
                "recommended_skills": [],
                "gap_percentage": 0,
                "matched_skills": [],
            }

        matched_skills = self._get_matched_skills(cv_skills, job_skills)
        matched_canonical = {_canonical_skill(skill) for skill in matched_skills}
        missing_skills = [
            skill for skill in job_skills if _canonical_skill(skill) not in matched_canonical
        ]
        recommended_skills = self._generate_skill_recommendations(missing_skills, cv_skills)
        gap_percentage = len(missing_skills) / len(job_skills) * 100 if job_skills else 0

        return {
            "missing_skills": missing_skills,
            "recommended_skills": recommended_skills,
            "gap_percentage": round(gap_percentage, 2),
            "matched_skills": matched_skills,
        }

    def _get_matched_skills(self, cv_skills: list[str], job_skills: list[str]) -> list[str]:
        cv_skill_set = {_canonical_skill(skill) for skill in cv_skills}
        return [
            skill for skill in dict.fromkeys(job_skills)
            if _canonical_skill(skill) in cv_skill_set
        ]

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

    def _cv_role_titles(self, cv: CV) -> list[str]:
        titles = _load_list(cv.job_titles)
        titles.extend(
            str(entry.get("title", "")).strip()
            for entry in _structured_entries(cv.experience)
            if entry.get("title")
            and str(entry["title"]).strip().casefold() not in {"position", "job title", "not specified"}
        )
        return list(dict.fromkeys(
            title for title in titles
            if title and title.casefold() not in {"position", "job title", "not specified"}
        ))

    def _role_match(self, cv: CV, job: ExternalJob) -> float | None:
        cv_titles = self._cv_role_titles(cv)
        job_title = getattr(job, "title", "") or ""
        if not cv_titles or not job_title:
            return None

        job_terms = _role_tokens(job_title)
        job_family = self._role_family(job_title)
        similarities = []
        for cv_title in cv_titles:
            cv_terms = _role_tokens(cv_title)
            union = job_terms | cv_terms
            overlap = len(job_terms & cv_terms) / len(union) if union else 0.0
            if job_family and job_family == self._role_family(cv_title):
                overlap = max(overlap, 0.85)
            similarities.append(overlap)
        return max(similarities, default=0.0)

    @staticmethod
    def _role_family(title: str) -> str | None:
        normalized = title.lower()
        if any(term in normalized for term in ("software", "developer", "programmer", "web engineer")):
            return "software development"
        return None

    def _experience_match(self, cv: CV, job: ExternalJob) -> float | None:
        required_years = self._required_years(job)
        cv_years = getattr(cv, "total_years_experience", None)
        has_role_history = bool(self._cv_role_titles(cv))
        if required_years is not None and cv_years is not None and (cv_years > 0 or has_role_history):
            if required_years <= 0:
                return 1.0
            return min(max(cv_years, 0) / required_years, 1.0)

        cv_level = self._experience_level(getattr(cv, "experience_level", None))
        job_level = self._job_experience_level(job)
        if cv_level == 0 and not has_role_history:
            cv_level = None
        if cv_level is None or job_level is None:
            return None
        return max(0.0, 1.0 - max(0, job_level - cv_level) * 0.3)

    @staticmethod
    def _required_years(job: ExternalJob) -> int | None:
        requirements = getattr(job, "requirements", "") or ""
        description = getattr(job, "description", "") or ""
        patterns = (
            r"\b(\d{1,2})\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:relevant\s+|professional\s+)?experience\b",
            r"\bexperience\b.{0,30}?\b(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b",
        )
        for text in (requirements, description):
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    return max(int(value) for value in matches)

        # Some listings use a terse "5+ years" requirement with no noun.
        terse_requirement = re.search(r"\b(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b", requirements.lower())
        return int(terse_requirement.group(1)) if terse_requirement else None

    def _job_experience_level(self, job: ExternalJob) -> int | None:
        title = (getattr(job, "title", "") or "").lower()
        return self._experience_level(title)

    @staticmethod
    def _experience_level(value: str | None) -> int | None:
        if not value:
            return None
        normalized = value.lower()
        for name, level in _EXPERIENCE_LEVELS.items():
            if name in normalized:
                return level
        return None

    def _education_match(self, cv: CV, job: ExternalJob) -> float | None:
        job_text = f"{getattr(job, 'title', '') or ''} {getattr(job, 'requirements', '') or ''} {getattr(job, 'description', '') or ''}".lower()
        degree_terms = {
            "bachelor", "bachelors", "b.sc", "b.a", "master", "masters", "m.sc",
            "m.a", "phd", "doctorate", "diploma", "degree", "mba", "associate",
        }
        requested_terms = {term for term in degree_terms if term in job_text}
        if not requested_terms:
            return None

        education = _structured_entries(cv.education)
        if not education:
            return None
        cv_education = " ".join(
            str(value) for entry in education for value in entry.values()
        ).lower()
        matching_terms = {term for term in requested_terms if term in cv_education}
        if matching_terms:
            return 1.0
        if any(term in cv_education for term in ("bachelor", "bachelors", "b.sc", "degree")):
            return 0.5
        return 0.0

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
        cv_skills = list({_canonical_skill(skill) for skill in _load_list(cv.skills)})
        job_skills = list({_canonical_skill(skill) for skill in _load_list(job.skills)})
        if not cv_skills or not job_skills:
            return None
        return len(set(cv_skills) & set(job_skills)) / len(job_skills)

    def _semantic_match(self, cv: CV, job: ExternalJob) -> float | None:
        """Semantic similarity using sentence embeddings (not just word overlap)."""
        if not cv.parsed_text or not (job.description or job.requirements):
            return None
        job_text = f"{job.description or ''} {job.requirements or ''}"
        
        # Try to use embeddings for true semantic matching
        if self.embedding_model is not None:
            try:
                similarity = self._chunked_similarity(cv.parsed_text, job_text)
                if similarity is not None:
                    return similarity
            except Exception as e:
                print(f"Error in semantic matching: {e}")
        
        # Fallback to enhanced word overlap with synonyms
        cv_words = _tokens(cv.parsed_text)
        job_words = _tokens(job_text)
        if not cv_words or not job_words:
            return None
        
        # Expand words with synonyms
        cv_words_expanded = self._expand_with_synonyms(cv_words)
        job_words_expanded = self._expand_with_synonyms(job_words)
        
        overlap = len(cv_words_expanded & job_words_expanded)
        union = len(cv_words_expanded | job_words_expanded)
        return overlap / union if union else None

    def _expand_with_synonyms(self, words: set[str]) -> set[str]:
        """Expand word set with synonyms for better semantic matching."""
        expanded = set(words)
        for word in words:
            if word in self.synonym_map:
                expanded.update(self.synonym_map[word])
        return expanded

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
            skill_tokens = _tokens(_canonical_skill(skill))
            if skill_tokens and skill_tokens <= haystack_tokens:
                matched += 1
        return matched / len(cv_skills)
