# Quick Reference Card

## 🔗 Access URL
```
http://152.42.229.221:6080/vnc.html
```

## 🔐 SSH Access
```bash
ssh root@152.42.229.221
```

## ⚡ Quick Commands

### Start/Stop Services
```bash
# Start everything
systemctl start vncserver@1 novnc

# Stop everything
systemctl stop vncserver@1 novnc

# Restart everything
systemctl restart vncserver@1 novnc

# Check status
systemctl status vncserver@1 novnc
```

### Manual Start (without systemd)
```bash
# Start VNC
sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24

# Start noVNC
websockify -D --web=/usr/share/novnc/ 6080 localhost:5901
```

### Manual Stop
```bash
# Stop VNC
sudo -u dev vncserver -kill :1

# Stop noVNC
pkill websockify
```

## 🐛 Troubleshooting

### Quick Diagnosis
```bash
bash /root/vnc-setup/08_verify_setup.sh
```

### Auto-Fix Common Issues
```bash
bash /root/vnc-setup/TROUBLESHOOTING.sh
```

### View Logs
```bash
# VNC log
tail -f /home/dev/.vnc/*.log

# noVNC service log
journalctl -u novnc -f

# VNC service log
journalctl -u vncserver@1 -f
```

### Check Processes
```bash
# Check if VNC is running
ps aux | grep Xtigervnc

# Check if noVNC is running
ps aux | grep websockify

# Check ports
netstat -tlnp | grep -E ':(5901|6080)'
```

## 🚀 Launch Antigravity

### In VNC Terminal
```bash
antigravity --no-sandbox
```

### Or use the desktop launcher
Double-click "Antigravity IDE" icon on desktop

## 🔄 Complete Restart
```bash
# Stop all
systemctl stop novnc vncserver@1
pkill -9 websockify
sudo -u dev vncserver -kill :1

# Wait 3 seconds
sleep 3

# Start all
sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24
websockify -D --web=/usr/share/novnc/ 6080 localhost:5901
```

## 📊 Port Information
- **5901** - VNC Server (TigerVNC)
- **6080** - noVNC Web Interface

## 🔧 Firewall
```bash
# Check firewall
ufw status

# Open ports if needed
ufw allow 5901
ufw allow 6080
```

## 📁 Important Files
```
/home/dev/.vnc/xstartup              # XFCE startup script
/home/dev/.vnc/config                # VNC config
/home/dev/.vnc/passwd                # VNC password
/etc/systemd/system/vncserver@.service  # VNC service
/etc/systemd/system/novnc.service       # noVNC service
```

## ⚠️ Common Issues

### Black screen in VNC
```bash
sudo -u dev vncserver -kill :1
sudo -u dev vncserver :1 -geometry 1920x1080 -depth 24
```

### Can't connect to noVNC
```bash
pkill websockify
websockify -D --web=/usr/share/novnc/ 6080 localhost:5901
```

### Antigravity won't launch
```bash
# Make sure you're user 'dev' not 'root'
whoami

# Launch with flags
antigravity --no-sandbox --user-data-dir=/tmp/antigravity-data
```

### Copy-paste not working
```bash
# In VNC terminal
pkill autocutsel
autocutsel -fork -s PRIMARY &
autocutsel -fork -s CLIPBOARD &
```

## 📞 Emergency Full Reinstall
```bash
cd /root/vnc-setup
bash INSTALL.sh
```

---

**Keep this handy for quick reference!**
