#!/bin/bash
# Master Installation Script
# Runs all setup steps in the correct order
# Run as: bash INSTALL.sh

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════╗
║                                               ║
║     ANTIGRAVITY VNC SETUP INSTALLER           ║
║     DigitalOcean Server Configuration         ║
║                                               ║
╚═══════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo "This script will set up VNC with Antigravity IDE"
echo "Server: 152.42.229.221"
echo "Access: http://152.42.229.221:6080/vnc.html"
echo ""

# Confirm before proceeding
read -p "Press ENTER to continue or Ctrl+C to cancel..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: This script must be run as root${NC}"
    echo "Please run: sudo bash INSTALL.sh"
    exit 1
fi

# Track progress
step=1
total_steps=8

run_step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[$step/$total_steps] $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    step=$((step + 1))
}

# Step 1: Cleanup
run_step "Cleaning up existing VNC sessions"
bash 01_cleanup.sh

# Step 2: Configure VNC for dev user
run_step "Configuring VNC for dev user with XFCE"
echo -e "${YELLOW}You will be prompted to set a VNC password${NC}"
echo -e "${YELLOW}Remember this password - you'll need it to connect!${NC}"
echo ""
sudo -u dev bash 02_configure_vnc_dev_user.sh

# Step 3: Start VNC
run_step "Starting VNC server"
sudo -u dev bash 03_start_vnc.sh

# Step 4: Start noVNC
run_step "Starting noVNC web interface"
bash 04_start_novnc.sh

# Step 5: Install clipboard support
run_step "Installing clipboard support"
bash 05_install_clipboard_support.sh

# Step 6: Create Antigravity launcher
run_step "Creating Antigravity launcher"
sudo -u dev bash 06_create_antigravity_launcher.sh

# Step 7: Create systemd services
run_step "Creating systemd services for auto-start"
bash 07_create_systemd_service.sh

# Step 8: Verify
run_step "Verifying installation"
bash 08_verify_setup.sh

# Success message
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════╗
║                                               ║
║          ✓ INSTALLATION COMPLETE!             ║
║                                               ║
╚═══════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}         NEXT STEPS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. Open your web browser"
echo ""
echo -e "2. Go to: ${YELLOW}http://152.42.229.221:6080/vnc.html${NC}"
echo ""
echo "3. Click 'Connect'"
echo ""
echo "4. Enter your VNC password"
echo ""
echo "5. You should see XFCE desktop!"
echo ""
echo "6. To launch Antigravity:"
echo "   - Double-click 'Antigravity IDE' icon on desktop"
echo "   - OR open terminal and type: antigravity --no-sandbox"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Show services status
echo "Services Status:"
systemctl is-active vncserver@1 >/dev/null 2>&1 && echo -e "  VNC Server:  ${GREEN}Active${NC}" || echo -e "  VNC Server:  ${RED}Inactive${NC}"
systemctl is-active novnc >/dev/null 2>&1 && echo -e "  noVNC:       ${GREEN}Active${NC}" || echo -e "  noVNC:       ${RED}Inactive${NC}"
echo ""

echo "To check status later, run: systemctl status vncserver@1 novnc"
echo "To restart services: systemctl restart vncserver@1 novnc"
echo ""
echo -e "${YELLOW}Happy coding with Antigravity! 🚀${NC}"
echo ""
