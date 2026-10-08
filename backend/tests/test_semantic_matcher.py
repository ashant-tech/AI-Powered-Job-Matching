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
