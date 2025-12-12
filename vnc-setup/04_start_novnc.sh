#!/bin/bash
# Start noVNC Web Access - Run as ROOT
# Provides web browser access to VNC

set -e

echo "=== Starting noVNC Web Interface ==="

# Kill any existing websockify
pkill -9 websockify 2>/dev/null || echo "No existing websockify process"

# Wait a moment
sleep 2

# Check if noVNC is installed
if [ ! -d "/usr/share/novnc" ]; then
    echo "ERROR: noVNC not found at /usr/share/novnc"
    echo "Install with: apt install novnc"
    exit 1
fi

# Start websockify in background
echo "Starting websockify..."
websockify -D \
    --web=/usr/share/novnc/ \
    --cert=/etc/ssl/certs/ssl-cert-snakeoil.pem \
    --key=/etc/ssl/private/ssl-cert-snakeoil.key \
    6080 localhost:5901

# Wait and check if it started
sleep 3

if pgrep -x websockify > /dev/null; then
    echo "✓ noVNC started successfully"
    echo ""
    echo "noVNC Web Access:"
    echo "  - URL: http://152.42.229.221:6080/vnc.html"
    echo "  - Secure URL: https://152.42.229.221:6080/vnc.html"
    echo "  - Target VNC: localhost:5901"
    echo ""
    echo "Process:"
    ps aux | grep websockify | grep -v grep
else
    echo "✗ ERROR: websockify failed to start"
    exit 1
fi

echo ""
echo "=== noVNC Running ==="
echo ""
echo "NEXT STEPS:"
echo "1. Open browser and go to: http://152.42.229.221:6080/vnc.html"
echo "2. Click 'Connect'"
echo "3. Enter your VNC password"
echo "4. You should see XFCE desktop as 'dev' user"
