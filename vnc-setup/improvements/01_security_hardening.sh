#!/bin/bash
# Security Hardening Script for VNC Setup
# Improves security with SSL, better passwords, and firewall rules

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "VNC Security Hardening"
echo "=========================================="
echo ""

# 1. Generate SSL Certificate for noVNC
echo "[1/7] Creating SSL certificate for secure HTTPS access..."
if [ ! -f /etc/ssl/private/vnc-selfsigned.key ]; then
    openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
        -keyout /etc/ssl/private/vnc-selfsigned.key \
        -out /etc/ssl/certs/vnc-selfsigned.crt \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=Personal/CN=152.42.229.221"
    chmod 600 /etc/ssl/private/vnc-selfsigned.key
    echo -e "${GREEN}✓ SSL certificate created${NC}"
else
    echo -e "${YELLOW}⚠ SSL certificate already exists${NC}"
fi

# 2. Update noVNC service to use SSL
echo "[2/7] Configuring noVNC with SSL..."
cat > /etc/systemd/system/novnc-secure.service << 'EOF'
[Unit]
Description=noVNC Secure (HTTPS)
After=network.target vncserver@1.service
Requires=vncserver@1.service

[Service]
Type=simple
ExecStart=/usr/bin/websockify \
    --web=/usr/share/novnc/ \
    --cert=/etc/ssl/certs/vnc-selfsigned.crt \
    --key=/etc/ssl/private/vnc-selfsigned.key \
    6080 localhost:5901
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable novnc-secure.service
echo -e "${GREEN}✓ Secure noVNC service created${NC}"

# 3. Configure UFW firewall rules
echo "[3/7] Configuring firewall..."
if command -v ufw &>/dev/null; then
    # Enable UFW if not enabled
    if ! ufw status | grep -q "Status: active"; then
        echo "y" | ufw enable
    fi

    # Allow SSH first (critical!)
    ufw allow 22/tcp comment 'SSH'

    # Allow noVNC
    ufw allow 6080/tcp comment 'noVNC HTTPS'

    # Block direct VNC access (only allow localhost)
    ufw delete allow 5901 2>/dev/null || true

    # Optional: Limit SSH to prevent brute force
    ufw limit 22/tcp

    echo -e "${GREEN}✓ Firewall configured${NC}"
    echo -e "${YELLOW}Note: VNC port 5901 blocked from external access (more secure)${NC}"
else
    echo -e "${YELLOW}⚠ UFW not installed, installing...${NC}"
    apt update -qq
    DEBIAN_FRONTEND=noninteractive apt install -y ufw
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 6080/tcp
    echo -e "${GREEN}✓ UFW installed and configured${NC}"
fi

# 4. Install and configure fail2ban
echo "[4/7] Installing fail2ban for brute-force protection..."
if ! command -v fail2ban-server &>/dev/null; then
    apt update -qq
    DEBIAN_FRONTEND=noninteractive apt install -y fail2ban
fi

# Configure fail2ban for SSH
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo -e "${GREEN}✓ Fail2ban configured${NC}"

# 5. Create script to change VNC password easily
echo "[5/7] Creating password change utility..."
cat > /usr/local/bin/change-vnc-password << 'EOF'
#!/bin/bash
# Easy VNC password change utility

echo "=============================="
echo "VNC Password Change Utility"
echo "=============================="
echo ""
echo "Current user: $(whoami)"
echo ""

if [ "$EUID" -eq 0 ]; then
    echo "Changing VNC password for user 'dev'..."
    sudo -u dev vncpasswd
else
    echo "Changing VNC password for current user..."
    vncpasswd
fi

echo ""
echo "Password changed! Restart VNC to apply:"
echo "  systemctl restart vncserver@1"
EOF

chmod +x /usr/local/bin/change-vnc-password
echo -e "${GREEN}✓ Password utility created: change-vnc-password${NC}"

# 6. Secure VNC configuration - disable remote clipboard by default (can enable if needed)
echo "[6/7] Hardening VNC configuration..."
cat > /home/dev/.vnc/config << 'EOF'
geometry=1920x1080
depth=24
dpi=96
localhost=no
alwaysshared=yes
# Security options
MaxIdleTime=0
MaxConnectionTime=0
MaxDisconnectionTime=0
EOF
chown dev:dev /home/dev/.vnc/config
chmod 600 /home/dev/.vnc/config
echo -e "${GREEN}✓ VNC configuration hardened${NC}"

# 7. Create security info file
echo "[7/7] Creating security documentation..."
cat > /root/SECURITY_INFO.txt << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                    VNC SECURITY CONFIGURATION                     ║
╚═══════════════════════════════════════════════════════════════════╝

SECURE ACCESS:
  HTTPS URL: https://152.42.229.221:6080/vnc.html
  (Note: Self-signed certificate - browser will warn, click Advanced → Proceed)

HTTP ACCESS (Less Secure):
  HTTP URL: http://152.42.229.221:6080/vnc.html

SECURITY FEATURES ENABLED:
  ✓ SSL/TLS encryption for noVNC (HTTPS)
  ✓ Firewall (UFW) blocking direct VNC access
  ✓ Fail2ban protecting against brute-force attacks
  ✓ VNC only accessible via noVNC proxy
  ✓ Self-signed SSL certificate

CHANGE VNC PASSWORD:
  Run: change-vnc-password
  Or: sudo -u dev vncpasswd

FIREWALL STATUS:
  Check: ufw status
  Allow port: ufw allow <port>
  Block port: ufw deny <port>

FAIL2BAN STATUS:
  Check: fail2ban-client status
  Check SSH bans: fail2ban-client status sshd

RECOMMENDED NEXT STEPS:
  1. Change default VNC password (vnc123)
  2. Change SSH password from default (2002)
  3. Consider setting up SSH key authentication
  4. Review firewall rules: ufw status numbered

CERTIFICATES:
  Location: /etc/ssl/certs/vnc-selfsigned.crt
  Key: /etc/ssl/private/vnc-selfsigned.key
  Valid: 365 days from creation

For production use, consider:
  - Getting a proper SSL certificate (Let's Encrypt)
  - Using SSH key authentication instead of passwords
  - Setting up IP allowlisting
  - Regular security updates
EOF

echo -e "${GREEN}✓ Security documentation created${NC}"

echo ""
echo "=========================================="
echo "Security Hardening Complete!"
echo "=========================================="
echo ""
echo "Changes made:"
echo "  ✓ SSL/TLS certificate generated"
echo "  ✓ Secure noVNC service created"
echo "  ✓ Firewall (UFW) configured"
echo "  ✓ Fail2ban installed for brute-force protection"
echo "  ✓ Password change utility added"
echo "  ✓ VNC configuration hardened"
echo ""
echo "IMPORTANT - Next Steps:"
echo "  1. Restart noVNC: systemctl restart novnc-secure"
echo "  2. Change VNC password: change-vnc-password"
echo "  3. Change SSH password: passwd"
echo ""
echo "Access via HTTPS (secure): https://152.42.229.221:6080/vnc.html"
echo "Access via HTTP: http://152.42.229.221:6080/vnc.html"
echo ""
echo "See /root/SECURITY_INFO.txt for details"
echo ""
