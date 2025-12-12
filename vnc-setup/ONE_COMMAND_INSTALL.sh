#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# ANTIGRAVITY VNC COMPLETE SETUP - ALL-IN-ONE INSTALLER
# ═══════════════════════════════════════════════════════════════════════
#
# This single script does EVERYTHING:
#   ✓ Cleans up old VNC sessions
#   ✓ Configures VNC for dev user with XFCE
#   ✓ Sets up clipboard support
#   ✓ Creates desktop launchers
#   ✓ Starts VNC and noVNC
#   ✓ Creates systemd services
#   ✓ Verifies installation
#
# USAGE: Just run this script on your server:
#   bash ONE_COMMAND_INSTALL.sh
#
# ═══════════════════════════════════════════════════════════════════════

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Banner
clear
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║         ANTIGRAVITY VNC COMPLETE SETUP INSTALLER                  ║
║         One Script to Rule Them All                               ║
║                                                                   ║
║  Server: 152.42.229.221                                           ║
║  Access: http://152.42.229.221:6080/vnc.html                      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: This script must be run as root${NC}"
    echo "Please run: sudo bash $0"
    exit 1
fi

# Progress tracking
current_step=0
total_steps=10

step() {
    current_step=$((current_step + 1))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[$current_step/$total_steps] $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════════
# STEP 1: CLEANUP
# ═══════════════════════════════════════════════════════════════════════
step "Cleaning up existing VNC sessions"

pkill -9 Xtigervnc 2>/dev/null && success "Killed Xtigervnc" || warning "No Xtigervnc running"
pkill -9 websockify 2>/dev/null && success "Killed websockify" || warning "No websockify running"
pkill -9 autocutsel 2>/dev/null && success "Killed autocutsel" || warning "No autocutsel running"

rm -rf /root/.vnc/*.pid 2>/dev/null || true
rm -rf /root/.vnc/*.log 2>/dev/null || true
rm -rf /home/dev/.vnc/*.pid 2>/dev/null || true
rm -rf /home/dev/.vnc/*.log 2>/dev/null || true

sleep 2
success "Cleanup complete"

# ═══════════════════════════════════════════════════════════════════════
# STEP 2: VERIFY DEV USER EXISTS
# ═══════════════════════════════════════════════════════════════════════
step "Verifying dev user exists"

if id "dev" &>/dev/null; then
    success "Dev user exists"
else
    error "Dev user does not exist!"
    echo "Creating dev user..."
    useradd -m -s /bin/bash dev
    echo "dev:dev123" | chpasswd
    usermod -aG sudo dev
    success "Dev user created with password: dev123"
fi

# ═══════════════════════════════════════════════════════════════════════
# STEP 3: INSTALL REQUIRED PACKAGES
# ═══════════════════════════════════════════════════════════════════════
step "Installing required packages"

# Check and install autocutsel
if ! command -v autocutsel &> /dev/null; then
    echo "Installing autocutsel..."
    apt update -qq
    DEBIAN_FRONTEND=noninteractive apt install -y autocutsel xclip
    success "Installed autocutsel and xclip"
else
    success "autocutsel already installed"
fi

# ═══════════════════════════════════════════════════════════════════════
# STEP 4: CONFIGURE VNC FOR DEV USER
# ═══════════════════════════════════════════════════════════════════════
step "Configuring VNC for dev user with XFCE"

# Create VNC directory
sudo -u dev mkdir -p /home/dev/.vnc

# Create xstartup
cat > /home/dev/.vnc/xstartup << 'XSTARTUP_EOF'
#!/bin/bash
# VNC xstartup script for XFCE desktop

# Start dbus if not running
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    eval $(dbus-launch --sh-syntax --exit-with-session)
fi

# Kill any existing clipboard managers
pkill -9 autocutsel 2>/dev/null || true

# Start clipboard synchronization
autocutsel -fork -s PRIMARY &
autocutsel -fork -s CLIPBOARD &

# Disable screensaver and power management
xset s off &
xset -dpms &
xset s noblank &

# Start XFCE desktop
exec startxfce4
XSTARTUP_EOF

chmod +x /home/dev/.vnc/xstartup
chown dev:dev /home/dev/.vnc/xstartup
success "Created xstartup with XFCE"

# Create VNC config
cat > /home/dev/.vnc/config << 'CONFIG_EOF'
# TigerVNC Configuration
geometry=1920x1080
depth=24
dpi=96
localhost=no
alwaysshared=yes
CONFIG_EOF

chmod 600 /home/dev/.vnc/config
chown dev:dev /home/dev/.vnc/config
success "Created VNC config"

# Set VNC password automatically
echo "Setting VNC password..."
VNC_PASSWORD="vnc123"  # Default password - change this!
echo "$VNC_PASSWORD" | sudo -u dev vncpasswd -f > /home/dev/.vnc/passwd
chmod 600 /home/dev/.vnc/passwd
chown dev:dev /home/dev/.vnc/passwd
success "VNC password set to: $VNC_PASSWORD"
warning "IMPORTANT: VNC password is: $VNC_PASSWORD"
warning "You can change it later by running: sudo -u dev vncpasswd"

# ═══════════════════════════════════════════════════════════════════════
# STEP 5: CREATE ANTIGRAVITY LAUNCHER
# ═══════════════════════════════════════════════════════════════════════
step "Creating Antigravity desktop launcher"

# Create desktop directory
sudo -u dev mkdir -p /home/dev/Desktop
sudo -u dev mkdir -p /home/dev/.local/share/applications

# Create desktop launcher
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

# Copy to applications menu
cp /home/dev/Desktop/antigravity.desktop /home/dev/.local/share/applications/
chown dev:dev /home/dev/.local/share/applications/antigravity.desktop

# Trust the launcher
sudo -u dev gio set /home/dev/Desktop/antigravity.desktop metadata::trusted true 2>/dev/null || true

success "Desktop launcher created"

# Create launch script
cat > /home/dev/launch-antigravity.sh << 'LAUNCH_EOF'
#!/bin/bash
cd ~
/usr/bin/antigravity --no-sandbox --user-data-dir=~/.config/antigravity-data "$@"
LAUNCH_EOF

chmod +x /home/dev/launch-antigravity.sh
chown dev:dev /home/dev/launch-antigravity.sh
success "Launch script created"

# ═══════════════════════════════════════════════════════════════════════
# STEP 6: START VNC SERVER
# ═══════════════════════════════════════════════════════════════════════
step "Starting VNC server as dev user"

# Kill any existing VNC session
sudo -u dev vncserver -kill :1 2>/dev/null || true
sleep 2

# Start VNC server
sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24
sleep 3

if pgrep -u dev Xtigervnc > /dev/null; then
    success "VNC server started on display :1 (port 5901)"
    ps aux | grep -E "dev.*Xtigervnc" | grep -v grep
else
    error "VNC server failed to start"
    echo "Check log: tail /home/dev/.vnc/*.log"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════
# STEP 7: START NOVNC WEB INTERFACE
# ═══════════════════════════════════════════════════════════════════════
step "Starting noVNC web interface"

# Kill any existing websockify
pkill -9 websockify 2>/dev/null || true
sleep 2

# Check if noVNC is installed
if [ ! -d "/usr/share/novnc" ]; then
    warning "noVNC not found, installing..."
    apt update -qq
    DEBIAN_FRONTEND=noninteractive apt install -y novnc
    success "Installed noVNC"
fi

# Start websockify
websockify -D \
    --web=/usr/share/novnc/ \
    6080 localhost:5901

sleep 3

if pgrep websockify > /dev/null; then
    success "noVNC started on port 6080"
    ps aux | grep websockify | grep -v grep
else
    error "websockify failed to start"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════
# STEP 8: CREATE SYSTEMD SERVICES
# ═══════════════════════════════════════════════════════════════════════
step "Creating systemd services for auto-start"

# Create VNC service
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

success "VNC service created"

# Create noVNC service
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

success "noVNC service created"

# Reload and enable services
systemctl daemon-reload
systemctl enable vncserver@1.service
systemctl enable novnc.service
success "Services enabled for auto-start"

# ═══════════════════════════════════════════════════════════════════════
# STEP 9: CONFIGURE FIREWALL
# ═══════════════════════════════════════════════════════════════════════
step "Configuring firewall"

if command -v ufw &>/dev/null; then
    if ufw status | grep -q "Status: active"; then
        ufw allow 5901 2>/dev/null || true
        ufw allow 6080 2>/dev/null || true
        success "Firewall rules added for ports 5901 and 6080"
    else
        warning "UFW is inactive, skipping firewall configuration"
    fi
else
    warning "UFW not installed, skipping firewall configuration"
fi

# ═══════════════════════════════════════════════════════════════════════
# STEP 10: VERIFICATION
# ═══════════════════════════════════════════════════════════════════════
step "Verifying installation"

echo ""
verification_passed=true

# Check dev user
if id dev &>/dev/null; then
    success "Dev user exists"
else
    error "Dev user missing"
    verification_passed=false
fi

# Check VNC files
if [ -f /home/dev/.vnc/xstartup ]; then
    success "VNC xstartup exists"
else
    error "VNC xstartup missing"
    verification_passed=false
fi

# Check VNC process
if pgrep -u dev Xtigervnc > /dev/null; then
    success "VNC server running as dev user"
else
    error "VNC server NOT running"
    verification_passed=false
fi

# Check VNC port
if netstat -tlnp 2>/dev/null | grep -q ":5901"; then
    success "VNC listening on port 5901"
else
    error "VNC NOT listening on port 5901"
    verification_passed=false
fi

# Check noVNC process
if pgrep websockify > /dev/null; then
    success "noVNC (websockify) running"
else
    error "noVNC NOT running"
    verification_passed=false
fi

# Check noVNC port
if netstat -tlnp 2>/dev/null | grep -q ":6080"; then
    success "noVNC listening on port 6080"
else
    error "noVNC NOT listening on port 6080"
    verification_passed=false
fi

# Check Antigravity
if command -v antigravity &>/dev/null; then
    success "Antigravity installed"
else
    warning "Antigravity not found in PATH"
fi

# Check clipboard tools
if command -v autocutsel &>/dev/null; then
    success "autocutsel installed"
else
    warning "autocutsel not installed"
fi

# Check systemd services
if systemctl is-enabled vncserver@1.service &>/dev/null; then
    success "VNC service enabled"
else
    warning "VNC service not enabled"
fi

if systemctl is-enabled novnc.service &>/dev/null; then
    success "noVNC service enabled"
else
    warning "noVNC service not enabled"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════
# SUCCESS BANNER
# ═══════════════════════════════════════════════════════════════════════

if [ "$verification_passed" = true ]; then
    echo ""
    echo -e "${GREEN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              ✓✓✓  INSTALLATION COMPLETE!  ✓✓✓                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
else
    echo ""
    echo -e "${YELLOW}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          ⚠  INSTALLATION COMPLETED WITH WARNINGS  ⚠              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════
# FINAL INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                    HOW TO ACCESS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "1. Open your web browser"
echo ""
echo -e "2. Go to: ${YELLOW}http://152.42.229.221:6080/vnc.html${NC}"
echo ""
echo -e "3. Click ${GREEN}'Connect'${NC}"
echo ""
echo -e "4. Enter VNC password: ${YELLOW}$VNC_PASSWORD${NC}"
echo ""
echo -e "5. You should see XFCE desktop!"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                  LAUNCH ANTIGRAVITY${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Once in VNC desktop:"
echo ""
echo "  Option 1: Double-click ${GREEN}'Antigravity IDE'${NC} icon on desktop"
echo ""
echo "  Option 2: Open terminal and type:"
echo "            ${YELLOW}antigravity --no-sandbox${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                  USEFUL COMMANDS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Check status:"
echo "  ${YELLOW}systemctl status vncserver@1 novnc${NC}"
echo ""
echo "Restart services:"
echo "  ${YELLOW}systemctl restart vncserver@1 novnc${NC}"
echo ""
echo "View VNC logs:"
echo "  ${YELLOW}tail -f /home/dev/.vnc/*.log${NC}"
echo ""
echo "Change VNC password:"
echo "  ${YELLOW}sudo -u dev vncpasswd${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}Happy coding with Antigravity! 🚀${NC}"
echo ""

# Save connection info to file
cat > /root/VNC_CONNECTION_INFO.txt << INFO_EOF
╔═══════════════════════════════════════════════════════════════════╗
║              ANTIGRAVITY VNC CONNECTION INFO                      ║
╚═══════════════════════════════════════════════════════════════════╝

Access URL:
  http://152.42.229.221:6080/vnc.html

Login:
  User: dev (automatic in VNC)
  VNC Password: $VNC_PASSWORD

Server:
  IP: 152.42.229.221
  SSH: ssh root@152.42.229.221

Launch Antigravity:
  In VNC terminal: antigravity --no-sandbox
  Or: Double-click desktop icon

Useful Commands:
  - Restart VNC: systemctl restart vncserver@1
  - Restart noVNC: systemctl restart novnc
  - Check status: systemctl status vncserver@1 novnc
  - View logs: tail -f /home/dev/.vnc/*.log
  - Change password: sudo -u dev vncpasswd

Services:
  ✓ VNC Server: Port 5901 (dev user)
  ✓ noVNC Web: Port 6080
  ✓ Auto-start: Enabled

Installation Date: $(date)
INFO_EOF

success "Connection info saved to: /root/VNC_CONNECTION_INFO.txt"
echo ""
echo "To view connection info anytime:"
echo "  ${YELLOW}cat /root/VNC_CONNECTION_INFO.txt${NC}"
echo ""

exit 0
