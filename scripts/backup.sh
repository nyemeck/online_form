#!/bin/bash
# ============================================
# Database backup script
# Run daily via cron: 0 3 * * * /srv/online_form/scripts/backup.sh
# ============================================

BACKUP_DIR=/srv/online_form/backups
DB_FILE=/srv/online_form/backend/responses.db
DATE=$(date +%Y%m%d_%H%M%S)
KEEP=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "ERROR: Database file not found: $DB_FILE"
    exit 1
fi

# Copy database
cp "$DB_FILE" "$BACKUP_DIR/responses_$DATE.db"

if [ $? -eq 0 ]; then
    echo "OK: Backup created: responses_$DATE.db"
else
    echo "ERROR: Backup failed"
    exit 1
fi

# Remove old backups (keep last N)
ls -t "$BACKUP_DIR"/responses_*.db 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm

echo "OK: Backups retained: $(ls "$BACKUP_DIR"/responses_*.db 2>/dev/null | wc -l)/$KEEP"

# Disk space check
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | awk '{print $1}')
DB_SIZE=$(du -sh "$DB_FILE" 2>/dev/null | awk '{print $1}')
echo "INFO: Disk usage: ${DISK_USAGE}% | DB size: $DB_SIZE | Backups total: $BACKUP_SIZE"

if [ "$DISK_USAGE" -ge 80 ]; then
    echo "WARNING: Disk usage is at ${DISK_USAGE}% — consider freeing up space"
fi
if [ "$DISK_USAGE" -ge 90 ]; then
    echo "CRITICAL: Disk usage is at ${DISK_USAGE}% — immediate action required"
fi
