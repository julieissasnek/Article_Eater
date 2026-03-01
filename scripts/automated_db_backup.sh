#!/bin/bash
# Article Eater Automated SQLite Backup
# Designed to be run daily via crontab
# Example: 0 2 * * * /path/to/automated_db_backup.sh

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$DIR")"
DB_PATH="${ROOT_DIR}/data/web_persistence.db"
BACKUP_DIR="${ROOT_DIR}/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

if [ -f "$DB_PATH" ]; then
    sqlite3 "$DB_PATH" ".backup '${BACKUP_DIR}/web_persistence_${DATE}.db'"
    # Optional: Rotate backups older than 7 days
    find "$BACKUP_DIR" -name "web_persistence_*.db" -type f -mtime +7 -delete
    echo "Backup completed successfully at $DATE"
else
    echo "Target DB $DB_PATH not found"
    exit 1
fi
