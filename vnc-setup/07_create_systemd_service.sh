#!/bin/bash
# Create Systemd Services for Auto-Start - Run as ROOT
# Makes VNC and noVNC start automatically on boot

set -e

echo "=== Creating Systemd Services ==="

# Create VNC service for dev user
echo "Creating VNC service for dev user..."
cat > /etc/systemd/system/vncserver@.service << 'EOF'
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
EOF

echo "✓ VNC service created"

# Create noVNC service
echo "Creating noVNC service..."
cat > /etc/systemd/system/novnc.service << 'EOF'
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
EOF

echo "✓ noVNC service created"

# Reload systemd
systemctl daemon-reload

# Enable services
echo "Enabling services..."
systemctl enable vncserver@1.service
systemctl enable novnc.service

echo "✓ Services enabled"

echo ""
echo "=== Systemd Services Created ==="
echo ""
echo "Services created and enabled:"
echo "  - vncserver@1.service (VNC for dev user on display :1)"
echo "  - novnc.service (Web interface on port 6080)"
echo ""
echo "To manage services:"
echo "  - Start VNC:   systemctl start vncserver@1"
echo "  - Start noVNC: systemctl start novnc"
echo "  - Stop VNC:    systemctl stop vncserver@1"
echo "  - Stop noVNC:  systemctl stop novnc"
echo "  - Status:      systemctl status vncserver@1"
echo ""
echo "Services will now start automatically on boot!"
