#!/bin/bash
# Backup PostgreSQL database

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Check if db is running
if ! docker-compose ps db | grep -q "running"; then
    echo "DB is not running. Starting..."
    docker-compose up -d db
    echo "Waiting for DB to be ready..."
    sleep 5
fi

echo "Backing up database..."
docker-compose exec -T db pg_dump -U portfolio portfolio > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "Saved to $BACKUP_DIR/backup_$TIMESTAMP.sql"
