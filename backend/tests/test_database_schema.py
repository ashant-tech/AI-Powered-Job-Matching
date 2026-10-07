from sqlalchemy import create_engine, inspect, text

from app.config.database import Base, ensure_schema
from app.models.cv import CV  # noqa: F401 - registers the CV table with Base.metadata
from app.models.user import User  # noqa: F401 - registers the referenced users table


def test_ensure_schema_adds_enhanced_cv_columns_to_existing_database():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE cvs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL,
                file_name VARCHAR NOT NULL,
                parsed_text TEXT,
                skills TEXT,
                experience TEXT,
                education TEXT,
                field VARCHAR,
                experience_level VARCHAR(50),
                total_years_experience INTEGER,
                job_titles TEXT,
                contact_info TEXT
            )
        """))

    try:
        ensure_schema(engine)
        ensure_schema(engine)

        columns = {column["name"] for column in inspect(engine).get_columns("cvs")}
        assert {
            "achievements",
            "certifications",
            "projects",
            "languages",
            "soft_skills",
        } <= columns
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
