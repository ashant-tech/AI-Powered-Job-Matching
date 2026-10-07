from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Lightweight column migrations: create_all never alters existing tables,
# so new columns are added here (runs on backend startup and in the collector).
_COLUMN_MIGRATIONS = {
    "users": {
        "department": "VARCHAR"
    },
    "external_jobs": {"field": "VARCHAR"},
    "cvs": {
        "field": "VARCHAR",
        "experience_level": "VARCHAR(50)",
        "total_years_experience": "INTEGER",
        "job_titles": "TEXT",
        "contact_info": "TEXT",
        "achievements": "TEXT",
        "certifications": "TEXT",
        "projects": "TEXT",
        "languages": "TEXT",
        "soft_skills": "TEXT",
    },
    "notifications": {
        "external_job_ids": "TEXT"
    },
}


def ensure_schema(target_engine=None):
    """Create missing tables and add missing columns (idempotent)."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    inspector = inspect(eng)
    for table, columns in _COLUMN_MIGRATIONS.items():
        if table not in inspector.get_table_names():
            continue
        existing = {col["name"] for col in inspector.get_columns(table)}
        for column, col_type in columns.items():
            if column not in existing:
                with eng.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
