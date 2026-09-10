# AI-Powered Job Matching

An AI-based job matching platform for job seekers. Users upload their CV, the system extracts
skills, education and experience, matches them against collected job postings and notifies
users when relevant jobs appear.

## Main Objectives

* Reduce the time spent searching for jobs.
* Analyze CVs using AI (skills, education, experience).
* Match candidates with suitable jobs and show an explainable match score.
* Recommend relevant job opportunities.
* Notify users about new matching jobs.

## Project Status

**MVP scaffold** – all layers are wired end-to-end (auth, CV upload & analysis, jobs, matching, notifications). AI components use a rule-based skill taxonomy plus sentence embeddings and can be upgraded independently.

## Technologies

* Frontend: Next.js, React, TypeScript, Tailwind CSS
* Backend: Python, FastAPI, SQLAlchemy
* AI/NLP: Sentence Transformers (with an offline hashed-embedding fallback), skill taxonomy
* CV Processing: pypdf, python-docx
* Database: PostgreSQL (SQLite for local development)
* Authentication: JWT, bcrypt
* Job Collection: public job APIs / RSS feeds, Python
* Notifications: in-app, email, SMS
* Tools: Git, GitHub, Docker

## Structure

| Directory | Stack | Purpose |
|-----------|-------|---------|
| `frontend/` | Next.js 14, TypeScript, Tailwind | Web UI (landing, auth, dashboard, CV upload, jobs, recommendations, notifications) |
| `backend/` | Python 3.10+, FastAPI, SQLAlchemy | REST API, CV parsing, AI analysis & matching, notifications |
| `job-collector/` | Python | Pulls jobs from external sources, cleans/dedupes, pushes to the API |
| `database/` | SQL / Python | Migrations placeholder and seed script |
| `docs/` | Markdown | Architecture, API, AI model and ideation docs |

## Quick start (local)

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload            # http://localhost:8000/docs
python ../database/seed.py               # demo user + sample jobs

# frontend
cd ../frontend
npm install
npm run dev                              # http://localhost:3000

# job collector (optional)
cd ../job-collector
pip install -r requirements.txt
API_URL=http://localhost:8000 API_TOKEN=<jwt from login> python main.py
```

Demo login after seeding: `demo@example.com` / `password123`.

## Docker

```bash
docker compose up --build
```

Runs Postgres, backend (`:8000`), frontend (`:3000`) and the hourly job collector.

## How matching works

1. CV text is extracted (PDF/DOCX/TXT) and cleaned.
2. `ai/skill_extractor.py` maps text to a canonical skill taxonomy; `ai/cv_analyzer.py` extracts
   education, experience entries and estimates years of experience.
3. `ai/embeddings.py` produces a sentence embedding (`all-MiniLM-L6-v2`, with a hashed fallback
   when the model isn't available).
4. `ai/ranking.py` scores each job: 50% skill overlap + 35% semantic similarity + 15% experience fit.
5. Matches at or above 60% create in-app notifications (plus email/SMS when configured).

See `docs/` for details.
