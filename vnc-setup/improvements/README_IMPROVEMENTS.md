# VNC Robustness Improvements

Complete set of improvements to make your VNC setup production-ready, secure, and highly reliable.

## 🎯 Overview

These improvements transform your basic VNC setup into a robust, enterprise-grade remote desktop solution with:

- **Security**: SSL/TLS, firewall, brute-force protection
- **Reliability**: Health checks, auto-restart, monitoring
- **Backup**: Automated backups, one-command restore
- **Performance**: Optimized settings, quality profiles

## 🚀 Quick Install

### Install All Improvements (Recommended)
```bash
cd /root/vnc-setup/improvements
chmod +x *.sh
./INSTALL_ALL_IMPROVEMENTS.sh
```

### Install Individual Improvements
```bash
# Security only
./01_security_hardening.sh

# Monitoring only
./02_monitoring_healthcheck.sh

# Backup system only
./03_backup_restore.sh

# Performance only
./04_performance_optimization.sh
```

## 📦 What Gets Installed

### 1. Security Hardening (`01_security_hardening.sh`)

**Features:**
- ✅ SSL/TLS certificate (HTTPS access)
- ✅ UFW firewall configuration
- ✅ Fail2ban brute-force protection
- ✅ Secure noVNC service
- ✅ Easy password change utility

**New Commands:**
- `change-vnc-password` - Change VNC password easily

**New Access:**
- HTTPS: `https://152.42.229.221:6080/vnc.html` (secure)
- HTTP: `http://152.42.229.221:6080/vnc.html` (legacy)

### 2. Monitoring & Health Checks (`02_monitoring_healthcheck.sh`)

**Features:**
- ✅ Automated health checks every 5 minutes
- ✅ Auto-restart VNC/noVNC if they fail
- ✅ Resource monitoring (CPU, memory, disk)
- ✅ Status dashboard
- ✅ Log rotation
- ✅ Alert system (extensible)

**New Commands:**
- `vnc-status` - Complete status dashboard
- `vnc-health-check` - Run health check manually
- `vnc-alert LEVEL MSG` - Send custom alerts

**Automated:**
- Health checks run every 5 minutes
- Auto-restart on failure
- Logs rotated daily/weekly

### 3. Backup & Restore (`03_backup_restore.sh`)

**Features:**
- ✅ One-command backup
- ✅ Daily automated backups
- ✅ Interactive restore
- ✅ Configuration export
- ✅ Keeps last 10 backups

**New Commands:**
- `vnc-backup` - Create backup now
- `vnc-restore` - Restore from backup (interactive)
- `vnc-export-config` - Export config as text

**Backups Include:**
- VNC configuration
- Systemd services
- SSL certificates
- Documentation

**Location:** `/root/vnc-backups/`

### 4. Performance Optimization (`04_performance_optimization.sh`)

**Features:**
- ✅ VNC compression optimized
- ✅ XFCE compositor disabled (faster)
- ✅ Network buffers increased
- ✅ Quality profiles (High/Balanced/Speed/Low-bandwidth)
- ✅ Connection quality checker
- ✅ Resource cleanup utility

**New Commands:**
- `vnc-tune` - Change quality profile (interactive)
- `vnc-quality-check` - Check connection performance
- `vnc-cleanup` - Clean old logs and temp files

**Quality Profiles:**
1. High Quality - Best image, more bandwidth
2. Balanced - Recommended (default)
3. High Speed - Faster, compressed
4. Low Bandwidth - For slow connections

## 📚 Complete Command Reference

### Status & Monitoring
```bash
vnc-status           # Full status dashboard
vnc-health-check     # Manual health check
vnc-quality-check    # Connection quality
```

### Security
```bash
change-vnc-password  # Change VNC password
ufw status           # Firewall status
fail2ban-client status sshd  # SSH protection
```

### Backup & Restore
```bash
vnc-backup           # Create backup
vnc-restore          # Restore from backup
vnc-export-config    # Export configuration
ls -lh /root/vnc-backups/  # View backups
```

### Performance
```bash
vnc-tune             # Change quality profile
vnc-quality-check    # Check performance
vnc-cleanup          # Clean old files
```

### Service Management
```bash
systemctl restart vncserver@1    # Restart VNC
systemctl restart novnc-secure   # Restart noVNC
systemctl status vncserver@1     # VNC status
```

## 📖 Documentation Files

After installation, detailed docs are in `/root/`:

- `VNC_IMPROVEMENTS_SUMMARY.txt` - Quick reference (start here)
- `SECURITY_INFO.txt` - Security configuration details
- `MONITORING_INFO.txt` - Monitoring system details
- `BACKUP_INFO.txt` - Backup system details
- `PERFORMANCE_INFO.txt` - Performance tuning details

## 🔧 Common Tasks

### Change VNC Password
```bash
change-vnc-password
# Then restart: systemctl restart vncserver@1
```

### Change SSH Password
```bash
passwd
```

### View Status
```bash
vnc-status
```

### Create Backup
```bash
vnc-backup
```

### Restore from Backup
```bash
vnc-restore
# Select backup number
# Confirm restoration
```

### Tune Performance
```bash
vnc-tune
# Select quality profile
# Restart: systemctl restart vncserver@1
```

### Check Health
```bash
vnc-health-check
```

## 🐛 Troubleshooting

### VNC Not Responding
```bash
# 1. Check status
vnc-status

# 2. Run health check
vnc-health-check

# 3. Restart VNC
systemctl restart vncserver@1
```

### Slow Performance
```bash
# 1. Check quality
vnc-quality-check

# 2. Try faster profile
vnc-tune  # Select "High Speed"

# 3. Clean up
vnc-cleanup

# 4. Restart
systemctl restart vncserver@1
```

### Need to Restore
```bash
# 1. List backups
ls -lh /root/vnc-backups/

# 2. Restore
vnc-restore

# 3. Select backup and confirm
```

### Certificate Warning in Browser
This is normal with self-signed certificates:
1. Click "Advanced" in browser
2. Click "Proceed to 152.42.229.221"
3. (For production, get Let's Encrypt certificate)

## 🔒 Security Best Practices

### Immediate (Do Now)
1. ✅ Change VNC password: `change-vnc-password`
2. ✅ Change SSH password: `passwd`
3. ✅ Test HTTPS access: `https://152.42.229.221:6080/vnc.html`

### Recommended
1. Set up SSH key authentication (disable password auth)
2. Configure fail2ban email alerts
3. Regular backups (already automated)
4. Monitor health check logs

### Advanced
1. Get proper SSL certificate (Let's Encrypt)
2. Set up IP allowlisting
3. Configure email/SMS alerts
4. Regular security updates

## 📊 Monitoring Details

### Automated Health Checks
- **Frequency:** Every 5 minutes
- **Actions:** Auto-restart if VNC/noVNC down
- **Logging:** `/var/log/vnc-health-check.log`
- **Alerts:** Resource warnings (CPU/Memory/Disk)

### View Health Check Logs
```bash
tail -f /var/log/vnc-health-check.log
journalctl -u vnc-health-check.service -f
```

### Health Check Status
```bash
systemctl status vnc-health-check.timer
systemctl list-timers vnc-health-check.timer
```

## 💾 Backup Details

### Automated Backups
- **Frequency:** Daily
- **Retention:** Last 10 backups
- **Location:** `/root/vnc-backups/`

### Manual Backup
```bash
vnc-backup
```

### View Backups
```bash
ls -lht /root/vnc-backups/
```

### Restore Process
```bash
vnc-restore
# Interactive menu:
# 1. Shows available backups
# 2. Select number
# 3. Confirm
# 4. Auto-restart services
```

## ⚡ Performance Tuning

### Quality Profiles

| Profile | Compression | Quality | Use Case |
|---------|-------------|---------|----------|
| High Quality | Max | Best | Fast network, best image |
| Balanced | Medium | Good | Recommended default |
| High Speed | Low | OK | Prioritize responsiveness |
| Low Bandwidth | Min | Lower | Slow connections |

### Change Profile
```bash
vnc-tune
# Select profile
# Restart: systemctl restart vncserver@1
```

### Custom Settings
Edit `/home/dev/.vnc/config`:
```ini
# Compression (1-9, higher = more)
ZlibLevel=6
CompressLevel=6

# Quality (1-9, higher = better)
quality=8

# Resolution
geometry=1920x1080
```

## 🔄 Auto-Start Configuration

All services auto-start on reboot:

```bash
# Check enabled services
systemctl list-unit-files | grep vnc

# Should show:
# vncserver@1.service - enabled
# novnc-secure.service - enabled
# vnc-health-check.timer - enabled
# vnc-backup.timer - enabled
```

## 📈 Resource Usage

### Check Resource Usage
```bash
vnc-quality-check
vnc-status
```

### Typical Usage
- **CPU:** 1-5% idle, 10-30% active
- **Memory:** 200-500 MB
- **Disk:** ~100 MB for VNC, logs rotate
- **Network:** Varies by activity, 100KB/s - 5MB/s

## 🆘 Getting Help

### View Documentation
```bash
cat /root/VNC_IMPROVEMENTS_SUMMARY.txt
cat /root/SECURITY_INFO.txt
cat /root/MONITORING_INFO.txt
cat /root/BACKUP_INFO.txt
cat /root/PERFORMANCE_INFO.txt
```

### Check Logs
```bash
# Health check logs
tail -f /var/log/vnc-health-check.log

# VNC logs
tail -f /home/dev/.vnc/*.log

# System logs
journalctl -u vncserver@1 -f
journalctl -u novnc-secure -f
```

### System Status
```bash
vnc-status  # Complete dashboard
```

## 🎓 Advanced Topics

### Email Alerts
Edit `/usr/local/bin/vnc-alert`:
```bash
# Uncomment and configure email
echo "$message" | mail -s "VNC Alert" your@email.com
```

### Webhook Notifications (Slack/Discord)
Edit `/usr/local/bin/vnc-alert`:
```bash
# Add webhook
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"$message\"}" \
  YOUR_WEBHOOK_URL
```

### Custom Health Checks
Edit `/usr/local/bin/vnc-health-check`:
- Add custom checks
- Modify restart logic
- Add custom alerts

### Let's Encrypt SSL
```bash
# Install certbot
apt install certbot

# Get certificate (requires domain)
certbot certonly --standalone -d your-domain.com

# Update novnc-secure.service
# Point to Let's Encrypt certificates
```

## 📝 Changelog

### Version 1.0 (Initial Release)
- Security hardening with SSL/TLS
- Health monitoring with auto-restart
- Automated backup system
- Performance optimizations
- Complete utilities suite

## 🎉 Summary

After installing these improvements, you'll have:

✅ **Secure:** HTTPS, firewall, fail2ban
✅ **Reliable:** Auto-restart, health checks
✅ **Protected:** Daily backups, easy restore
✅ **Fast:** Optimized settings, quality profiles
✅ **Monitored:** Status dashboard, alerts
✅ **Production-Ready:** Enterprise-grade setup

**Your VNC is now robust and ready for serious use!** 🚀
