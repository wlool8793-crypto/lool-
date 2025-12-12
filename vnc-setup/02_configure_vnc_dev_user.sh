#!/bin/bash
# VNC Configuration Script for DEV USER
# Run this as: sudo -u dev bash 02_configure_vnc_dev_user.sh

set -e

# Ensure we're running as dev user
if [ "$USER" != "dev" ]; then
    echo "ERROR: This script must be run as dev user"
    echo "Run: sudo -u dev bash $0"
    exit 1
fi

echo "=== Configuring VNC for user: $USER ==="

# Create VNC directory
mkdir -p ~/.vnc
cd ~/.vnc

# Create xstartup file with XFCE
echo "Creating xstartup file with XFCE desktop..."
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
# VNC xstartup script for XFCE desktop

# Uncomment for debugging
# set -x
# exec > ~/.vnc/startup.log 2>&1

# Start dbus if not running
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    eval $(dbus-launch --sh-syntax --exit-with-session)
fi

# Kill any existing clipboard managers
pkill -9 autocutsel 2>/dev/null || true

# Start clipboard synchronization (fixes copy-paste)
autocutsel -fork -s PRIMARY &
autocutsel -fork -s CLIPBOARD &

# Disable screensaver and power management
xset s off &
xset -dpms &
xset s noblank &

# Start XFCE desktop
exec startxfce4
EOF

# Make xstartup executable
chmod +x ~/.vnc/xstartup

echo "✓ xstartup created"

# Set VNC password
echo "Setting VNC password..."
echo "Please enter a VNC password (6-8 characters recommended):"
vncpasswd

# Create VNC config file
echo "Creating VNC configuration..."
cat > ~/.vnc/config << 'EOF'
# TigerVNC Configuration
geometry=1920x1080
depth=24
dpi=96
localhost=no
alwaysshared=yes
EOF

echo "✓ VNC config created"

# Set correct permissions
chmod 600 ~/.vnc/config
chmod 755 ~/.vnc

echo "=== VNC Configuration Complete for $USER ==="
echo ""
echo "Configuration files created:"
echo "  - ~/.vnc/xstartup (XFCE desktop launcher)"
echo "  - ~/.vnc/config (VNC settings)"
echo "  - ~/.vnc/passwd (VNC password - encrypted)"
echo ""
echo "Next step: Start VNC server"
