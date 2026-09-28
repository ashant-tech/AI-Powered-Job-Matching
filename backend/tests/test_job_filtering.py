import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.database import SessionLocal
from app.models.job import ExternalJob
from app.services.job_service import JobService

client = TestClient(app)


def test_remote_filtering():
    """Test that remote_only filter correctly identifies remote jobs."""
    db = SessionLocal()

    # Create test jobs with unique IDs to avoid conflicts
    test_id = str(uuid.uuid4())[:8]

    # Remote job (by job_type)
    remote_job = ExternalJob(
        external_id=f"remote1_{test_id}",
        title="Remote Developer",
        company="Tech Co",
        description="Remote position",
        job_type="remote",
        location="Remote",
        is_active=True
    )

    # Remote job (by location)
    remote_job2 = ExternalJob(
        external_id=f"remote2_{test_id}",
        title="Software Engineer",
        company="Startup",
        description="Work from anywhere",
        job_type="full-time",
        location="Remote",
        is_active=True
    )

    # Non-remote job
    onsite_job = ExternalJob(
        external_id=f"onsite1_{test_id}",
        title="Onsite Developer",
        company="Corp Inc",
        description="Office position",
        job_type="full-time",
        location="New York",
        is_active=True
    )

    db.add_all([remote_job, remote_job2, onsite_job])
    db.commit()

    try:
        job_service = JobService(db)

        # Test remote_only filter - filter only our test jobs
        all_test_jobs = job_service.get_jobs()
        our_test_jobs = [job for job in all_test_jobs if test_id in job.external_id]

        remote_test_jobs = [job for job in our_test_jobs if job_service._is_remote(job)]
        assert len(remote_test_jobs) == 2
        assert all(job_service._is_remote(job) for job in remote_test_jobs)

        # Test without remote filter
        assert len(our_test_jobs) == 3

        # Test with field filter combined - set field to computer_it for remote jobs
        remote_job.field = "computer_it"
        remote_job2.field = "computer_it"
        db.commit()

        remote_computer_jobs = job_service.get_jobs(remote_only=True, field="computer_it")
        remote_computer_test_jobs = [job for job in remote_computer_jobs if test_id in job.external_id]
        # Should only return our remote jobs that also match computer field
        assert len(remote_computer_test_jobs) == 2

    finally:
        # Cleanup
        db.query(ExternalJob).filter(ExternalJob.external_id.like(f"%{test_id}%")).delete()
        db.commit()
        db.close()


def test_salary_filtering():
    """Test that salary range filters work correctly."""
    test_id = str(uuid.uuid4())[:8]

    db = SessionLocal()

    # Create test jobs with different salaries
    low_salary_job = ExternalJob(
        external_id=f"salary1_{test_id}",
        title="Junior Developer",
        company="Small Co",
        description="Entry level",
        salary_min=30000,
        salary_max=50000,
        is_active=True
    )

    mid_salary_job = ExternalJob(
        external_id=f"salary2_{test_id}",
        title="Senior Developer",
        company="Medium Co",
        description="Mid level",
        salary_min=60000,
        salary_max=80000,
        is_active=True
    )

    high_salary_job = ExternalJob(
        external_id=f"salary3_{test_id}",
        title="Lead Developer",
        company="Big Co",
        description="Senior level",
        salary_min=100000,
        salary_max=150000,
        is_active=True
    )

    db.add_all([low_salary_job, mid_salary_job, high_salary_job])
    db.commit()

    try:
        job_service = JobService(db)

        # Helper function to filter only our test jobs
        def filter_test_jobs(jobs):
            return [job for job in jobs if test_id in job.external_id]

        # Test minimum salary filter
        high_paying_jobs = job_service.get_jobs(salary_min=70000)
        high_paying_test_jobs = filter_test_jobs(high_paying_jobs)
        assert len(high_paying_test_jobs) >= 1  # At least the high salary job
        assert all(job.salary_min >= 70000 for job in high_paying_test_jobs)

        # Test maximum salary filter
        low_paying_jobs = job_service.get_jobs(salary_max=70000)
        low_paying_test_jobs = filter_test_jobs(low_paying_jobs)
        assert len(low_paying_test_jobs) >= 1  # At least the low salary job
        assert all(job.salary_max <= 70000 for job in low_paying_test_jobs)

        # Test salary range filter
        mid_range_jobs = job_service.get_jobs(salary_min=55000, salary_max=90000)
        mid_range_test_jobs = filter_test_jobs(mid_range_jobs)
        assert len(mid_range_test_jobs) >= 1  # At least the mid salary job
        assert all(55000 <= job.salary_min <= 90000 for job in mid_range_test_jobs)

    finally:
        # Cleanup
        db.query(ExternalJob).filter(ExternalJob.external_id.like(f"%{test_id}%")).delete()
        db.commit()
        db.close()


def test_combination_filters():
    """Test that multiple filters work together correctly."""
    test_id = str(uuid.uuid4())[:8]

    db = SessionLocal()

    # Create test jobs with various attributes
    remote_computer_job = ExternalJob(
        external_id=f"combo1_{test_id}",
        title="Remote Python Developer",
        company="Tech Startup",
        description="Remote Python position",
        job_type="remote",
        location="Remote",
        field="computer_it",
        salary_min=80000,
        salary_max=120000,
        is_active=True
    )

    onsite_computer_job = ExternalJob(
        external_id=f"combo2_{test_id}",
        title="Onsite Java Developer",
        company="Enterprise Corp",
        description="Office Java position",
        job_type="full-time",
        location="San Francisco",
        field="computer_it",
        salary_min=90000,
        salary_max=130000,
        is_active=True
    )

    remote_health_job = ExternalJob(
        external_id=f"combo3_{test_id}",
        title="Remote Nurse",
        company="Health System",
        description="Remote healthcare position",
        job_type="remote",
        location="Remote",
        field="health",
        salary_min=60000,
        salary_max=80000,
        is_active=True
    )

    db.add_all([remote_computer_job, onsite_computer_job, remote_health_job])
    db.commit()

    try:
        job_service = JobService(db)

        # Helper function to filter only our test jobs
        def filter_test_jobs(jobs):
            return [job for job in jobs if test_id in job.external_id]

        # Test remote + computer field combination
        remote_computer_jobs = job_service.get_jobs(remote_only=True, field="computer_it")
        remote_computer_test_jobs = filter_test_jobs(remote_computer_jobs)
        assert len(remote_computer_test_jobs) == 1
        assert remote_computer_test_jobs[0].external_id == f"combo1_{test_id}"

        # Test remote + salary combination
        remote_high_salary = job_service.get_jobs(remote_only=True, salary_min=70000)
        remote_high_salary_test_jobs = filter_test_jobs(remote_high_salary)
        assert len(remote_high_salary_test_jobs) >= 1  # At least one remote high salary job
        assert all(job_service._is_remote(job) for job in remote_high_salary_test_jobs)
        assert all(job.salary_min >= 70000 for job in remote_high_salary_test_jobs)

        # Test field + salary combination
        computer_mid_salary = job_service.get_jobs(field="computer_it", salary_min=85000, salary_max=125000)
        computer_mid_salary_test_jobs = filter_test_jobs(computer_mid_salary)
        assert len(computer_mid_salary_test_jobs) == 1
        assert computer_mid_salary_test_jobs[0].external_id == f"combo1_{test_id}"

        # Test all filters combined
        specific_job = job_service.get_jobs(
            remote_only=True,
            field="computer_it",
            salary_min=75000,
            salary_max=125000
        )
        specific_job_test_jobs = filter_test_jobs(specific_job)
        assert len(specific_job_test_jobs) == 1
        assert specific_job_test_jobs[0].external_id == f"combo1_{test_id}"

    finally:
        # Cleanup
        db.query(ExternalJob).filter(ExternalJob.external_id.like(f"%{test_id}%")).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
