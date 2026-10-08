from processors.duplicate_detector import DuplicateDetector


def test_remove_duplicates_merges_cross_source_copies_and_keeps_direct_link():
    description = (
        "Responsible for managing financial reports, budgets, reconciliations, monthly closes, "
        "regulatory filings, audit support, and internal controls across the organization."
    )
    jobs = [
        {
            "external_id": "telegram-101",
            "title": "Finance Officer",
            "company": "Example Microfinance",
            "location": "Addis Ababa",
            "description": description,
            "source": "Telegram",
            "source_url": "https://t.me/jobs/101",
        },
        {
            "external_id": "website-finance-officer",
            "title": "Job Vacancy: Finance Officer",
            "company": "Example Microfinance",
            "location": "Addis Ababa, Ethiopia",
            "description": description,
            "source": "Ethiojobs",
            "apply_url": "https://careers.example.com/finance-officer",
        },
    ]

    unique_jobs = DuplicateDetector().remove_duplicates(jobs)

    assert len(unique_jobs) == 1
    assert unique_jobs[0]["apply_url"] == "https://careers.example.com/finance-officer"
