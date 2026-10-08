# Changelog

This file records user-facing features and notable fixes by the date they were committed to the repository. Dates use the repository's commit history.

## 2026-10-09

### Added

- Refreshed the signed-in CV upload experience with a responsive upload flow, real drag-and-drop, file preview/removal, and clearer CV status and profile review panels.
- Improved text readability across the app by enlarging small helper text, increasing contrast for muted copy and placeholders, and setting a consistent default text color.
- Updated the README to describe the current system, setup, deployment, and limitations.

### Fixed

- Prevented optional match-notification failures from turning successfully calculated recommendations into failed match requests.
- Added traceback and request-path logging for otherwise unhandled backend errors while keeping client error responses generic.

## 2026-10-08

### Added

- Added explanations to CV-based recommendations, including fit level, confidence, matched skills, skill gaps, and relevant caveats.
- Added CV profile review and correction for skills, work field, experience, prior job titles, and education.
- Added relevant / not relevant feedback on recommendations to modestly adjust similar future matches.
- Added cross-source job deduplication and richer-record merging in collection and backend ingestion.
- Refreshed the login, registration, dashboard, jobs, recommendations, and profile experiences.
- Added public navigation between the home, sign-in, registration, and browse-jobs pages.

### Changed

- Improved browse search ranking and filter updates to reduce unrelated results.
- Tightened job-field classification, personalized recommendation filtering, and CV match thresholds to suppress weak or unrelated matches.
- Reduced matching memory risk by loading the optional embedding model only once and keeping embeddings disabled by default on small hosts.
- Updated salary negotiation examples for Ethiopian monthly ETB compensation.

## 2026-10-07

### Added

- Expanded CV extraction and matching signals, including structured skills, experience, and profile information.
- Improved interview preparation and salary negotiation guidance.

### Fixed

- Kept a CV upload successful if the follow-up matching operation fails.
- Added startup schema migration support for the enhanced CV profile fields.

## 2026-10-04

### Added

- Added career guidance, resume analysis, interview preparation, career transition, workplace culture, learning, salary, and network tools.

### Changed

- Routed frontend API requests through the deployed backend proxy.

## 2026-10-01

### Added

- Added viewed-job tracking and updated dashboard activity counts to reflect match statuses more accurately.

## 2026-09-30

### Added

- Added scheduled hourly job collection for the deployed service.
- Expanded the configured Telegram job-channel list.

### Changed

- Improved collector-side duplicate detection across job sources.

## 2026-09-29

### Added

- Added password reset flows and email configuration.
- Expanded dashboard statistics and recent activity.
- Added user work-department data to help personalize job recommendations.

## 2026-09-28

### Added

- Expanded CV analysis and job filtering, with additional profile signals available to recommendations.
- Improved the job-search and recommendation interfaces with clearer filtering and match details.

## 2026-09-27

### Added

- Added production deployment configuration, API rate limits for authentication, database setup/migration support, and health checks.
- Added job-field classification and stricter field-aware matching.
- Improved PDF text extraction, including OCR support for scanned CVs.

## 2026-09-26

### Added

- Added live job collection from public Telegram previews and Ethiojobs, including application deadlines.
- Added deadline parsing and expiry handling for job listings and related matches.

## 2026-09-22

### Changed

- Changed job matching to use trusted external listings without relying on a local seeded job catalog.
- Updated CV replacement and matching behavior for the single-CV workflow.

## 2026-09-20

### Added

- Expanded Ethiopian job collection sources.
- Added Telegram notification preferences and richer job-match notifications.

## 2026-09-18

### Added

- Added automatic matching when jobs are collected or a CV is uploaded.
- Added in-app and optional Telegram notifications for new matches.
- Added duplicate-match prevention during repeated matching runs.

## 2026-09-09 to 2026-09-15

### Added

- Established the initial Next.js frontend, FastAPI backend, database, and job-collector structure.
- Added account registration/authentication, CV upload and analysis, job browsing, match scoring, profiles, notifications, and collaboration invitations.
- Added the initial job-source integrations, Telegram notifications, Docker setup, and test configuration.
