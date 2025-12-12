#!/bin/bash
# Install and Configure Clipboard Support - Run as ROOT
# Enables copy-paste between local machine and VNC

set -e

echo "=== Installing Clipboard Support ==="

# Install autocutsel if not already installed
if ! command -v autocutsel &> /dev/null; then
    echo "Installing autocutsel..."
    apt update
    apt install -y autocutsel
    echo "✓ autocutsel installed"
else
    echo "✓ autocutsel already installed"
fi

# Install xclip for additional clipboard support
if ! command -v xclip &> /dev/null; then
    echo "Installing xclip..."
    apt install -y xclip
    echo "✓ xclip installed"
else
    echo "✓ xclip already installed"
fi

echo ""
echo "=== Clipboard Support Installed ==="
echo ""
echo "NOTE: Clipboard sync (autocutsel) is configured to start"
echo "automatically in the VNC xstartup script."
echo ""
echo "After connecting to VNC, clipboard should work for:"
echo "  - Copy from local → Paste in VNC"
echo "  - Copy from VNC → Paste in local"
