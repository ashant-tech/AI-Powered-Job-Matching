#!/usr/bin/env bash
# Database backup with retention.
#   Postgres (docker):  ./scripts/backup_db.sh            (uses the `db` compose service)
#   SQLite (local dev): ./scripts/backup_db.sh --sqlite
# Cron example (daily 02:30, keep 14 days):
#   30 2 * * * cd /path/to/job-matching && ./scripts/backup_db.sh >> backups/backup.log 2>&1
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$REPO_ROOT/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

if [[ "${1:-}" == "--sqlite" ]]; then
    SRC="$REPO_ROOT/backend/job_matching.db"
    OUT="$BACKUP_DIR/job_matching_sqlite_$TIMESTAMP.db"
    sqlite3 "$SRC" ".backup '$OUT'"
    echo "SQLite backup written to $OUT"
else
    OUT="$BACKUP_DIR/jobmatching_pg_$TIMESTAMP.sql.gz"
    docker compose -f "$REPO_ROOT/docker-compose.yml" exec -T db \
        pg_dump -U jobmatching jobmatching | gzip > "$OUT"
    echo "Postgres backup written to $OUT"
fi

# Prune backups older than RETENTION_DAYS
find "$BACKUP_DIR" -type f \( -name "jobmatching_pg_*.sql.gz" -o -name "job_matching_sqlite_*.db" \) \
    -mtime +"$RETENTION_DAYS" -delete

echo "Retention: removed backups older than $RETENTION_DAYS days"
