#!/bin/bash
# Start VNC Server as DEV USER
# Run this as: sudo -u dev bash 03_start_vnc.sh

set -e

# Ensure we're running as dev user
if [ "$USER" != "dev" ]; then
    echo "ERROR: This script must be run as dev user"
    echo "Run: sudo -u dev bash $0"
    exit 1
fi

echo "=== Starting VNC Server as $USER ==="

# Kill any existing VNC sessions for this user
vncserver -kill :1 2>/dev/null || echo "No existing VNC session on :1"

# Wait a moment
sleep 2

# Start VNC server on display :1 (port 5901)
echo "Starting VNC server on display :1..."
vncserver :1 -geometry 1920x1080 -depth 24

# Check if it started
sleep 3

if pgrep -u $USER Xtigervnc > /dev/null; then
    echo "✓ VNC server started successfully"
    echo ""
    echo "VNC Server Details:"
    echo "  - Display: :1"
    echo "  - Port: 5901"
    echo "  - User: $USER"
    echo "  - Desktop: XFCE"
    echo ""

    # Show the process
    ps aux | grep Xtigervnc | grep -v grep

    # Show log location
    echo ""
    echo "VNC log: ~/.vnc/$(hostname):1.log"
    echo "To view log: tail -f ~/.vnc/$(hostname):1.log"
else
    echo "✗ ERROR: VNC server failed to start"
    echo "Check log: tail ~/.vnc/$(hostname):1.log"
    exit 1
fi

echo ""
echo "=== VNC Server Running ==="
