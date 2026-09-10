# System Architecture

```
+-------------+       HTTPS/JSON       +----------------+        SQL        +------------+
|  Frontend   | <--------------------> |   Backend API  | <---------------> | PostgreSQL |
|  (Next.js)  |                        |   (FastAPI)    |                   +------------+
+-------------+                        +----------------+
                                          ^        |
                        POST /api/jobs    |        | email / SMS
                                          |        v
                                   +---------------+   +------------------+
                                   | Job Collector |   | Notification svc |
                                   +---------------+   +------------------+
                                          ^
                                          | HTTP
                              external job boards / RSS feeds
```

## Components

- **Frontend** – Next.js App Router. Talks to the API via `src/services/*` using a JWT stored in `localStorage`.
- **Backend** – FastAPI, layered as `routes -> services -> models`. AI logic lives in `app/ai`, file parsing in `app/cv_processing`.
- **Job collector** – standalone script/container. Fetches from sources, cleans and dedupes, then posts jobs through the API so the backend embeds and indexes them uniformly.
- **Database** – PostgreSQL in Docker; SQLite by default for local dev. Tables: users, cvs, jobs, skills, cv_skills, job_skills, matches, notifications.

## Data flow

1. User registers/logs in → JWT.
2. User uploads CV → text extraction → skill/education/experience extraction → embedding → stored `CV`.
3. User requests recommendations (`POST /api/matching/run`) → every active job scored against the latest CV → `Match` rows upserted → high scores create `Notification`s.
4. Job collector inserts new jobs → `match_all_users_for_job` can be invoked to notify existing users (hook for a scheduler/worker).

## Deployment

`docker-compose.yml` runs all services. For production swap SQLite for Postgres (already wired), set a strong `SECRET_KEY`, configure SMTP, and put the frontend and API behind a reverse proxy.
