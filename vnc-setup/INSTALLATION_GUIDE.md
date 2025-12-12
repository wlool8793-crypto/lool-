# Antigravity VNC Setup - Complete Installation Guide

## 🎯 Goal
Run Antigravity IDE on DigitalOcean server accessible via web browser at `http://152.42.229.221:6080/vnc.html`

## 📋 Prerequisites
- ✅ DigitalOcean server: 152.42.229.221 (8GB RAM, 4 vCPUs)
- ✅ Ubuntu 22.04 LTS
- ✅ SSH access: `ssh root@152.42.229.221`
- ✅ `dev` user already exists
- ✅ Software installed: VNC, noVNC, Antigravity, XFCE

## 🚀 Quick Start (5 Minutes)

### Step 1: Connect to Server
```bash
ssh root@152.42.229.221
```

### Step 2: Upload Scripts
On your local machine, upload all scripts from `vnc-setup/` folder:
```bash
# From your local machine where you have the vnc-setup folder
scp -r vnc-setup root@152.42.229.221:/root/
```

Or manually copy each script via SSH.

### Step 3: Run Installation (On Server)
Once connected to the server via SSH:

```bash
# Navigate to the scripts directory
cd /root/vnc-setup

# Make all scripts executable
chmod +x *.sh

# Run the complete setup
./INSTALL.sh
```

The installation script will run all steps automatically. You'll be prompted to set a VNC password.

---

## 📝 Manual Step-by-Step Instructions

If you prefer to run each step manually or if the automatic installation fails:

### 1️⃣ Clean Up Existing VNC Sessions
```bash
cd /root/vnc-setup
bash 01_cleanup.sh
```
**What it does:** Kills all existing VNC and noVNC processes, cleans up lock files

---

### 2️⃣ Configure VNC for Dev User with XFCE
```bash
sudo -u dev bash 02_configure_vnc_dev_user.sh
```
**What it does:**
- Creates VNC configuration files in `/home/dev/.vnc/`
- Sets up XFCE desktop (not GNOME)
- Configures clipboard support (autocutsel)
- **You'll be prompted to set a VNC password** (remember this!)

---

### 3️⃣ Start VNC Server
```bash
sudo -u dev bash 03_start_vnc.sh
```
**What it does:**
- Starts VNC server on display :1 (port 5901)
- Runs as `dev` user (NOT root)
- Uses XFCE desktop environment

---

### 4️⃣ Start noVNC Web Interface
```bash
bash 04_start_novnc.sh
```
**What it does:**
- Starts websockify on port 6080
- Enables web browser access to VNC
- Accessible at `http://152.42.229.221:6080/vnc.html`

---

### 5️⃣ Install Clipboard Support
```bash
bash 05_install_clipboard_support.sh
```
**What it does:**
- Installs `autocutsel` and `xclip`
- Enables copy-paste between local machine and VNC

---

### 6️⃣ Create Antigravity Launcher
```bash
sudo -u dev bash 06_create_antigravity_launcher.sh
```
**What it does:**
- Creates desktop icon for Antigravity
- Creates application menu entry
- Creates launch script with proper flags

---

### 7️⃣ Create Systemd Services (Optional but Recommended)
```bash
bash 07_create_systemd_service.sh
```
**What it does:**
- Makes VNC start automatically on boot
- Makes noVNC start automatically on boot
- Enables auto-restart if services crash

To start services now:
```bash
systemctl start vncserver@1
systemctl start novnc
```

---

### 8️⃣ Verify Setup
```bash
bash 08_verify_setup.sh
```
**What it does:**
- Checks if all components are running correctly
- Verifies VNC is running as `dev` user
- Checks if ports are open
- Provides diagnostic information

---

## ✅ Verification & Testing

### Check if Services Are Running
```bash
# Check VNC server
ps aux | grep Xtigervnc | grep dev

# Check noVNC
ps aux | grep websockify

# Check ports
netstat -tlnp | grep -E ':(5901|6080)'
```

Expected output:
- VNC running as user `dev` on port 5901
- websockify running on port 6080

### Access VNC via Browser
1. Open browser: `http://152.42.229.221:6080/vnc.html`
2. Click **Connect**
3. Enter VNC password (set in step 2)
4. You should see **XFCE desktop** logged in as `dev`

### Test Antigravity
In the VNC session:
1. Right-click desktop → **Open Terminal**
2. Type: `antigravity --no-sandbox`
3. Antigravity should launch successfully!

Or double-click the **Antigravity IDE** icon on desktop.

---

## 🔧 Troubleshooting

### Problem: VNC Shows Black Screen
```bash
# Check VNC logs
sudo -u dev tail -f /home/dev/.vnc/*.log

# Common fix: Restart VNC
sudo -u dev vncserver -kill :1
sudo -u dev bash /root/vnc-setup/03_start_vnc.sh
```

### Problem: Can't Connect to noVNC
```bash
# Check if websockify is running
ps aux | grep websockify

# Check firewall
ufw status
ufw allow 6080
ufw allow 5901

# Restart noVNC
pkill websockify
bash /root/vnc-setup/04_start_novnc.sh
```

### Problem: Antigravity Won't Launch
```bash
# From VNC terminal, try:
antigravity --no-sandbox --user-data-dir=/tmp/antigravity-data

# Check if running as dev user
whoami  # Should show 'dev', not 'root'
```

### Problem: Copy-Paste Doesn't Work
```bash
# In VNC session terminal:
pkill autocutsel
autocutsel -fork -s PRIMARY &
autocutsel -fork -s CLIPBOARD &
```

### Problem: Service Won't Start on Boot
```bash
# Check service status
systemctl status vncserver@1
systemctl status novnc

# View logs
journalctl -u vncserver@1 -n 50
journalctl -u novnc -n 50

# Re-enable services
systemctl daemon-reload
systemctl enable vncserver@1
systemctl enable novnc
```

---

## 🔄 Common Commands

### Restart Everything
```bash
# Stop all
systemctl stop novnc
systemctl stop vncserver@1

# Start all
systemctl start vncserver@1
systemctl start novnc
```

### Check Status
```bash
systemctl status vncserver@1
systemctl status novnc
```

### View Logs
```bash
# VNC log
sudo -u dev tail -f /home/dev/.vnc/*.log

# noVNC log
journalctl -u novnc -f

# VNC service log
journalctl -u vncserver@1 -f
```

### Stop Services
```bash
systemctl stop novnc
systemctl stop vncserver@1
```

---

## 📊 System Architecture

```
┌─────────────────┐
│  Your Browser   │
│  (Bangladesh)   │
└────────┬────────┘
         │ HTTP
         │ Port 6080
         ▼
┌─────────────────────────┐
│   DigitalOcean Server   │
│   152.42.229.221        │
│   (Singapore - SGP1)    │
│                         │
│  ┌──────────────────┐   │
│  │    websockify    │   │
│  │  (noVNC Server)  │   │
│  │    Port 6080     │   │
│  └────────┬─────────┘   │
│           │              │
│           ▼              │
│  ┌──────────────────┐   │
│  │   VNC Server     │   │
│  │   (TigerVNC)     │   │
│  │   Port 5901      │   │
│  │   User: dev      │   │
│  └────────┬─────────┘   │
│           │              │
│           ▼              │
│  ┌──────────────────┐   │
│  │ XFCE Desktop     │   │
│  │                  │   │
│  │ ┌──────────────┐ │   │
│  │ │ Antigravity  │ │   │
│  │ │     IDE      │ │   │
│  │ └──────────────┘ │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

---

## 🎓 Technical Details

### Why XFCE Instead of GNOME?
- GNOME has compatibility issues with VNC
- Applications don't launch properly from GNOME menu over VNC
- XFCE is lighter and works better with remote desktop

### Why Dev User Instead of Root?
- Electron apps (Antigravity, Chrome, VS Code) refuse to run as root for security
- Even with `--no-sandbox`, they don't work properly as root
- Running as non-root user is best practice

### Port Information
- **5901**: VNC server (TigerVNC) - local only
- **6080**: noVNC web interface - publicly accessible

### Files Created
```
/home/dev/.vnc/xstartup          # XFCE startup script
/home/dev/.vnc/config            # VNC configuration
/home/dev/.vnc/passwd            # VNC password (encrypted)
/home/dev/Desktop/antigravity.desktop  # Desktop launcher
/home/dev/launch-antigravity.sh  # Launch script
/etc/systemd/system/vncserver@.service  # VNC systemd service
/etc/systemd/system/novnc.service       # noVNC systemd service
```

---

## 💰 Cost Estimate

**Server Specs:**
- 8 GB RAM / 4 vCPUs / 80 GB Disk
- Cost: ~$48/month
- **Your credit: $200 (student)**
- **Duration: ~4 months**

---

## 🎉 Success Criteria

✅ Open `http://152.42.229.221:6080/vnc.html` in browser
✅ See XFCE desktop running as `dev` user
✅ Copy-paste works between local and VNC
✅ Antigravity IDE launches without errors
✅ Services auto-start on reboot

---

## 📞 Support

If something doesn't work:
1. Run `bash 08_verify_setup.sh` for diagnostics
2. Check logs in `/home/dev/.vnc/*.log`
3. Ensure firewall allows ports 5901 and 6080
4. Verify VNC is running as `dev`, not `root`

---

**Created:** 2025-12-06
**Server:** 152.42.229.221 (DigitalOcean SGP1)
**Access:** http://152.42.229.221:6080/vnc.html
