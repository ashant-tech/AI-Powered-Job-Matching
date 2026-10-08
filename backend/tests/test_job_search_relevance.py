from types import SimpleNamespace

from app.services.job_service import _search_relevance


def _job(**overrides):
    values = {
        "title": "Office Administrator",
        "skills": '["accounting"]',
        "company": "Example Organization",
        "location": "Addis Ababa",
        "field": "business_finance",
        "job_type": "full-time",
        "requirements": "Degree in business administration",
        "description": "Manage office operations and records.",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_search_does_not_match_a_query_inside_an_unrelated_word():
    assert _search_relevance(_job(), ["it"]) == 0
    assert _search_relevance(_job(), ["data"]) == 0


def test_search_prioritizes_title_and_accepts_common_word_prefixes():
    title_match = _search_relevance(_job(title="Software Engineer"), ["engineer"])
    description_match = _search_relevance(
        _job(title="Office Assistant", description="Support software engineering projects."),
        ["engineer"],
    )

    assert title_match > description_match
    assert description_match > 0


def test_every_meaningful_query_term_must_match():
    assert _search_relevance(_job(title="Python Developer"), ["python", "developer"]) > 0
    assert _search_relevance(_job(title="Python Developer"), ["python", "nurse"]) == 0


def test_search_ignores_common_connecting_words():
    assert _search_relevance(_job(title="Software Engineer"), ["engineer", "in", "jobs"]) > 0
