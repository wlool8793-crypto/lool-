#!/bin/bash
# Ultra Performance Rollback Script
# Reverts all optimizations to default settings

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              ULTRA PERFORMANCE ROLLBACK                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will revert all performance optimizations!${NC}"
echo ""
echo "This will:"
echo "  - Restore default sysctl settings"
echo "  - Disable performance systemd services"
echo "  - Restore default XFCE settings"
echo "  - Remove optimized launchers"
echo "  - Disable zram swap"
echo ""

read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled."
    exit 0
fi

echo ""
echo "Starting rollback..."
echo ""

# 1. Rollback Network Optimizations
echo -e "${BLUE}[1/5] Rolling back network optimizations...${NC}"

# Restore sysctl.conf from backup
SYSCTL_BACKUP=$(ls -t /etc/sysctl.conf.backup.* 2>/dev/null | head -1)
if [ -n "$SYSCTL_BACKUP" ]; then
    cp "$SYSCTL_BACKUP" /etc/sysctl.conf
    echo -e "${GREEN}✓ Restored sysctl.conf from backup${NC}"
else
    # Remove optimization sections
    sed -i '/# BBR CONGESTION CONTROL/,/^$/d' /etc/sysctl.conf 2>/dev/null || true
    sed -i '/# ULTRA NETWORK OPTIMIZATIONS/,/^$/d' /etc/sysctl.conf 2>/dev/null || true
    sed -i '/# ULTRA SYSTEM OPTIMIZATIONS/,/^$/d' /etc/sysctl.conf 2>/dev/null || true
    echo -e "${GREEN}✓ Removed network optimization settings${NC}"
fi

# Set TCP to cubic (default)
sysctl -w net.ipv4.tcp_congestion_control=cubic >/dev/null 2>&1 || true
echo -e "${GREEN}✓ TCP congestion control set to cubic (default)${NC}"

# 2. Rollback System Optimizations
echo ""
echo -e "${BLUE}[2/5] Rolling back system optimizations...${NC}"

# Disable performance services
systemctl disable cpu-performance.service 2>/dev/null || true
systemctl stop cpu-performance.service 2>/dev/null || true
systemctl disable io-scheduler.service 2>/dev/null || true
systemctl stop io-scheduler.service 2>/dev/null || true
systemctl disable disable-thp.service 2>/dev/null || true
systemctl stop disable-thp.service 2>/dev/null || true
systemctl disable readahead-optimize.service 2>/dev/null || true
systemctl stop readahead-optimize.service 2>/dev/null || true

# Remove service files
rm -f /etc/systemd/system/cpu-performance.service
rm -f /etc/systemd/system/io-scheduler.service
rm -f /etc/systemd/system/disable-thp.service
rm -f /etc/systemd/system/readahead-optimize.service
systemctl daemon-reload

# Set CPU to ondemand (balanced)
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -f $cpu/cpufreq/scaling_governor ]; then
        echo ondemand > $cpu/cpufreq/scaling_governor 2>/dev/null || \
        echo powersave > $cpu/cpufreq/scaling_governor 2>/dev/null || true
    fi
done

# Re-enable THP
echo always > /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null || true
echo always > /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null || true

echo -e "${GREEN}✓ System optimizations rolled back${NC}"

# 3. Rollback Desktop Optimizations
echo ""
echo -e "${BLUE}[3/5] Rolling back desktop optimizations...${NC}"

# Restore XFCE config from backup
XFCE_BACKUP=$(ls -td /home/dev/.config/xfce4.backup.* 2>/dev/null | head -1)
if [ -n "$XFCE_BACKUP" ]; then
    rm -rf /home/dev/.config/xfce4
    mv "$XFCE_BACKUP" /home/dev/.config/xfce4
    chown -R dev:dev /home/dev/.config/xfce4
    echo -e "${GREEN}✓ Restored XFCE config from backup${NC}"
else
    # Just remove the optimization configs
    rm -f /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml
    rm -f /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
    rm -f /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
    rm -f /home/dev/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml
    echo -e "${GREEN}✓ Removed XFCE optimization configs${NC}"
fi

# Remove autostart disables
rm -f /home/dev/.config/autostart/xfce4-power-manager.desktop
rm -f /home/dev/.config/autostart/xfce4-screensaver.desktop
rm -f /home/dev/.config/autostart/xscreensaver.desktop
rm -f /home/dev/.config/autostart/light-locker.desktop

echo -e "${GREEN}✓ Desktop optimizations rolled back${NC}"

# 4. Rollback Application Optimizations
echo ""
echo -e "${BLUE}[4/5] Rolling back application optimizations...${NC}"

# Remove optimized launchers
rm -f /home/dev/bin/antigravity-fast
rm -f /home/dev/bin/chrome-fast
rm -f /home/dev/bin/firefox-fast
rm -f /home/dev/bin/code-fast
rm -f /home/dev/Desktop/antigravity-optimized.desktop

# Remove aliases
rm -f /home/dev/.bash_aliases

# Remove PATH addition from .bashrc
sed -i '/export PATH="\$HOME\/bin:\$PATH"/d' /home/dev/.bashrc 2>/dev/null || true
sed -i '/export PATH="\$HOME\/bin:\$PATH"/d' /home/dev/.profile 2>/dev/null || true

echo -e "${GREEN}✓ Application optimizations rolled back${NC}"

# 5. Rollback Memory Optimizations
echo ""
echo -e "${BLUE}[5/5] Rolling back memory optimizations...${NC}"

# Disable zram
systemctl disable zram-swap.service 2>/dev/null || true
systemctl stop zram-swap.service 2>/dev/null || true
swapoff /dev/zram0 2>/dev/null || true
rm -f /etc/systemd/system/zram-swap.service
rm -f /etc/default/zramswap

# Disable OOM protection service
systemctl disable protect-vnc-oom.service 2>/dev/null || true
rm -f /etc/systemd/system/protect-vnc-oom.service
rm -f /usr/local/bin/protect-vnc-oom

# Remove tmpfs entries from fstab
sed -i '/# Ultra Performance: RAM-based temporary storage/d' /etc/fstab 2>/dev/null || true
sed -i '/tmpfs \/tmp tmpfs/d' /etc/fstab 2>/dev/null || true
sed -i '/tmpfs \/var\/tmp tmpfs/d' /etc/fstab 2>/dev/null || true

# Remove utilities
rm -f /usr/local/bin/memory-cleanup
rm -f /usr/local/bin/memory-monitor
rm -f /usr/local/bin/vnc-performance

# Disable preload
systemctl disable preload 2>/dev/null || true
systemctl stop preload 2>/dev/null || true

systemctl daemon-reload

echo -e "${GREEN}✓ Memory optimizations rolled back${NC}"

# Remove documentation files
echo ""
echo "Removing documentation..."
rm -f /root/NETWORK_OPTIMIZATIONS.txt
rm -f /root/SYSTEM_OPTIMIZATIONS.txt
rm -f /root/DESKTOP_OPTIMIZATIONS.txt
rm -f /root/APP_OPTIMIZATIONS.txt
rm -f /root/MEMORY_OPTIMIZATIONS.txt

# Apply sysctl changes
sysctl -p >/dev/null 2>&1 || true

# Restart VNC
echo ""
echo "Restarting VNC..."
pkill -u dev Xtigervnc 2>/dev/null || true
sleep 2
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 2>/dev/null || true
sudo -u dev vncserver :1 2>/dev/null || true
systemctl restart novnc-secure 2>/dev/null || true

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              ROLLBACK COMPLETE                                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "All ultra performance optimizations have been reverted."
echo ""
echo -e "${YELLOW}Note: A system reboot is recommended for all changes to take effect.${NC}"
echo ""
echo "To reboot: sudo reboot"
echo ""
