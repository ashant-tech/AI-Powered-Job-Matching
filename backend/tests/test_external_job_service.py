from app.services.external_job_service import ExternalJobService


def test_external_job_service_accepts_trusted_job_url(monkeypatch):
    monkeypatch.setenv("TRUSTED_JOB_DOMAINS", "trustedjobs.example")
    service = ExternalJobService()

    job = service._to_external_job(
        {
            "id": "job-1",
            "title": "Python Developer",
            "company": "Example Co",
            "description": "Build APIs",
            "url": "https://careers.trustedjobs.example/jobs/job-1",
        },
        "https://api.trustedjobs.example/jobs",
    )

    assert job is not None
    assert job.apply_url == "https://careers.trustedjobs.example/jobs/job-1"


def test_external_job_service_rejects_untrusted_or_insecure_url(monkeypatch):
    monkeypatch.setenv("TRUSTED_JOB_DOMAINS", "trustedjobs.example")
    service = ExternalJobService()

    assert not service._is_trusted_url("http://trustedjobs.example/jobs")
    assert not service._is_trusted_url("https://untrusted.example/jobs")
    assert service._to_external_job(
        {
            "title": "Python Developer",
            "company": "Example Co",
            "description": "Build APIs",
            "url": "https://untrusted.example/jobs/job-1",
        },
        "https://api.trustedjobs.example/jobs",
    ) is None