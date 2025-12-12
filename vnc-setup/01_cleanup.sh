#!/bin/bash
# VNC Cleanup Script - Run as ROOT
# Kills all existing VNC and noVNC sessions

set -e

echo "=== VNC Cleanup Script ==="
echo "Stopping all VNC and noVNC processes..."

# Kill all VNC processes
pkill -9 Xtigervnc 2>/dev/null || echo "No Xtigervnc processes found"
pkill -9 Xtightvnc 2>/dev/null || echo "No Xtightvnc processes found"
pkill -9 Xvnc 2>/dev/null || echo "No Xvnc processes found"

# Kill websockify (noVNC)
pkill -9 websockify 2>/dev/null || echo "No websockify processes found"

# Kill autocutsel if running
pkill -9 autocutsel 2>/dev/null || echo "No autocutsel processes found"

# Clean up VNC directories for root and dev
echo "Cleaning VNC configuration directories..."
rm -rf /root/.vnc/*.pid 2>/dev/null || true
rm -rf /root/.vnc/*.log 2>/dev/null || true
rm -rf /home/dev/.vnc/*.pid 2>/dev/null || true
rm -rf /home/dev/.vnc/*.log 2>/dev/null || true

# Check if anything is still running
sleep 2
if pgrep -x "Xtigervnc" > /dev/null; then
    echo "WARNING: Some VNC processes still running"
    ps aux | grep -i vnc
else
    echo "✓ All VNC processes stopped"
fi

if pgrep -x "websockify" > /dev/null; then
    echo "WARNING: websockify still running"
    ps aux | grep websockify
else
    echo "✓ websockify stopped"
fi

echo "=== Cleanup Complete ==="
