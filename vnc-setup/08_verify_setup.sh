#!/bin/bash
# Verification Script - Run as ROOT
# Checks if everything is configured correctly

set -e

echo "========================================="
echo "    VNC SETUP VERIFICATION"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_item() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

# 1. Check if dev user exists
echo "1. Checking dev user..."
id dev &>/dev/null
check_item $? "Dev user exists"
echo ""

# 2. Check VNC configuration
echo "2. Checking VNC configuration..."
if [ -f /home/dev/.vnc/xstartup ]; then
    check_item 0 "VNC xstartup exists"
    if grep -q "startxfce4" /home/dev/.vnc/xstartup; then
        check_item 0 "XFCE configured in xstartup"
    else
        check_item 1 "XFCE NOT configured (found $(grep -i "exec" /home/dev/.vnc/xstartup | tail -1))"
    fi
else
    check_item 1 "VNC xstartup NOT found"
fi

if [ -f /home/dev/.vnc/passwd ]; then
    check_item 0 "VNC password is set"
else
    check_item 1 "VNC password NOT set"
fi
echo ""

# 3. Check if VNC is running
echo "3. Checking VNC server..."
if pgrep -u dev Xtigervnc > /dev/null; then
    check_item 0 "VNC server is running as dev user"
    VNC_PID=$(pgrep -u dev Xtigervnc)
    echo "   Process: $(ps -p $VNC_PID -o args=)"
else
    check_item 1 "VNC server NOT running"
fi

if netstat -tlnp 2>/dev/null | grep -q ":5901"; then
    check_item 0 "VNC listening on port 5901"
else
    check_item 1 "VNC NOT listening on port 5901"
fi
echo ""

# 4. Check noVNC
echo "4. Checking noVNC..."
if pgrep websockify > /dev/null; then
    check_item 0 "websockify (noVNC) is running"
    WS_PID=$(pgrep websockify)
    echo "   Process: $(ps -p $WS_PID -o args=)"
else
    check_item 1 "websockify NOT running"
fi

if netstat -tlnp 2>/dev/null | grep -q ":6080"; then
    check_item 0 "noVNC listening on port 6080"
else
    check_item 1 "noVNC NOT listening on port 6080"
fi
echo ""

# 5. Check clipboard tools
echo "5. Checking clipboard support..."
command -v autocutsel &>/dev/null
check_item $? "autocutsel installed"
command -v xclip &>/dev/null
check_item $? "xclip installed"
echo ""

# 6. Check Antigravity
echo "6. Checking Antigravity IDE..."
command -v antigravity &>/dev/null
check_item $? "Antigravity installed"

if [ -f /home/dev/Desktop/antigravity.desktop ]; then
    check_item 0 "Antigravity desktop launcher exists"
else
    check_item 1 "Antigravity desktop launcher NOT found"
fi
echo ""

# 7. Check systemd services
echo "7. Checking systemd services..."
if systemctl is-enabled vncserver@1.service &>/dev/null; then
    check_item 0 "VNC service enabled for autostart"
else
    check_item 1 "VNC service NOT enabled"
fi

if systemctl is-enabled novnc.service &>/dev/null; then
    check_item 0 "noVNC service enabled for autostart"
else
    check_item 1 "noVNC service NOT enabled"
fi
echo ""

# 8. Check firewall
echo "8. Checking firewall..."
if command -v ufw &>/dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo -e "${YELLOW}!${NC} UFW firewall is active"
        if ufw status | grep -q "5901"; then
            check_item 0 "Port 5901 allowed in UFW"
        else
            check_item 1 "Port 5901 NOT allowed in UFW"
            echo "   Run: ufw allow 5901"
        fi
        if ufw status | grep -q "6080"; then
            check_item 0 "Port 6080 allowed in UFW"
        else
            check_item 1 "Port 6080 NOT allowed in UFW"
            echo "   Run: ufw allow 6080"
        fi
    else
        echo -e "${GREEN}✓${NC} UFW firewall is inactive (all ports open)"
    fi
else
    echo -e "${YELLOW}!${NC} UFW not installed (firewall may be open)"
fi
echo ""

# Summary
echo "========================================="
echo "           SUMMARY"
echo "========================================="
echo ""
echo "If all checks passed, you can access VNC at:"
echo ""
echo -e "  ${GREEN}http://152.42.229.221:6080/vnc.html${NC}"
echo ""
echo "Login credentials:"
echo "  - User: dev (logged in automatically in VNC)"
echo "  - VNC Password: (the password you set)"
echo ""
echo "To launch Antigravity:"
echo "  1. Connect to VNC via browser"
echo "  2. Open terminal (right-click → Terminal)"
echo "  3. Type: antigravity --no-sandbox"
echo "  4. Or double-click Antigravity icon on desktop"
echo ""
echo "========================================="
