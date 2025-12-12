#!/bin/bash
# Create Antigravity Desktop Launcher - Run as DEV USER
# Creates a desktop icon for easy Antigravity launch

set -e

# Ensure we're running as dev user
if [ "$USER" != "dev" ]; then
    echo "ERROR: This script must be run as dev user"
    echo "Run: sudo -u dev bash $0"
    exit 1
fi

echo "=== Creating Antigravity Launcher ==="

# Create desktop directory if it doesn't exist
mkdir -p ~/Desktop

# Create desktop launcher
cat > ~/Desktop/antigravity.desktop << 'EOF'
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
EOF

# Make it executable
chmod +x ~/Desktop/antigravity.desktop

# Trust the launcher (for XFCE)
gio set ~/Desktop/antigravity.desktop metadata::trusted true 2>/dev/null || true

echo "✓ Desktop launcher created: ~/Desktop/antigravity.desktop"

# Also create in applications menu
mkdir -p ~/.local/share/applications
cp ~/Desktop/antigravity.desktop ~/.local/share/applications/

echo "✓ Application menu entry created"

# Create a simple launch script
cat > ~/launch-antigravity.sh << 'EOF'
#!/bin/bash
# Launch Antigravity IDE safely
cd ~
/usr/bin/antigravity --no-sandbox --user-data-dir=~/.config/antigravity-data "$@"
EOF

chmod +x ~/launch-antigravity.sh

echo "✓ Launch script created: ~/launch-antigravity.sh"

echo ""
echo "=== Antigravity Launcher Created ==="
echo ""
echo "You can now launch Antigravity by:"
echo "  1. Double-clicking icon on desktop"
echo "  2. Searching 'Antigravity' in application menu"
echo "  3. Running: ~/launch-antigravity.sh"
echo "  4. Running: antigravity --no-sandbox"
