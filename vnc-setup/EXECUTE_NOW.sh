#!/bin/bash
# This script connects to your server and does EVERYTHING
# Just run this from YOUR terminal where you have SSH access

echo "Connecting to 152.42.229.221 and running complete installation..."
echo ""

ssh root@152.42.229.221 'bash -s' << 'REMOTE_COMMANDS'
#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# ANTIGRAVITY VNC COMPLETE SETUP - REMOTE EXECUTION
# ═══════════════════════════════════════════════════════════════════════

set -e

# Color codes
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
║     ANTIGRAVITY VNC COMPLETE SETUP - REMOTE INSTALLER            ║
║     Server: 152.42.229.221                                        ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

current_step=0
total_steps=10

step() {
    current_step=$((current_step + 1))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[$current_step/$total_steps] $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

success() { echo -e "${GREEN}✓ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# ═══════════════════════════════════════════════════════════════════════
step "Cleaning up existing VNC sessions"
# ═══════════════════════════════════════════════════════════════════════

pkill -9 Xtigervnc 2>/dev/null && success "Killed Xtigervnc" || warning "No Xtigervnc running"
pkill -9 websockify 2>/dev/null && success "Killed websockify" || warning "No websockify running"
pkill -9 autocutsel 2>/dev/null && success "Killed autocutsel" || warning "No autocutsel running"

rm -rf /root/.vnc/*.pid /root/.vnc/*.log /home/dev/.vnc/*.pid /home/dev/.vnc/*.log 2>/dev/null || true
sleep 2
success "Cleanup complete"

# ═══════════════════════════════════════════════════════════════════════
step "Verifying dev user exists"
# ═══════════════════════════════════════════════════════════════════════

if id "dev" &>/dev/null; then
    success "Dev user exists"
else
    warning "Dev user does not exist - creating..."
    useradd -m -s /bin/bash dev
    echo "dev:dev123" | chpasswd
    usermod -aG sudo dev
    success "Dev user created with password: dev123"
fi

# ═══════════════════════════════════════════════════════════════════════
step "Installing required packages"
# ═══════════════════════════════════════════════════════════════════════

if ! command -v autocutsel &> /dev/null; then
    echo "Installing autocutsel..."
    apt update -qq
    DEBIAN_FRONTEND=noninteractive apt install -y autocutsel xclip >/dev/null 2>&1
    success "Installed autocutsel and xclip"
else
    success "autocutsel already installed"
fi

# ═══════════════════════════════════════════════════════════════════════
step "Configuring VNC for dev user with XFCE"
# ═══════════════════════════════════════════════════════════════════════

sudo -u dev mkdir -p /home/dev/.vnc

cat > /home/dev/.vnc/xstartup << 'XSTARTUP_EOF'
#!/bin/bash
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    eval $(dbus-launch --sh-syntax --exit-with-session)
fi
pkill -9 autocutsel 2>/dev/null || true
autocutsel -fork -s PRIMARY &
autocutsel -fork -s CLIPBOARD &
xset s off &
xset -dpms &
xset s noblank &
exec startxfce4
XSTARTUP_EOF

chmod +x /home/dev/.vnc/xstartup
chown dev:dev /home/dev/.vnc/xstartup
success "Created xstartup with XFCE"

cat > /home/dev/.vnc/config << 'CONFIG_EOF'
geometry=1920x1080
depth=24
dpi=96
localhost=no
alwaysshared=yes
CONFIG_EOF

chmod 600 /home/dev/.vnc/config
chown dev:dev /home/dev/.vnc/config
success "Created VNC config"

VNC_PASSWORD="vnc123"
echo "$VNC_PASSWORD" | sudo -u dev vncpasswd -f > /home/dev/.vnc/passwd
chmod 600 /home/dev/.vnc/passwd
chown dev:dev /home/dev/.vnc/passwd
success "VNC password set to: $VNC_PASSWORD"

# ═══════════════════════════════════════════════════════════════════════
step "Creating Antigravity desktop launcher"
# ═══════════════════════════════════════════════════════════════════════

sudo -u dev mkdir -p /home/dev/Desktop /home/dev/.local/share/applications

cat > /home/dev/Desktop/antigravity.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Antigravity IDE
Comment=AI-Powered Code Editor
Exec=/usr/bin/antigravity --no-sandbox
Icon=code
Terminal=false
Categories=Development;IDE;
StartupNotify=true
DESKTOP_EOF

chmod +x /home/dev/Desktop/antigravity.desktop
chown dev:dev /home/dev/Desktop/antigravity.desktop
cp /home/dev/Desktop/antigravity.desktop /home/dev/.local/share/applications/
chown dev:dev /home/dev/.local/share/applications/antigravity.desktop
sudo -u dev gio set /home/dev/Desktop/antigravity.desktop metadata::trusted true 2>/dev/null || true
success "Desktop launcher created"

cat > /home/dev/launch-antigravity.sh << 'LAUNCH_EOF'
#!/bin/bash
cd ~
/usr/bin/antigravity --no-sandbox --user-data-dir=~/.config/antigravity-data "$@"
LAUNCH_EOF

chmod +x /home/dev/launch-antigravity.sh
chown dev:dev /home/dev/launch-antigravity.sh
success "Launch script created"

# ═══════════════════════════════════════════════════════════════════════
step "Starting VNC server as dev user"
# ═══════════════════════════════════════════════════════════════════════

sudo -u dev vncserver -kill :1 2>/dev/null || true
sleep 2
sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24
sleep 3

if pgrep -u dev Xtigervnc > /dev/null; then
    success "VNC server started on display :1 (port 5901)"
else
    error "VNC server failed to start"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════
step "Starting noVNC web interface"
# ═══════════════════════════════════════════════════════════════════════

pkill -9 websockify 2>/dev/null || true
sleep 2

if [ ! -d "/usr/share/novnc" ]; then
    warning "noVNC not found, installing..."
    apt update -qq
    DEBIAN_FRONTEND=noninteractive apt install -y novnc >/dev/null 2>&1
    success "Installed noVNC"
fi

websockify -D --web=/usr/share/novnc/ 6080 localhost:5901
sleep 3

if pgrep websockify > /dev/null; then
    success "noVNC started on port 6080"
else
    error "websockify failed to start"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════
step "Creating systemd services for auto-start"
# ═══════════════════════════════════════════════════════════════════════

cat > /etc/systemd/system/vncserver@.service << 'VNC_SERVICE_EOF'
[Unit]
Description=Remote Desktop VNC Service for user %i
After=syslog.target network.target

[Service]
Type=forking
User=%i
PAMName=login
PIDFile=/home/%i/.vnc/%H:%i.pid
ExecStartPre=/bin/sh -c '/usr/bin/vncserver -kill :%i > /dev/null 2>&1 || :'
ExecStart=/usr/bin/vncserver :%i -geometry 1920x1080 -depth 24
ExecStop=/usr/bin/vncserver -kill :%i
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
VNC_SERVICE_EOF

cat > /etc/systemd/system/novnc.service << 'NOVNC_SERVICE_EOF'
[Unit]
Description=noVNC Web VNC Client
After=network.target vncserver@1.service
Requires=vncserver@1.service

[Service]
Type=simple
ExecStart=/usr/bin/websockify --web=/usr/share/novnc/ 6080 localhost:5901
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
NOVNC_SERVICE_EOF

systemctl daemon-reload
systemctl enable vncserver@1.service >/dev/null 2>&1
systemctl enable novnc.service >/dev/null 2>&1
success "Services enabled for auto-start"

# ═══════════════════════════════════════════════════════════════════════
step "Configuring firewall"
# ═══════════════════════════════════════════════════════════════════════

if command -v ufw &>/dev/null && ufw status | grep -q "Status: active"; then
    ufw allow 5901 2>/dev/null || true
    ufw allow 6080 2>/dev/null || true
    success "Firewall rules added"
else
    warning "UFW inactive or not installed"
fi

# ═══════════════════════════════════════════════════════════════════════
step "Verifying installation"
# ═══════════════════════════════════════════════════════════════════════

echo ""
id dev &>/dev/null && success "Dev user exists" || error "Dev user missing"
[ -f /home/dev/.vnc/xstartup ] && success "VNC xstartup exists" || error "xstartup missing"
pgrep -u dev Xtigervnc > /dev/null && success "VNC running as dev" || error "VNC NOT running"
netstat -tlnp 2>/dev/null | grep -q ":5901" && success "VNC port 5901 listening" || error "Port 5901 not listening"
pgrep websockify > /dev/null && success "noVNC running" || error "noVNC NOT running"
netstat -tlnp 2>/dev/null | grep -q ":6080" && success "noVNC port 6080 listening" || error "Port 6080 not listening"
command -v antigravity &>/dev/null && success "Antigravity installed" || warning "Antigravity not found"
systemctl is-enabled vncserver@1.service &>/dev/null && success "VNC service enabled" || warning "VNC service not enabled"
systemctl is-enabled novnc.service &>/dev/null && success "noVNC service enabled" || warning "noVNC service not enabled"

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║              ✓✓✓  INSTALLATION COMPLETE!  ✓✓✓                    ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                    ACCESS INFO${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  URL: ${YELLOW}http://152.42.229.221:6080/vnc.html${NC}"
echo -e "  Password: ${YELLOW}vnc123${NC}"
echo -e "  Desktop: XFCE (logged in as 'dev')"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "To launch Antigravity:"
echo "  - Double-click 'Antigravity IDE' icon on desktop"
echo "  - OR in terminal: antigravity --no-sandbox"
echo ""
echo "Useful commands:"
echo "  - Restart: systemctl restart vncserver@1 novnc"
echo "  - Status:  systemctl status vncserver@1 novnc"
echo "  - Logs:    tail -f /home/dev/.vnc/*.log"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""

# Save connection info
cat > /root/VNC_CONNECTION_INFO.txt << INFO_EOF
╔═══════════════════════════════════════════════════════════════════╗
║              ANTIGRAVITY VNC CONNECTION INFO                      ║
╚═══════════════════════════════════════════════════════════════════╝

Access URL: http://152.42.229.221:6080/vnc.html
VNC Password: vnc123
User: dev (automatic in VNC)

Launch Antigravity:
  - Double-click desktop icon
  - OR terminal: antigravity --no-sandbox

Useful Commands:
  systemctl restart vncserver@1 novnc
  systemctl status vncserver@1 novnc
  tail -f /home/dev/.vnc/*.log
  sudo -u dev vncpasswd

Installation Date: $(date)
INFO_EOF

echo "Connection info saved to: /root/VNC_CONNECTION_INFO.txt"

REMOTE_COMMANDS

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Installation complete! Open your browser:"
echo "http://152.42.229.221:6080/vnc.html"
echo "Password: vnc123"
echo "═══════════════════════════════════════════════════════════════════"
