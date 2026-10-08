import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai.semantic_matcher import SemanticMatcher
from app.models.cv import CV
from app.models.job import ExternalJob


def _cv(field="computer_it", skills='["python", "django", "sql", "machine learning"]'):
    return CV(
        user_id=1, title="CV", file_path="/tmp/cv.txt", file_name="cv.txt",
        parsed_text="Computer science graduate. Python, Django, SQL, machine learning, data analysis.",
        skills=skills, field=field,
    )


def _job(field, title, skills="", description="", requirements=""):
    return ExternalJob(
        external_id=f"job-{title[:5]}", title=title, company="Co", field=field,
        skills=skills, description=description, requirements=requirements,
        apply_url="https://example.com/x",
    )


def test_score_is_on_zero_to_hundred_scale():
    matcher = SemanticMatcher()
    job = _job("computer_it", "Data Scientist", skills='["python", "machine learning", "sql"]',
               description="Build machine learning models with python and sql.")
    score = matcher.calculate_match_score(_cv(), job)
    assert 0.0 <= score <= 100.0
    # A strongly field- and skill-aligned job must score well above a 0-1 fraction.
    assert score > 50.0


def test_relevant_field_outranks_unrelated():
    matcher = SemanticMatcher()
    cv = _cv()
    relevant = _job("computer_it", "Data Scientist", skills='["python", "machine learning"]',
                    description="machine learning with python")
    unrelated = _job("health", "Registered Nurse", skills='["patient care"]',
                     description="hospital patient care")
    assert matcher.calculate_match_score(cv, relevant) > matcher.calculate_match_score(cv, unrelated)


def test_missing_signal_does_not_inflate_score():
    """A job with no skills/description should not get a ~50% neutral floor."""
    matcher = SemanticMatcher()
    empty = _job("other", "Mystery Role")  # no field match, no skills, no description
    assert matcher.calculate_match_score(_cv(), empty) < 10.0


def test_field_match_alone_is_below_recommendation_threshold():
    from app.services.matching_service import MIN_MATCH_SCORE

    matcher = SemanticMatcher()
    cv = _cv(skills="[]")
    job = _job("computer_it", "Office Coordinator")

    assert matcher.calculate_match_score(cv, job) < MIN_MATCH_SCORE


def test_skill_matching_requires_a_real_skill_match_not_a_shared_word():
    matcher = SemanticMatcher()
    cv = _cv(skills='["machine"]')
    job = _job("computer_it", "Machine Learning Engineer", skills='["machine learning"]')

    assert matcher._skill_match(cv, job) == 0.0


def test_skill_matching_normalizes_common_aliases():
    matcher = SemanticMatcher()
    cv = _cv(skills='["js", "python3"]')
    job = _job("computer_it", "Developer", skills='["javascript", "python"]')

    assert matcher._skill_match(cv, job) == 1.0


def test_match_details_use_cv_roles_and_explicit_experience_requirements():
    matcher = SemanticMatcher()
    cv = _cv(skills='["python", "sql"]')
    cv.job_titles = '["Software Developer"]'
    cv.experience = '[{"title": "Software Developer"}]'
    cv.total_years_experience = 2
    job = _job(
        "computer_it",
        "Senior Software Engineer",
        skills='["python", "sql", "aws"]',
        description="Build and maintain software applications using Python and SQL.",
        requirements="At least 5 years of experience.",
    )

    details = matcher.calculate_match_with_details(cv, job)

    assert details["component_scores"]["role"] >= 0.8
    assert details["component_scores"]["experience"] == 0.4
    assert details["score_confidence"] > 80
    assert any("2 of 3 skills" in reason for reason in details["match_reasons"])
    assert any("asks for about 5+ years" in reason for reason in details["match_reasons"])


def test_experience_reason_is_not_claimed_without_job_level_evidence():
    matcher = SemanticMatcher()
    cv = _cv()
    cv.experience_level = "Senior"
    job = _job("computer_it", "Software Developer", description="Build software applications.")

    details = matcher.calculate_match_with_details(cv, job)

    assert details["component_scores"]["experience"] is None
    assert not any("experience level" in reason.lower() for reason in details["match_reasons"])


def test_company_tenure_is_not_mistaken_for_candidate_experience_requirement():
    matcher = SemanticMatcher()
    cv = _cv()
    cv.total_years_experience = 0
    cv.experience_level = "Entry Level"
    job = _job(
        "computer_it",
        "Senior Software Developer",
        description="Our company has operated for 20 years.",
    )

    assert matcher._required_years(job) is None
    assert matcher._experience_match(cv, job) is None


def test_placeholder_cv_experience_does_not_count_as_confirmed_work_history():
    matcher = SemanticMatcher()
    cv = _cv()
    cv.total_years_experience = 0
    cv.experience_level = "Entry Level"
    cv.experience = '[{"title": "Position", "years": "Not specified"}]'
    job = _job("computer_it", "Developer", requirements="3 years of experience required.")

    assert matcher._experience_match(cv, job) is None


def test_sparse_job_listing_has_low_score_confidence_and_is_not_a_strong_fit():
    matcher = SemanticMatcher()
    cv = _cv()
    job = _job("computer_it", "Office Coordinator")

    details = matcher.calculate_match_with_details(cv, job)

    assert details["score_confidence"] < 25
    assert details["fit_level"] == "Possible"
    assert details["match_caveats"]
    assert details["match_score"] < 45
