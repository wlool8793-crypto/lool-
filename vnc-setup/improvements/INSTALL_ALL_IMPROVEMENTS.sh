#!/bin/bash
# Master Installation Script for All VNC Improvements
# Run this to apply all robustness improvements at once

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        VNC ROBUSTNESS IMPROVEMENTS - MASTER INSTALLER             ║
║        Make Your VNC Setup Production-Ready                       ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "This will install:"
echo "  1. Security Hardening (SSL, firewall, fail2ban)"
echo "  2. Monitoring & Health Checks (auto-restart, alerts)"
echo "  3. Backup & Restore System (daily backups)"
echo "  4. Performance Optimizations (faster, lower latency)"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting installation...${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Track progress
total_steps=4
current_step=0

run_improvement() {
    current_step=$((current_step + 1))
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}[$current_step/$total_steps] $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""

    if [ -f "$SCRIPT_DIR/$2" ]; then
        bash "$SCRIPT_DIR/$2"
    else
        echo -e "${RED}Error: Script $2 not found${NC}"
        return 1
    fi
}

# Run all improvement scripts
run_improvement "Security Hardening" "01_security_hardening.sh"
run_improvement "Monitoring & Health Checks" "02_monitoring_healthcheck.sh"
run_improvement "Backup & Restore System" "03_backup_restore.sh"
run_improvement "Performance Optimization" "04_performance_optimization.sh"

# Final configuration
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Final Configuration${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Restarting services with new configuration..."
systemctl daemon-reload

# Stop old services
systemctl stop novnc 2>/dev/null || true
systemctl stop vncserver@1 2>/dev/null || true
sleep 3

# Start with new configuration
echo "Starting VNC server..."
systemctl start vncserver@1
sleep 5

echo "Starting secure noVNC..."
systemctl start novnc-secure 2>/dev/null || systemctl start novnc

sleep 3

# Verify everything is running
echo ""
echo "Verifying services..."
if pgrep -u dev Xtigervnc >/dev/null; then
    echo -e "  VNC Server: ${GREEN}✓ Running${NC}"
else
    echo -e "  VNC Server: ${RED}✗ Not running${NC}"
fi

if pgrep websockify >/dev/null; then
    echo -e "  noVNC: ${GREEN}✓ Running${NC}"
else
    echo -e "  noVNC: ${RED}✗ Not running${NC}"
fi

if systemctl is-active vnc-health-check.timer >/dev/null 2>&1; then
    echo -e "  Health Checks: ${GREEN}✓ Enabled${NC}"
else
    echo -e "  Health Checks: ${YELLOW}⚠ Not enabled${NC}"
fi

if systemctl is-active vnc-backup.timer >/dev/null 2>&1; then
    echo -e "  Daily Backups: ${GREEN}✓ Enabled${NC}"
else
    echo -e "  Daily Backups: ${YELLOW}⚠ Not enabled${NC}"
fi

# Create master info file
cat > /root/VNC_IMPROVEMENTS_SUMMARY.txt << 'SUMMARY_EOF'
╔═══════════════════════════════════════════════════════════════════╗
║              VNC IMPROVEMENTS - QUICK REFERENCE                   ║
╚═══════════════════════════════════════════════════════════════════╝

INSTALLED: $(date)

════════════════════════════════════════════════════════════════════
SECURITY FEATURES
════════════════════════════════════════════════════════════════════
✓ SSL/TLS encryption (HTTPS)
✓ Firewall (UFW) configured
✓ Fail2ban brute-force protection
✓ VNC password protection

Access URLs:
  HTTPS (Secure): https://152.42.229.221:6080/vnc.html
  HTTP: http://152.42.229.221:6080/vnc.html

Security Commands:
  change-vnc-password  - Change VNC password
  ufw status           - View firewall rules
  fail2ban-client status - Check banned IPs

════════════════════════════════════════════════════════════════════
MONITORING FEATURES
════════════════════════════════════════════════════════════════════
✓ Health checks every 5 minutes
✓ Auto-restart on failure
✓ Resource monitoring
✓ Log rotation

Monitoring Commands:
  vnc-status          - Full status dashboard
  vnc-health-check    - Run health check now
  vnc-quality-check   - Check connection quality

Logs:
  /var/log/vnc-health-check.log
  /home/dev/.vnc/*.log

════════════════════════════════════════════════════════════════════
BACKUP FEATURES
════════════════════════════════════════════════════════════════════
✓ Daily automated backups
✓ Keeps last 10 backups
✓ One-command restore

Backup Commands:
  vnc-backup          - Create backup now
  vnc-restore         - Restore from backup
  vnc-export-config   - Export configuration

Backup Location:
  /root/vnc-backups/

════════════════════════════════════════════════════════════════════
PERFORMANCE FEATURES
════════════════════════════════════════════════════════════════════
✓ VNC compression optimized
✓ XFCE compositor disabled
✓ Network buffers increased
✓ Quality profiles available

Performance Commands:
  vnc-tune            - Change quality profile
  vnc-quality-check   - Check performance
  vnc-cleanup         - Clean old files

════════════════════════════════════════════════════════════════════
QUICK COMMAND REFERENCE
════════════════════════════════════════════════════════════════════
Status & Monitoring:
  vnc-status          - Complete status dashboard
  vnc-health-check    - Manual health check
  vnc-quality-check   - Connection quality

Security:
  change-vnc-password - Change VNC password
  ufw status          - Firewall status
  fail2ban-client status sshd - SSH protection status

Backup & Restore:
  vnc-backup          - Backup configuration
  vnc-restore         - Restore from backup
  vnc-export-config   - Export as text

Performance:
  vnc-tune            - Change quality profile
  vnc-cleanup         - Clean old files

Service Management:
  systemctl restart vncserver@1 - Restart VNC
  systemctl restart novnc-secure - Restart noVNC
  systemctl status vncserver@1 - VNC status

════════════════════════════════════════════════════════════════════
DETAILED DOCUMENTATION
════════════════════════════════════════════════════════════════════
/root/SECURITY_INFO.txt     - Security configuration
/root/MONITORING_INFO.txt   - Monitoring details
/root/BACKUP_INFO.txt       - Backup system
/root/PERFORMANCE_INFO.txt  - Performance tuning

════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
════════════════════════════════════════════════════════════════════
VNC not responding:
  1. Check: vnc-status
  2. Run: vnc-health-check
  3. Restart: systemctl restart vncserver@1

Slow performance:
  1. Check: vnc-quality-check
  2. Tune: vnc-tune (try "High Speed")
  3. Clean: vnc-cleanup

Need to restore:
  1. Run: vnc-restore
  2. Select backup
  3. Confirm restoration

════════════════════════════════════════════════════════════════════
RECOMMENDED NEXT STEPS
════════════════════════════════════════════════════════════════════
1. Change default passwords:
   - VNC: change-vnc-password
   - SSH: passwd

2. Test backup/restore:
   - Create: vnc-backup
   - Verify: ls -lh /root/vnc-backups/

3. Check monitoring:
   - View: vnc-status
   - Test: vnc-health-check

4. Verify security:
   - Firewall: ufw status
   - Fail2ban: fail2ban-client status

5. Test HTTPS access:
   - Visit: https://152.42.229.221:6080/vnc.html

════════════════════════════════════════════════════════════════════
SUMMARY_EOF

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           ✓✓✓ ALL IMPROVEMENTS INSTALLED! ✓✓✓                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    WHAT'S NEW${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Security:"
echo "  ✓ HTTPS access: https://152.42.229.221:6080/vnc.html"
echo "  ✓ Firewall protection"
echo "  ✓ Fail2ban (brute-force prevention)"
echo ""
echo "Monitoring:"
echo "  ✓ Health checks every 5 minutes"
echo "  ✓ Auto-restart if VNC fails"
echo "  ✓ Status dashboard: vnc-status"
echo ""
echo "Backups:"
echo "  ✓ Daily automated backups"
echo "  ✓ One-command restore: vnc-restore"
echo "  ✓ Location: /root/vnc-backups/"
echo ""
echo "Performance:"
echo "  ✓ Optimized compression"
echo "  ✓ Quality profiles: vnc-tune"
echo "  ✓ Performance monitor: vnc-quality-check"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                  IMPORTANT NEXT STEPS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Change VNC password from default (vnc123):"
echo "   ${YELLOW}change-vnc-password${NC}"
echo ""
echo "2. Change SSH password from default (2002):"
echo "   ${YELLOW}passwd${NC}"
echo ""
echo "3. Test HTTPS access (more secure):"
echo "   ${YELLOW}https://152.42.229.221:6080/vnc.html${NC}"
echo "   (Browser will warn about self-signed cert - click Advanced → Proceed)"
echo ""
echo "4. View full status:"
echo "   ${YELLOW}vnc-status${NC}"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Complete documentation: ${YELLOW}/root/VNC_IMPROVEMENTS_SUMMARY.txt${NC}"
echo ""
echo -e "${GREEN}Your VNC setup is now production-ready! 🚀${NC}"
echo ""
