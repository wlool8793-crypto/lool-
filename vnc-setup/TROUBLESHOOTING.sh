#!/bin/bash
# VNC Troubleshooting Script
# Attempts to diagnose and fix common VNC issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════╗
║     VNC TROUBLESHOOTING & REPAIR              ║
╚═══════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

# Function to fix issues
fix_issue() {
    echo -e "${YELLOW}Attempting to fix: $1${NC}"
    eval "$2"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fixed${NC}"
    else
        echo -e "${RED}✗ Failed to fix${NC}"
    fi
    echo ""
}

# Check what's wrong
echo "Diagnosing issues..."
echo ""

# Issue 1: VNC not running
if ! pgrep -u dev Xtigervnc > /dev/null; then
    echo -e "${RED}✗ VNC server not running${NC}"
    fix_issue "VNC server not running" "sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24"
else
    echo -e "${GREEN}✓ VNC server running${NC}"
fi

# Issue 2: noVNC not running
if ! pgrep websockify > /dev/null; then
    echo -e "${RED}✗ noVNC not running${NC}"
    fix_issue "noVNC not running" "websockify -D --web=/usr/share/novnc/ 6080 localhost:5901"
else
    echo -e "${GREEN}✓ noVNC running${NC}"
fi

# Issue 3: VNC running as root instead of dev
if pgrep -u root Xtigervnc > /dev/null; then
    echo -e "${YELLOW}⚠ VNC running as root (should be dev)${NC}"
    fix_issue "Kill root VNC and start as dev" "vncserver -kill :1 && sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24"
fi

# Issue 4: Firewall blocking ports
if command -v ufw &>/dev/null && ufw status | grep -q "Status: active"; then
    if ! ufw status | grep -q "5901"; then
        echo -e "${YELLOW}⚠ Firewall may be blocking port 5901${NC}"
        fix_issue "Allow port 5901" "ufw allow 5901"
    fi
    if ! ufw status | grep -q "6080"; then
        echo -e "${YELLOW}⚠ Firewall may be blocking port 6080${NC}"
        fix_issue "Allow port 6080" "ufw allow 6080"
    fi
fi

# Issue 5: xstartup not configured for XFCE
if [ -f /home/dev/.vnc/xstartup ]; then
    if ! grep -q "startxfce4" /home/dev/.vnc/xstartup; then
        echo -e "${YELLOW}⚠ xstartup not configured for XFCE${NC}"
        fix_issue "Reconfigure xstartup" "sudo -u dev bash /root/vnc-setup/02_configure_vnc_dev_user.sh"
    else
        echo -e "${GREEN}✓ xstartup configured for XFCE${NC}"
    fi
else
    echo -e "${RED}✗ xstartup file missing${NC}"
    fix_issue "Create xstartup" "sudo -u dev bash /root/vnc-setup/02_configure_vnc_dev_user.sh"
fi

# Issue 6: Services not enabled
if ! systemctl is-enabled vncserver@1 &>/dev/null; then
    echo -e "${YELLOW}⚠ VNC service not enabled for autostart${NC}"
    fix_issue "Enable VNC service" "systemctl enable vncserver@1"
fi

if ! systemctl is-enabled novnc &>/dev/null; then
    echo -e "${YELLOW}⚠ noVNC service not enabled for autostart${NC}"
    fix_issue "Enable noVNC service" "systemctl enable novnc"
fi

# Complete restart
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Performing complete restart...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Stop everything
echo "Stopping all services..."
systemctl stop novnc 2>/dev/null || true
systemctl stop vncserver@1 2>/dev/null || true
pkill -9 websockify 2>/dev/null || true
sudo -u dev vncserver -kill :1 2>/dev/null || true

sleep 3

# Start everything
echo "Starting VNC server..."
sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24

sleep 3

echo "Starting noVNC..."
websockify -D --web=/usr/share/novnc/ 6080 localhost:5901

sleep 3

# Verify
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Final Status Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if pgrep -u dev Xtigervnc > /dev/null; then
    echo -e "${GREEN}✓ VNC server running as dev${NC}"
else
    echo -e "${RED}✗ VNC server NOT running${NC}"
fi

if pgrep websockify > /dev/null; then
    echo -e "${GREEN}✓ noVNC running${NC}"
else
    echo -e "${RED}✗ noVNC NOT running${NC}"
fi

if netstat -tlnp 2>/dev/null | grep -q ":5901"; then
    echo -e "${GREEN}✓ VNC port 5901 listening${NC}"
else
    echo -e "${RED}✗ VNC port 5901 NOT listening${NC}"
fi

if netstat -tlnp 2>/dev/null | grep -q ":6080"; then
    echo -e "${GREEN}✓ noVNC port 6080 listening${NC}"
else
    echo -e "${RED}✗ noVNC port 6080 NOT listening${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Try accessing: http://152.42.229.221:6080/vnc.html"
echo ""
echo "If still not working, check logs:"
echo "  - VNC log: tail -f /home/dev/.vnc/*.log"
echo "  - noVNC log: journalctl -u novnc -n 50"
echo "  - VNC service: journalctl -u vncserver@1 -n 50"
echo ""
