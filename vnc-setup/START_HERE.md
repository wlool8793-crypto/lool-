# 🚀 START HERE - Antigravity VNC Setup

## ⚡ **FASTEST METHOD** (Recommended)

### 1. Copy this file to your server:
```bash
scp ONE_COMMAND_INSTALL.sh root@152.42.229.221:/tmp/
```

### 2. SSH to your server:
```bash
ssh root@152.42.229.221
```

### 3. Run the installer:
```bash
bash /tmp/ONE_COMMAND_INSTALL.sh
```

### 4. Open your browser:
```
http://152.42.229.221:6080/vnc.html
```

**Password:** vnc123

**That's it! You're done!** 🎉

---

## 📦 **What Gets Installed:**

- ✅ VNC server (running as dev user, not root)
- ✅ XFCE desktop (VNC-friendly)
- ✅ noVNC web interface (browser access)
- ✅ Clipboard support (copy-paste works)
- ✅ Antigravity desktop launcher
- ✅ Auto-start on boot (systemd services)

---

## 🎯 **Launch Antigravity:**

Once in VNC desktop:
1. Double-click **"Antigravity IDE"** icon
2. OR open terminal: `antigravity --no-sandbox`

---

## 🔧 **Useful Commands:**

```bash
# Restart services
systemctl restart vncserver@1 novnc

# Check status
systemctl status vncserver@1 novnc

# View logs
tail -f /home/dev/.vnc/*.log

# Change VNC password
sudo -u dev vncpasswd

# View connection info
cat /root/VNC_CONNECTION_INFO.txt
```

---

## 📁 **Other Files in This Package:**

- **ONE_COMMAND_INSTALL.sh** - All-in-one installer ⭐
- **INSTALL.sh** - Modular installer (runs 01-08 scripts)
- **01-08_*.sh** - Individual setup scripts
- **TROUBLESHOOTING.sh** - Auto-fix common issues
- **INSTALLATION_GUIDE.md** - Complete documentation
- **QUICK_REFERENCE.md** - Command cheat sheet
- **SUMMARY.md** - Package overview

---

## 🐛 **If Something Goes Wrong:**

```bash
# Auto-fix issues
bash /tmp/TROUBLESHOOTING.sh

# Check what's wrong
bash /tmp/08_verify_setup.sh
```

---

## 💡 **Quick Tips:**

- VNC Password: **vnc123** (change with `sudo -u dev vncpasswd`)
- Services auto-start on reboot
- Copy-paste works between local and VNC
- XFCE is lighter and faster than GNOME
- Everything runs as 'dev' user, not root

---

## 🎊 **Success Looks Like:**

1. Browser shows XFCE desktop ✅
2. Desktop has Antigravity icon ✅
3. Antigravity launches without errors ✅
4. Copy-paste works ✅
5. Services survive reboot ✅

---

**Happy coding! 🚀**
