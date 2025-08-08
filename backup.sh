#!/bin/bash

# LinkedIn Content Generation System Backup Script
# This script creates backups of configuration and data files

set -e  # Exit on any error

# Configuration
BACKUP_DIR="/backup/linkedin-agent"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="linkedin-agent-backup-$DATE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
   exit 1
fi

# Create backup directory
log "Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# Create temporary backup directory
TEMP_BACKUP_DIR="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$TEMP_BACKUP_DIR"

log "Starting backup of LinkedIn Content Generation System..."

# Backup configuration files
log "Backing up configuration files..."
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$TEMP_BACKUP_DIR/.env"
    log "✓ Environment file backed up"
else
    warning "No .env file found"
fi

# Backup data directory
log "Backing up data files..."
if [ -d "$PROJECT_DIR/data" ]; then
    cp -r "$PROJECT_DIR/data" "$TEMP_BACKUP_DIR/"
    log "✓ Data directory backed up"
else
    warning "No data directory found"
fi

# Backup logs (if they exist)
log "Backing up log files..."
if [ -d "/var/log" ]; then
    if [ -f "/var/log/linkedin-agent.out.log" ]; then
        cp "/var/log/linkedin-agent.out.log" "$TEMP_BACKUP_DIR/"
        log "✓ Output log backed up"
    fi
    if [ -f "/var/log/linkedin-agent.err.log" ]; then
        cp "/var/log/linkedin-agent.err.log" "$TEMP_BACKUP_DIR/"
        log "✓ Error log backed up"
    fi
fi

# Backup supervisor configuration
log "Backing up supervisor configuration..."
if [ -f "/etc/supervisor/conf.d/linkedin-agent.conf" ]; then
    cp "/etc/supervisor/conf.d/linkedin-agent.conf" "$TEMP_BACKUP_DIR/"
    log "✓ Supervisor config backed up"
fi

# Create backup manifest
log "Creating backup manifest..."
cat > "$TEMP_BACKUP_DIR/backup-manifest.txt" << EOF
LinkedIn Content Generation System Backup
========================================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
Project Directory: $PROJECT_DIR

Files Backed Up:
$(find "$TEMP_BACKUP_DIR" -type f -name "*.env" -o -name "*.log" -o -name "*.conf" | sort)

Directories Backed Up:
$(find "$TEMP_BACKUP_DIR" -type d | sort)

System Information:
$(uname -a)

Disk Usage:
$(df -h "$BACKUP_DIR")
EOF

# Compress backup
log "Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
BACKUP_SIZE=$(du -h "$BACKUP_NAME.tar.gz" | cut -f1)

# Remove temporary directory
rm -rf "$TEMP_BACKUP_DIR"

# Clean old backups (keep last 7 days)
log "Cleaning old backups..."
find "$BACKUP_DIR" -name "linkedin-agent-backup-*.tar.gz" -mtime +7 -delete

# List remaining backups
log "Remaining backups:"
ls -lh "$BACKUP_DIR"/linkedin-agent-backup-*.tar.gz 2>/dev/null || warning "No backup files found"

log "Backup completed successfully!"
log "Backup file: $BACKUP_NAME.tar.gz"
log "Backup size: $BACKUP_SIZE"
log "Backup location: $BACKUP_DIR"

# Optional: Send notification
if command -v mail &> /dev/null; then
    echo "LinkedIn Agent backup completed successfully at $(date). Backup size: $BACKUP_SIZE" | mail -s "LinkedIn Agent Backup Complete" root
fi

exit 0 