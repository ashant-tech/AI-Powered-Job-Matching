"""One-shot data migration: SQLite (backend/job_matching.db) -> Postgres.

Usage (from repo root, with the Postgres server reachable):
    python scripts/migrate_sqlite_to_postgres.py \
        --source sqlite:///backend/job_matching.db \
        --target postgresql://jobmatching:jobmatching@localhost:5432/jobmatching

Copies every row from every table defined on the shared SQLAlchemy metadata,
preserving primary keys. Tables that already contain rows in the target are
skipped unless --force is given (in which case they are truncated first).
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from sqlalchemy import create_engine, select  # noqa: E402

from app.config.database import Base  # noqa: E402
import app.models.user  # noqa: F401,E402
import app.models.cv  # noqa: F401,E402
import app.models.job  # noqa: F401,E402
import app.models.skill  # noqa: F401,E402
import app.models.match  # noqa: F401,E402
import app.models.notification  # noqa: F401,E402
import app.models.collaboration  # noqa: F401,E402


def engine_for(url: str):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=f"sqlite:///{REPO_ROOT / 'backend' / 'job_matching.db'}")
    parser.add_argument("--target", required=True, help="Postgres DATABASE_URL")
    parser.add_argument("--force", action="store_true", help="truncate non-empty target tables")
    args = parser.parse_args()

    source = engine_for(args.source)
    target = engine_for(args.target)

    Base.metadata.create_all(bind=target)

    # sorted_tables respects FK dependencies (parents first)
    for table in Base.metadata.sorted_tables:
        with source.connect() as src:
            rows = [dict(r._mapping) for r in src.execute(select(table))]

        if not rows:
            print(f"{table.name}: 0 rows, nothing to copy")
            continue

        with target.begin() as tgt:
            existing = tgt.execute(table.select().limit(1)).first()
            if existing is not None:
                if not args.force:
                    print(f"{table.name}: target not empty, skipped (use --force to truncate)")
                    continue
                tgt.execute(table.delete())
            tgt.execute(table.insert(), rows)

        print(f"{table.name}: copied {len(rows)} rows")

    print("Migration complete. Verify with: SELECT count(*) FROM jobs; (psql)")


if __name__ == "__main__":
    main()
