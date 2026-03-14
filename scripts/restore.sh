#!/bin/bash
# Restore PostgreSQL database from backup file
# Usage: ./scripts/restore.sh backups/backup_20260314_120000.sql

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql>"
    echo "Example: $0 backups/backup_20260314_120000.sql"
    exit 1
fi

# Resolve path relative to where user ran the command
if [[ "$1" = /* ]]; then
    BACKUP_FILE="$1"
else
    BACKUP_FILE="$(pwd)/$1"
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "File not found: $BACKUP_FILE"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if db is running
if ! docker-compose ps db | grep -q "running"; then
    echo "DB is not running. Starting..."
    docker-compose up -d db
    echo "Waiting for DB to be ready..."
    sleep 5
fi

echo "Restoring from $BACKUP_FILE ..."
docker-compose exec -T db psql -U portfolio portfolio < "$BACKUP_FILE"
echo "Restore complete."
