from types import SimpleNamespace
from unittest.mock import patch

from app.models.job import ExternalJob
from app.services.job_service import JobService


def _job(external_id, title, skills, field="computer_it"):
    return ExternalJob(
        external_id=external_id,
        title=title,
        company="Example Co",
        description=title,
        field=field,
        skills=skills,
        is_active=True,
    )


def _service(jobs):
    class ExternalJobs:
        def fetch_jobs(self):
            return jobs

    service = JobService.__new__(JobService)
    service.db = None
    return service, ExternalJobs()


def test_recommendations_exclude_jobs_without_cv_skill_overlap():
    jobs = [
        _job("recommend-python", "Python Developer", '["python", "sql"]'),
        _job("recommend-unrelated", "Patient Care Assistant", '["patient care"]'),
    ]
    service, external_jobs = _service(jobs)
    user = SimpleNamespace(id=1, department="Computer Science")
    cv = SimpleNamespace(field="computer_it", skills='["python"]')

    with patch("app.services.job_service.ExternalJobService", return_value=external_jobs):
        recommendations = service.get_recommended_jobs(user, cv=cv)

    assert [job.external_id for job in recommendations] == ["recommend-python"]


def test_recommendations_without_field_or_skills_do_not_return_every_job():
    jobs = [_job("unrelated", "Patient Care Assistant", '["patient care"]', field="health")]
    service, external_jobs = _service(jobs)
    user = SimpleNamespace(id=1, department=None)
    cv = SimpleNamespace(field="other", skills="[]")

    with patch("app.services.job_service.ExternalJobService", return_value=external_jobs):
        recommendations = service.get_recommended_jobs(user, cv=cv)

    assert recommendations == []
