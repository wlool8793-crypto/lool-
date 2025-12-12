# VNC Setup for Antigravity IDE

Complete setup scripts for running Antigravity IDE on DigitalOcean via web browser.

## 🚀 Quick Install

```bash
# 1. Connect to server
ssh root@152.42.229.221

# 2. Upload this folder to server
# (On your local machine)
scp -r vnc-setup root@152.42.229.221:/root/

# 3. Run installation
cd /root/vnc-setup
chmod +x *.sh
./INSTALL.sh
```

That's it! Access at: **http://152.42.229.221:6080/vnc.html**

## 📁 Files

| File | Description |
|------|-------------|
| `INSTALL.sh` | Master installation script - **START HERE** |
| `INSTALLATION_GUIDE.md` | Detailed documentation |
| `01_cleanup.sh` | Clean up existing VNC sessions |
| `02_configure_vnc_dev_user.sh` | Configure VNC for dev user with XFCE |
| `03_start_vnc.sh` | Start VNC server |
| `04_start_novnc.sh` | Start noVNC web interface |
| `05_install_clipboard_support.sh` | Install clipboard tools |
| `06_create_antigravity_launcher.sh` | Create desktop launcher |
| `07_create_systemd_service.sh` | Create auto-start services |
| `08_verify_setup.sh` | Verify installation |

## ✅ What This Sets Up

✅ VNC server running as `dev` user (not root)
✅ XFCE desktop (better VNC compatibility than GNOME)
✅ noVNC web interface on port 6080
✅ Clipboard support for copy-paste
✅ Antigravity IDE desktop launcher
✅ Systemd services for auto-start on boot

## 🔧 Manual Installation

If you prefer step-by-step:

```bash
bash 01_cleanup.sh
sudo -u dev bash 02_configure_vnc_dev_user.sh
sudo -u dev bash 03_start_vnc.sh
bash 04_start_novnc.sh
bash 05_install_clipboard_support.sh
sudo -u dev bash 06_create_antigravity_launcher.sh
bash 07_create_systemd_service.sh
bash 08_verify_setup.sh
```

## 🐛 Troubleshooting

```bash
# Check if everything is working
bash 08_verify_setup.sh

# Restart services
systemctl restart vncserver@1 novnc

# View logs
journalctl -u vncserver@1 -n 50
tail -f /home/dev/.vnc/*.log
```

## 📖 Documentation

See `INSTALLATION_GUIDE.md` for complete documentation including:
- Detailed step-by-step instructions
- Troubleshooting guide
- System architecture
- Common commands
- Technical details

## 🎯 Access

After installation:
- **URL:** http://152.42.229.221:6080/vnc.html
- **User:** dev (automatic login in VNC)
- **Password:** VNC password you set during installation

## 💻 Launching Antigravity

In the VNC session:
1. Double-click "Antigravity IDE" icon on desktop
2. OR open terminal: `antigravity --no-sandbox`

## 🆘 Support

If something doesn't work:
1. Run `bash 08_verify_setup.sh`
2. Check logs in `/home/dev/.vnc/*.log`
3. Ensure ports 5901 and 6080 are open
4. Verify VNC is running as `dev`, not `root`
