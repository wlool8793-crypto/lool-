#!/bin/bash

###############################################################################
# Squid Proxy Auto-Installation Script
# This script installs and configures Squid proxy on Ubuntu VMs
# Designed to run automatically on VM creation
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root. Use: sudo bash proxy_setup.sh"
fi

log "Starting Squid proxy installation..."

# Update package lists
log "Updating package lists..."
apt-get update -qq || error "Failed to update package lists"

# Install Squid
log "Installing Squid proxy server..."
DEBIAN_FRONTEND=noninteractive apt-get install -y squid apache2-utils || error "Failed to install Squid"

# Backup original configuration
log "Backing up original Squid configuration..."
cp /etc/squid/squid.conf /etc/squid/squid.conf.backup

# Create new Squid configuration
log "Creating optimized Squid configuration..."
cat > /etc/squid/squid.conf << 'EOF'
# Squid Proxy Configuration for Web Scraping
# Optimized for anonymity and performance

# Access Control Lists
acl localnet src 0.0.0.1-0.255.255.255
acl localnet src 10.0.0.0/8
acl localnet src 100.64.0.0/10
acl localnet src 169.254.0.0/16
acl localnet src 172.16.0.0/12
acl localnet src 192.168.0.0/16
acl localnet src fc00::/7
acl localnet src fe80::/10

# Allow all IPs (open proxy for scraping)
acl all src 0.0.0.0/0

# SSL ports
acl SSL_ports port 443

# Safe ports
acl Safe_ports port 80          # http
acl Safe_ports port 21          # ftp
acl Safe_ports port 443         # https
acl Safe_ports port 70          # gopher
acl Safe_ports port 210         # wais
acl Safe_ports port 1025-65535  # unregistered ports
acl Safe_ports port 280         # http-mgmt
acl Safe_ports port 488         # gss-http
acl Safe_ports port 591         # filemaker
acl Safe_ports port 777         # multiling http

acl CONNECT method CONNECT

# Deny requests to certain unsafe ports
http_access deny !Safe_ports

# Deny CONNECT to other than secure SSL ports
http_access deny CONNECT !SSL_ports

# Allow localhost access
http_access allow localhost manager
http_access deny manager

# Allow all requests (for scraping purposes)
http_access allow all

# Squid listening port
http_port 3128

# Hide client IP and proxy headers (important for anonymity)
forwarded_for delete
via off
follow_x_forwarded_for deny all
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
request_header_access Cache-Control deny all

# Performance tuning
cache_mem 256 MB
maximum_object_size_in_memory 512 KB
maximum_object_size 4 MB
cache_dir ufs /var/spool/squid 1000 16 256

# DNS settings
dns_nameservers 8.8.8.8 8.8.4.4

# Connection limits
client_lifetime 30 minutes
pconn_timeout 60 seconds
request_timeout 5 minutes

# Disable caching for dynamic content
refresh_pattern ^ftp:           1440    20%     10080
refresh_pattern ^gopher:        1440    0%      1440
refresh_pattern -i (/cgi-bin/|\?) 0     0%      0
refresh_pattern .               0       20%     4320

# Logging
access_log /var/log/squid/access.log squid
cache_log /var/log/squid/cache.log
cache_store_log /var/log/squid/store.log

# Coredump directory
coredump_dir /var/spool/squid

# Leave coredumps in the first cache dir
refresh_pattern \^ftp:          1440    20%     10080
refresh_pattern \^gopher:       1440    0%      1440
refresh_pattern -i (/cgi-bin/|\?) 0     0%      0
refresh_pattern .               0       20%     4320
EOF

log "Squid configuration created successfully"

# Create cache directories
log "Initializing Squid cache directories..."
squid -z || warning "Cache initialization had warnings (this is usually fine)"

# Configure firewall (UFW)
log "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp    # SSH
    ufw allow 3128/tcp  # Squid proxy
    ufw reload
    log "Firewall configured: Ports 22 and 3128 opened"
else
    warning "UFW not found, skipping firewall configuration"
fi

# Enable and start Squid service
log "Starting Squid proxy service..."
systemctl enable squid || error "Failed to enable Squid service"
systemctl restart squid || error "Failed to start Squid service"

# Wait for Squid to start
sleep 3

# Check Squid status
if systemctl is-active --quiet squid; then
    log "Squid proxy is running successfully!"
else
    error "Squid failed to start. Check logs: journalctl -u squid"
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')

# Display configuration summary
log "Installation complete!"
echo ""
echo "================================================================"
echo "  Squid Proxy Server Configuration Summary"
echo "================================================================"
echo "  Status: ${GREEN}Running${NC}"
echo "  Server IP: ${GREEN}${SERVER_IP}${NC}"
echo "  Proxy Port: ${GREEN}3128${NC}"
echo "  Proxy URL: ${GREEN}http://${SERVER_IP}:3128${NC}"
echo ""
echo "  Configuration File: /etc/squid/squid.conf"
echo "  Access Log: /var/log/squid/access.log"
echo "  Cache Log: /var/log/squid/cache.log"
echo ""
echo "  Test your proxy:"
echo "  ${YELLOW}curl -x http://${SERVER_IP}:3128 http://ifconfig.me${NC}"
echo "================================================================"

# Create a test endpoint
log "Creating proxy test endpoint..."
cat > /root/test_proxy.sh << 'TESTEOF'
#!/bin/bash
echo "Testing Squid proxy..."
PROXY_IP=$(curl -s ifconfig.me)
echo "Proxy IP: $PROXY_IP"
curl -x http://localhost:3128 http://ifconfig.me
TESTEOF

chmod +x /root/test_proxy.sh

log "Setup complete! Proxy is ready to use."

# Optional: Install monitoring tools
log "Installing monitoring tools..."
apt-get install -y htop iftop net-tools || warning "Some monitoring tools failed to install"

exit 0
