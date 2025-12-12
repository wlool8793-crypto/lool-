#!/bin/bash
# VNC Backup and Restore System
# Creates backups of VNC configuration and provides easy restore

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "VNC Backup & Restore System Setup"
echo "=========================================="
echo ""

BACKUP_DIR="/root/vnc-backups"
mkdir -p "$BACKUP_DIR"

# 1. Create backup script
echo "[1/4] Creating backup script..."
cat > /usr/local/bin/vnc-backup << 'EOF'
#!/bin/bash
# VNC Configuration Backup Script

BACKUP_DIR="/root/vnc-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vnc-backup-$TIMESTAMP.tar.gz"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================="
echo "VNC Configuration Backup"
echo "=============================="
echo ""

mkdir -p "$BACKUP_DIR"

echo "Creating backup..."
tar -czf "$BACKUP_FILE" \
    --ignore-failed-read \
    /home/dev/.vnc/ \
    /etc/systemd/system/vncserver@.service \
    /etc/systemd/system/novnc.service \
    /etc/systemd/system/novnc-secure.service \
    /etc/ssl/certs/vnc-selfsigned.crt \
    /etc/ssl/private/vnc-selfsigned.key \
    /root/VNC_INFO.txt \
    /root/SECURITY_INFO.txt \
    /root/MONITORING_INFO.txt \
    2>/dev/null || true

if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Backup created successfully${NC}"
    echo "  File: $BACKUP_FILE"
    echo "  Size: $SIZE"
    echo ""

    # Keep only last 10 backups
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/vnc-backup-*.tar.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        echo "Cleaning old backups (keeping last 10)..."
        ls -1t "$BACKUP_DIR"/vnc-backup-*.tar.gz | tail -n +11 | xargs rm -f
        echo -e "${GREEN}✓ Old backups cleaned${NC}"
    fi

    echo ""
    echo "Backup list:"
    ls -lh "$BACKUP_DIR"/vnc-backup-*.tar.gz 2>/dev/null | awk '{print "  "$9" ("$5")"}'
else
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi
EOF

chmod +x /usr/local/bin/vnc-backup
echo -e "${GREEN}✓ Backup script created: vnc-backup${NC}"

# 2. Create restore script
echo "[2/4] Creating restore script..."
cat > /usr/local/bin/vnc-restore << 'EOF'
#!/bin/bash
# VNC Configuration Restore Script

BACKUP_DIR="/root/vnc-backups"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================="
echo "VNC Configuration Restore"
echo "=============================="
echo ""

# List available backups
echo "Available backups:"
BACKUPS=($(ls -1t "$BACKUP_DIR"/vnc-backup-*.tar.gz 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo -e "${RED}No backups found in $BACKUP_DIR${NC}"
    exit 1
fi

for i in "${!BACKUPS[@]}"; do
    SIZE=$(du -h "${BACKUPS[$i]}" | cut -f1)
    DATE=$(echo "${BACKUPS[$i]}" | grep -oP '\d{8}_\d{6}')
    READABLE_DATE=$(date -d "${DATE:0:8} ${DATE:9:2}:${DATE:11:2}:${DATE:13:2}" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$DATE")
    echo "  [$i] $READABLE_DATE ($SIZE)"
done

echo ""
read -p "Enter backup number to restore (or 'q' to quit): " choice

if [ "$choice" = "q" ]; then
    echo "Cancelled"
    exit 0
fi

if [ "$choice" -ge 0 ] 2>/dev/null && [ "$choice" -lt ${#BACKUPS[@]} ]; then
    BACKUP_FILE="${BACKUPS[$choice]}"
    echo ""
    echo -e "${YELLOW}⚠ WARNING: This will overwrite current VNC configuration${NC}"
    read -p "Continue? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        echo ""
        echo "Stopping VNC services..."
        systemctl stop novnc novnc-secure vncserver@1 2>/dev/null || true
        sleep 2

        echo "Restoring from: $BACKUP_FILE"
        tar -xzf "$BACKUP_FILE" -C / 2>/dev/null

        echo "Restarting VNC services..."
        systemctl daemon-reload
        systemctl start vncserver@1
        systemctl start novnc-secure 2>/dev/null || systemctl start novnc

        echo ""
        echo -e "${GREEN}✓ Restore completed successfully${NC}"
        echo ""
        echo "Verify with: vnc-status"
    else
        echo "Cancelled"
    fi
else
    echo -e "${RED}Invalid selection${NC}"
    exit 1
fi
EOF

chmod +x /usr/local/bin/vnc-restore
echo -e "${GREEN}✓ Restore script created: vnc-restore${NC}"

# 3. Create automated backup timer
echo "[3/4] Setting up automated daily backups..."
cat > /etc/systemd/system/vnc-backup.service << 'EOF'
[Unit]
Description=VNC Configuration Backup
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/vnc-backup
StandardOutput=journal
StandardError=journal
EOF

cat > /etc/systemd/system/vnc-backup.timer << 'EOF'
[Unit]
Description=Daily VNC Backup
Requires=vnc-backup.service

[Timer]
OnCalendar=daily
OnBootSec=10min
Persistent=true
Unit=vnc-backup.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable vnc-backup.timer
systemctl start vnc-backup.timer
echo -e "${GREEN}✓ Automated daily backups enabled${NC}"

# 4. Create configuration export script
echo "[4/4] Creating configuration export tool..."
cat > /usr/local/bin/vnc-export-config << 'EOF'
#!/bin/bash
# Export VNC configuration as human-readable text

GREEN='\033[0;32m'
NC='\033[0m'

OUTPUT_FILE="/root/vnc-config-export.txt"

cat > "$OUTPUT_FILE" << 'EXPORT_EOF'
╔═══════════════════════════════════════════════════════════════════╗
║              VNC CONFIGURATION EXPORT                             ║
╚═══════════════════════════════════════════════════════════════════╝

Export Date: $(date)
Hostname: $(hostname)
IP Address: 152.42.229.221

════════════════════════════════════════════════════════════════════
VNC CONFIGURATION (/home/dev/.vnc/config)
════════════════════════════════════════════════════════════════════
EXPORT_EOF

cat /home/dev/.vnc/config >> "$OUTPUT_FILE" 2>/dev/null || echo "Not found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

════════════════════════════════════════════════════════════════════
VNC XSTARTUP (/home/dev/.vnc/xstartup)
════════════════════════════════════════════════════════════════════
EXPORT_EOF

cat /home/dev/.vnc/xstartup >> "$OUTPUT_FILE" 2>/dev/null || echo "Not found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

════════════════════════════════════════════════════════════════════
SYSTEMD SERVICES
════════════════════════════════════════════════════════════════════

--- vncserver@.service ---
EXPORT_EOF

cat /etc/systemd/system/vncserver@.service >> "$OUTPUT_FILE" 2>/dev/null || echo "Not found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

--- novnc.service ---
EXPORT_EOF

cat /etc/systemd/system/novnc.service >> "$OUTPUT_FILE" 2>/dev/null || echo "Not found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

--- novnc-secure.service ---
EXPORT_EOF

cat /etc/systemd/system/novnc-secure.service >> "$OUTPUT_FILE" 2>/dev/null || echo "Not found" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

════════════════════════════════════════════════════════════════════
FIREWALL RULES (UFW)
════════════════════════════════════════════════════════════════════
EXPORT_EOF

ufw status numbered >> "$OUTPUT_FILE" 2>/dev/null || echo "UFW not configured" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

════════════════════════════════════════════════════════════════════
RUNNING PROCESSES
════════════════════════════════════════════════════════════════════
EXPORT_EOF

ps aux | grep -E "Xtigervnc|websockify" | grep -v grep >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << 'EXPORT_EOF'

════════════════════════════════════════════════════════════════════
NETWORK PORTS
════════════════════════════════════════════════════════════════════
EXPORT_EOF

netstat -tlnp 2>/dev/null | grep -E ":(5901|6080)" >> "$OUTPUT_FILE"

echo -e "${GREEN}✓ Configuration exported to: $OUTPUT_FILE${NC}"
echo ""
echo "View with: cat $OUTPUT_FILE"
EOF

chmod +x /usr/local/bin/vnc-export-config
echo -e "${GREEN}✓ Export tool created: vnc-export-config${NC}"

# Create initial backup
echo ""
echo "Creating initial backup..."
/usr/local/bin/vnc-backup

# Create backup info file
cat > /root/BACKUP_INFO.txt << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                VNC BACKUP & RESTORE SYSTEM                        ║
╚═══════════════════════════════════════════════════════════════════╝

BACKUP COMMANDS:
  vnc-backup           - Create backup now
  vnc-restore          - Restore from backup (interactive)
  vnc-export-config    - Export config as text

AUTOMATED BACKUPS:
  - Runs daily automatically
  - Keeps last 10 backups
  - Location: /root/vnc-backups/

BACKUP CONTENTS:
  - VNC configuration (/home/dev/.vnc/)
  - Systemd services
  - SSL certificates
  - Documentation files

VIEW BACKUPS:
  ls -lh /root/vnc-backups/

MANUAL BACKUP SCHEDULE:
  Check: systemctl status vnc-backup.timer
  Disable: systemctl stop vnc-backup.timer
  Enable: systemctl start vnc-backup.timer

RESTORE PROCESS:
  1. Run: vnc-restore
  2. Select backup from list
  3. Confirm restoration
  4. Services auto-restart

EXPORT CONFIGURATION:
  vnc-export-config
  Output: /root/vnc-config-export.txt

DISASTER RECOVERY:
  If VNC completely broken:
    1. Run: vnc-restore
    2. Select most recent backup
    3. Services will restart automatically
EOF

echo ""
echo "=========================================="
echo "Backup System Setup Complete!"
echo "=========================================="
echo ""
echo "Features enabled:"
echo "  ✓ Manual backup: vnc-backup"
echo "  ✓ Restore: vnc-restore"
echo "  ✓ Daily automated backups"
echo "  ✓ Config export: vnc-export-config"
echo "  ✓ Keeps last 10 backups"
echo ""
echo "Backups location: /root/vnc-backups/"
echo "See /root/BACKUP_INFO.txt for details"
echo ""
