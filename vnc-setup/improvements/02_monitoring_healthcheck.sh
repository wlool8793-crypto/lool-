#!/bin/bash
# VNC Monitoring and Health Check System
# Automatically monitors and restarts VNC/noVNC if they fail

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "VNC Monitoring & Health Check Setup"
echo "=========================================="
echo ""

# 1. Create health check script
echo "[1/5] Creating health check script..."
cat > /usr/local/bin/vnc-health-check << 'EOF'
#!/bin/bash
# VNC Health Check Script
# Checks if VNC and noVNC are running, restarts if needed

LOG_FILE="/var/log/vnc-health-check.log"
MAX_LOG_SIZE=10485760  # 10MB

# Rotate log if too large
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null) -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_vnc() {
    if pgrep -u dev Xtigervnc >/dev/null; then
        return 0
    else
        return 1
    fi
}

check_novnc() {
    if pgrep websockify >/dev/null; then
        return 0
    else
        return 1
    fi
}

check_vnc_port() {
    if netstat -tln 2>/dev/null | grep -q ":5901"; then
        return 0
    else
        return 1
    fi
}

check_novnc_port() {
    if netstat -tln 2>/dev/null | grep -q ":6080"; then
        return 0
    else
        return 1
    fi
}

# Check VNC
if ! check_vnc || ! check_vnc_port; then
    log "⚠ VNC server not running or port not listening - attempting restart"
    systemctl restart vncserver@1 2>&1 | tee -a "$LOG_FILE"
    sleep 5
    if check_vnc && check_vnc_port; then
        log "✓ VNC server restarted successfully"
    else
        log "✗ VNC server restart failed - manual intervention required"
        exit 1
    fi
else
    log "✓ VNC server healthy"
fi

# Check noVNC
if ! check_novnc || ! check_novnc_port; then
    log "⚠ noVNC not running or port not listening - attempting restart"
    # Try secure service first, fallback to regular
    systemctl restart novnc-secure 2>&1 | tee -a "$LOG_FILE" || systemctl restart novnc 2>&1 | tee -a "$LOG_FILE"
    sleep 3
    if check_novnc && check_novnc_port; then
        log "✓ noVNC restarted successfully"
    else
        log "✗ noVNC restart failed - manual intervention required"
        exit 1
    fi
else
    log "✓ noVNC healthy"
fi

# Check system resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

log "System: CPU=${CPU_USAGE}% MEM=${MEM_USAGE}% DISK=${DISK_USAGE}%"

# Alert if resources high
if (( $(echo "$CPU_USAGE > 90" | bc -l) )); then
    log "⚠ WARNING: High CPU usage: ${CPU_USAGE}%"
fi

if [ "$MEM_USAGE" -gt 90 ]; then
    log "⚠ WARNING: High memory usage: ${MEM_USAGE}%"
fi

if [ "$DISK_USAGE" -gt 90 ]; then
    log "⚠ WARNING: High disk usage: ${DISK_USAGE}%"
fi

log "Health check completed successfully"
EOF

chmod +x /usr/local/bin/vnc-health-check
echo -e "${GREEN}✓ Health check script created${NC}"

# 2. Create systemd timer for health checks
echo "[2/5] Setting up automated health checks (every 5 minutes)..."
cat > /etc/systemd/system/vnc-health-check.service << 'EOF'
[Unit]
Description=VNC Health Check
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/vnc-health-check
StandardOutput=journal
StandardError=journal
EOF

cat > /etc/systemd/system/vnc-health-check.timer << 'EOF'
[Unit]
Description=Run VNC Health Check every 5 minutes
Requires=vnc-health-check.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=vnc-health-check.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable vnc-health-check.timer
systemctl start vnc-health-check.timer
echo -e "${GREEN}✓ Health check timer enabled (runs every 5 minutes)${NC}"

# 3. Create status dashboard script
echo "[3/5] Creating status dashboard..."
cat > /usr/local/bin/vnc-status << 'EOF'
#!/bin/bash
# VNC Status Dashboard

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              VNC STATUS DASHBOARD                                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# VNC Server Status
echo -e "${YELLOW}VNC SERVER:${NC}"
if pgrep -u dev Xtigervnc >/dev/null; then
    echo -e "  Status: ${GREEN}✓ Running${NC}"
    VNC_PID=$(pgrep -u dev Xtigervnc)
    echo "  PID: $VNC_PID"
    echo "  User: dev"
    if netstat -tln 2>/dev/null | grep -q ":5901"; then
        echo -e "  Port 5901: ${GREEN}✓ Listening${NC}"
    else
        echo -e "  Port 5901: ${RED}✗ Not listening${NC}"
    fi
else
    echo -e "  Status: ${RED}✗ Not running${NC}"
fi
echo ""

# noVNC Status
echo -e "${YELLOW}noVNC WEB INTERFACE:${NC}"
if pgrep websockify >/dev/null; then
    echo -e "  Status: ${GREEN}✓ Running${NC}"
    NOVNC_PID=$(pgrep websockify)
    echo "  PID: $NOVNC_PID"
    if netstat -tln 2>/dev/null | grep -q ":6080"; then
        echo -e "  Port 6080: ${GREEN}✓ Listening${NC}"
    else
        echo -e "  Port 6080: ${RED}✗ Not listening${NC}"
    fi
else
    echo -e "  Status: ${RED}✗ Not running${NC}"
fi
echo ""

# Systemd Services
echo -e "${YELLOW}SYSTEMD SERVICES:${NC}"
VNC_SVC=$(systemctl is-active vncserver@1 2>/dev/null || echo "inactive")
NOVNC_SVC=$(systemctl is-active novnc 2>/dev/null || echo "inactive")
NOVNC_SEC_SVC=$(systemctl is-active novnc-secure 2>/dev/null || echo "inactive")

if [ "$VNC_SVC" = "active" ]; then
    echo -e "  vncserver@1: ${GREEN}✓ Active${NC}"
else
    echo -e "  vncserver@1: ${RED}✗ $VNC_SVC${NC}"
fi

if [ "$NOVNC_SVC" = "active" ]; then
    echo -e "  novnc: ${GREEN}✓ Active${NC}"
elif [ "$NOVNC_SEC_SVC" = "active" ]; then
    echo -e "  novnc-secure: ${GREEN}✓ Active (HTTPS)${NC}"
else
    echo -e "  novnc: ${RED}✗ $NOVNC_SVC${NC}"
fi
echo ""

# System Resources
echo -e "${YELLOW}SYSTEM RESOURCES:${NC}"
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_TOTAL=$(free -h | awk 'NR==2 {print $2}')
MEM_USED=$(free -h | awk 'NR==2 {print $3}')
MEM_PERCENT=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
UPTIME=$(uptime -p)

echo "  CPU Usage: ${CPU_USAGE}%"
echo "  Memory: ${MEM_USED} / ${MEM_TOTAL} (${MEM_PERCENT}%)"
echo "  Disk Usage: ${DISK_USAGE}"
echo "  Uptime: ${UPTIME}"
echo ""

# Network Info
echo -e "${YELLOW}NETWORK:${NC}"
echo "  Server IP: 152.42.229.221"
echo "  HTTP Access: http://152.42.229.221:6080/vnc.html"
echo "  HTTPS Access: https://152.42.229.221:6080/vnc.html"
echo ""

# Recent Health Checks
echo -e "${YELLOW}RECENT HEALTH CHECKS:${NC}"
if [ -f /var/log/vnc-health-check.log ]; then
    tail -5 /var/log/vnc-health-check.log
else
    echo "  No health check logs found"
fi
echo ""

# Quick Actions
echo -e "${YELLOW}QUICK ACTIONS:${NC}"
echo "  Restart VNC: systemctl restart vncserver@1"
echo "  Restart noVNC: systemctl restart novnc"
echo "  View logs: journalctl -u vncserver@1 -n 50"
echo "  Health check: vnc-health-check"
echo ""
EOF

chmod +x /usr/local/bin/vnc-status
echo -e "${GREEN}✓ Status dashboard created: vnc-status${NC}"

# 4. Create log rotation configuration
echo "[4/5] Configuring log rotation..."
cat > /etc/logrotate.d/vnc << 'EOF'
/var/log/vnc-health-check.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 root root
}

/home/dev/.vnc/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
    su dev dev
}
EOF
echo -e "${GREEN}✓ Log rotation configured${NC}"

# 5. Create alerting script (can be extended with email/SMS)
echo "[5/5] Creating alert system..."
cat > /usr/local/bin/vnc-alert << 'EOF'
#!/bin/bash
# VNC Alert System
# Can be extended to send emails or SMS

ALERT_LOG="/var/log/vnc-alerts.log"

send_alert() {
    local severity=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$severity] $message" >> "$ALERT_LOG"

    # Add email notification here if needed
    # echo "$message" | mail -s "VNC Alert: $severity" your@email.com

    # Or webhook notification
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"VNC Alert: $message\"}" \
    #   YOUR_WEBHOOK_URL
}

# Example: vnc-alert CRITICAL "VNC server down"
send_alert "$1" "$2"
EOF

chmod +x /usr/local/bin/vnc-alert
echo -e "${GREEN}✓ Alert system created${NC}"

# Create monitoring info file
cat > /root/MONITORING_INFO.txt << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                 VNC MONITORING SYSTEM                             ║
╚═══════════════════════════════════════════════════════════════════╝

AUTOMATED HEALTH CHECKS:
  - Runs every 5 minutes automatically
  - Checks VNC and noVNC processes
  - Checks ports 5901 and 6080
  - Auto-restarts services if down
  - Monitors system resources

COMMANDS:
  vnc-status         - View full status dashboard
  vnc-health-check   - Run health check manually
  vnc-alert LEVEL MSG - Send alert (for custom monitoring)

LOGS:
  Health checks: /var/log/vnc-health-check.log
  Alerts: /var/log/vnc-alerts.log
  VNC logs: /home/dev/.vnc/*.log

VIEW LOGS:
  tail -f /var/log/vnc-health-check.log
  journalctl -u vnc-health-check.service -f
  journalctl -u vncserver@1 -f

TIMER STATUS:
  systemctl status vnc-health-check.timer
  systemctl list-timers vnc-health-check.timer

DISABLE/ENABLE MONITORING:
  systemctl stop vnc-health-check.timer    (disable)
  systemctl start vnc-health-check.timer   (enable)

LOG ROTATION:
  - Health check logs: Daily, keep 7 days
  - VNC logs: Weekly, keep 4 weeks
  - Logs automatically compressed

EXTENDING ALERTS:
  Edit /usr/local/bin/vnc-alert to add:
  - Email notifications
  - SMS alerts
  - Webhook notifications (Slack, Discord, etc.)
EOF

echo ""
echo "=========================================="
echo "Monitoring System Setup Complete!"
echo "=========================================="
echo ""
echo "Features enabled:"
echo "  ✓ Health checks every 5 minutes"
echo "  ✓ Auto-restart on failure"
echo "  ✓ Status dashboard (vnc-status)"
echo "  ✓ Log rotation"
echo "  ✓ Resource monitoring"
echo ""
echo "Try it now:"
echo "  vnc-status           - View dashboard"
echo "  vnc-health-check     - Run health check"
echo ""
echo "See /root/MONITORING_INFO.txt for details"
echo ""
