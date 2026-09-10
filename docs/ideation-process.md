# Ideation Process

## Problem
Job seekers spend hours scanning boards, most listings are irrelevant, and good opportunities are missed because nobody is watching every source continuously.

## Goal
Reduce search time by letting users upload a CV once, then automatically surfacing and notifying them about jobs that fit their skills, education and experience.

## Key decisions
- **CV-first onboarding** – no long forms; the CV is the profile.
- **Explainable matching** – each recommendation shows matched vs. missing skills and a breakdown of the score, so users trust and act on it.
- **Pluggable job sources** – a collector with a simple `JobSource` interface so new boards/RSS feeds can be added without touching the API.
- **Notifications as the core loop** – in-app first, email/SMS optional; users shouldn't need to keep checking.
- **Hybrid AI** – rule-based skill taxonomy for precision + sentence embeddings for recall/semantics; cheap to run and easy to debug, with a clear path to stronger models.

## MVP scope
Register/login → upload CV → view analysis → get ranked recommendations → receive notifications → browse jobs.

## Future
Employer side (post jobs, view candidates), application tracking, CV improvement tips based on missing skills, mobile app.
