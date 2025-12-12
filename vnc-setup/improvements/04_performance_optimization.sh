#!/bin/bash
# VNC Performance Optimization Script
# Optimizes VNC settings for better performance and lower latency

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "VNC Performance Optimization"
echo "=========================================="
echo ""

# 1. Optimize VNC configuration
echo "[1/6] Optimizing VNC configuration..."
cat > /home/dev/.vnc/config << 'EOF'
# Display settings
geometry=1920x1080
depth=24
dpi=96

# Network settings
localhost=no
alwaysshared=yes

# Performance optimizations
ZlibLevel=6
CompressLevel=6
quality=8

# Security
MaxIdleTime=0
MaxConnectionTime=0
MaxDisconnectionTime=0
EOF

chown dev:dev /home/dev/.vnc/config
chmod 600 /home/dev/.vnc/config
echo -e "${GREEN}✓ VNC config optimized${NC}"

# 2. Optimize XFCE for better performance
echo "[2/6] Optimizing XFCE settings..."
sudo -u dev mkdir -p /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml

# Disable compositor for better performance
cat > /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="use_compositing" type="bool" value="false"/>
    <property name="frame_opacity" type="int" value="100"/>
    <property name="theme" type="string" value="Default"/>
    <property name="title_font" type="string" value="Sans Bold 9"/>
  </property>
</channel>
EOF

# Optimize panel settings
cat > /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-panel" version="1.0">
  <property name="panels" type="uint" value="1">
    <property name="panel-1" type="empty">
      <property name="autohide-behavior" type="uint" value="0"/>
      <property name="background-style" type="uint" value="0"/>
      <property name="size" type="uint" value="28"/>
    </property>
  </property>
</channel>
EOF

chown -R dev:dev /home/dev/.config/xfce4
echo -e "${GREEN}✓ XFCE optimized (compositor disabled)${NC}"

# 3. Create performance tuning script
echo "[3/6] Creating performance tuning utility..."
cat > /usr/local/bin/vnc-tune << 'EOF'
#!/bin/bash
# VNC Performance Tuning Utility

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}VNC Performance Tuning${NC}"
echo "======================="
echo ""
echo "Select quality profile:"
echo "  1) High Quality (slower, best image)"
echo "  2) Balanced (recommended)"
echo "  3) High Speed (faster, compressed)"
echo "  4) Low Bandwidth (for slow connections)"
echo ""
read -p "Choice [1-4]: " choice

case $choice in
    1)
        ZLIB=9
        COMP=9
        QUAL=9
        PROFILE="High Quality"
        ;;
    2)
        ZLIB=6
        COMP=6
        QUAL=8
        PROFILE="Balanced"
        ;;
    3)
        ZLIB=3
        COMP=3
        QUAL=6
        PROFILE="High Speed"
        ;;
    4)
        ZLIB=1
        COMP=1
        QUAL=4
        PROFILE="Low Bandwidth"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Applying profile: $PROFILE"
echo "  Compression Level: $COMP"
echo "  Zlib Level: $ZLIB"
echo "  Quality: $QUAL"

# Update VNC config
sed -i "/^ZlibLevel=/c\ZlibLevel=$ZLIB" /home/dev/.vnc/config
sed -i "/^CompressLevel=/c\CompressLevel=$COMP" /home/dev/.vnc/config
sed -i "/^quality=/c\quality=$QUAL" /home/dev/.vnc/config

echo ""
echo -e "${GREEN}✓ Profile applied${NC}"
echo ""
echo "Restart VNC to apply:"
echo "  systemctl restart vncserver@1"
EOF

chmod +x /usr/local/bin/vnc-tune
echo -e "${GREEN}✓ Tuning utility created: vnc-tune${NC}"

# 4. Optimize system for VNC
echo "[4/6] Applying system optimizations..."

# Increase network buffer sizes
cat >> /etc/sysctl.conf << 'EOF'

# VNC Performance Optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_window_scaling=1
EOF

sysctl -p >/dev/null 2>&1 || true
echo -e "${GREEN}✓ Network buffers optimized${NC}"

# 5. Create connection quality checker
echo "[5/6] Creating connection quality checker..."
cat > /usr/local/bin/vnc-quality-check << 'EOF'
#!/bin/bash
# VNC Connection Quality Checker

echo "VNC Connection Quality Check"
echo "============================"
echo ""

# Check if VNC is running
if ! pgrep -u dev Xtigervnc >/dev/null; then
    echo "VNC is not running"
    exit 1
fi

# Get VNC process info
VNC_PID=$(pgrep -u dev Xtigervnc)
echo "VNC Server:"
echo "  PID: $VNC_PID"

# CPU and Memory usage
CPU_USAGE=$(ps -p $VNC_PID -o %cpu --no-headers | tr -d ' ')
MEM_USAGE=$(ps -p $VNC_PID -o %mem --no-headers | tr -d ' ')
echo "  CPU: ${CPU_USAGE}%"
echo "  Memory: ${MEM_USAGE}%"

# Connection count
CONN_COUNT=$(netstat -an | grep ":5901" | grep ESTABLISHED | wc -l)
echo "  Active connections: $CONN_COUNT"

echo ""
echo "System Resources:"
TOTAL_CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
TOTAL_MEM=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
echo "  Total CPU: ${TOTAL_CPU}%"
echo "  Total Memory: ${TOTAL_MEM}%"

echo ""
echo "Network:"
# Check bandwidth (requires vnstat)
if command -v vnstat &>/dev/null; then
    vnstat -i eth0 --oneline 2>/dev/null | awk -F\; '{print "  Current: "$11" down, "$12" up"}'
else
    echo "  Install vnstat for bandwidth monitoring: apt install vnstat"
fi

echo ""
echo "VNC Configuration:"
grep -E "quality|Compress|Zlib" /home/dev/.vnc/config | sed 's/^/  /'

echo ""
echo "Recommendations:"
# Check CPU
if (( $(echo "$TOTAL_CPU > 80" | bc -l 2>/dev/null || echo 0) )); then
    echo "  ⚠ High CPU usage - consider reducing quality (vnc-tune)"
fi

# Check Memory
if (( $(echo "$TOTAL_MEM > 80" | bc -l 2>/dev/null || echo 0) )); then
    echo "  ⚠ High memory usage - close unnecessary applications"
fi

if [ "$CONN_COUNT" -gt 2 ]; then
    echo "  ⚠ Multiple connections - may impact performance"
fi

echo "  ℹ Tune performance: vnc-tune"
EOF

chmod +x /usr/local/bin/vnc-quality-check
echo -e "${GREEN}✓ Quality checker created: vnc-quality-check${NC}"

# 6. Create resource cleanup script
echo "[6/6] Creating resource cleanup utility..."
cat > /usr/local/bin/vnc-cleanup << 'EOF'
#!/bin/bash
# VNC Resource Cleanup Utility

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "VNC Resource Cleanup"
echo "===================="
echo ""

# Clean old logs
echo "Cleaning old logs..."
find /home/dev/.vnc/ -name "*.log" -mtime +7 -delete 2>/dev/null
find /var/log/ -name "vnc-*.log" -mtime +30 -delete 2>/dev/null
echo -e "${GREEN}✓ Old logs cleaned${NC}"

# Clean temp files
echo "Cleaning temp files..."
find /tmp/.X11-unix/ -type s -mtime +1 -delete 2>/dev/null || true
echo -e "${GREEN}✓ Temp files cleaned${NC}"

# Clean old backups (keep 10)
echo "Cleaning old backups..."
BACKUP_DIR="/root/vnc-backups"
if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/vnc-backup-*.tar.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        ls -1t "$BACKUP_DIR"/vnc-backup-*.tar.gz | tail -n +11 | xargs rm -f
        echo -e "${GREEN}✓ Old backups cleaned (kept last 10)${NC}"
    else
        echo -e "${YELLOW}No old backups to clean${NC}"
    fi
fi

# Show disk usage
echo ""
echo "Disk usage:"
df -h / | grep -v Filesystem

echo ""
echo -e "${GREEN}Cleanup complete!${NC}"
EOF

chmod +x /usr/local/bin/vnc-cleanup
echo -e "${GREEN}✓ Cleanup utility created: vnc-cleanup${NC}"

# Create performance info file
cat > /root/PERFORMANCE_INFO.txt << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║              VNC PERFORMANCE OPTIMIZATION                         ║
╚═══════════════════════════════════════════════════════════════════╝

OPTIMIZATIONS APPLIED:
  ✓ VNC compression and quality tuned
  ✓ XFCE compositor disabled (faster rendering)
  ✓ Network buffers increased
  ✓ Panel effects reduced

PERFORMANCE COMMANDS:
  vnc-tune             - Change quality profile (interactive)
  vnc-quality-check    - Check connection quality
  vnc-cleanup          - Clean old logs and temp files

QUALITY PROFILES:
  1. High Quality     - Best image, more bandwidth
  2. Balanced         - Recommended (default)
  3. High Speed       - Faster, compressed
  4. Low Bandwidth    - For slow connections

CURRENT SETTINGS:
  View: cat /home/dev/.vnc/config

PERFORMANCE MONITORING:
  Check CPU/Memory: vnc-quality-check
  System resources: vnc-status
  Process info: top -p $(pgrep Xtigervnc)

TIPS FOR BETTER PERFORMANCE:
  - Close unused applications in VNC
  - Use "High Speed" profile for slow networks
  - Reduce window animations in XFCE
  - Lower resolution if needed (1280x720)
  - Restart VNC weekly: systemctl restart vncserver@1

CHANGE RESOLUTION:
  Edit /home/dev/.vnc/config
  Change: geometry=1920x1080
  To: geometry=1280x720  (or other)
  Then: systemctl restart vncserver@1

NETWORK OPTIMIZATION:
  - Settings in /etc/sysctl.conf
  - TCP window scaling enabled
  - Larger network buffers

TROUBLESHOOTING SLOWNESS:
  1. Check: vnc-quality-check
  2. Try: vnc-tune (select "High Speed")
  3. Clean: vnc-cleanup
  4. Restart: systemctl restart vncserver@1
EOF

echo ""
echo "=========================================="
echo "Performance Optimization Complete!"
echo "=========================================="
echo ""
echo "Optimizations applied:"
echo "  ✓ VNC compression tuned (balanced)"
echo "  ✓ XFCE compositor disabled"
echo "  ✓ Network buffers increased"
echo "  ✓ Performance utilities added"
echo ""
echo "Try these commands:"
echo "  vnc-tune            - Change quality profile"
echo "  vnc-quality-check   - Check performance"
echo "  vnc-cleanup         - Free up space"
echo ""
echo "Restart VNC to apply all optimizations:"
echo "  systemctl restart vncserver@1"
echo ""
echo "See /root/PERFORMANCE_INFO.txt for details"
echo ""
