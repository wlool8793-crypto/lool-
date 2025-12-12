# How to Transfer Scripts to Server

## Method 1: Using SCP (Recommended)

### From Linux/Mac
```bash
# Upload entire folder
scp -r vnc-setup root@152.42.229.221:/root/

# Or upload individual files
scp vnc-setup/*.sh root@152.42.229.221:/root/vnc-setup/
scp vnc-setup/*.md root@152.42.229.221:/root/vnc-setup/
```

### From Windows (PowerShell)
```powershell
# Upload entire folder
scp -r vnc-setup root@152.42.229.221:/root/

# Or use WinSCP (GUI tool)
# Download: https://winscp.net/
```

## Method 2: Manual Copy-Paste via SSH

1. Connect to server:
```bash
ssh root@152.42.229.221
```

2. Create directory:
```bash
mkdir -p /root/vnc-setup
cd /root/vnc-setup
```

3. Create each file using `nano` or `vi`:
```bash
# Example for creating INSTALL.sh
nano INSTALL.sh
# Paste the contents, then press Ctrl+X, Y, Enter to save
```

4. Make executable:
```bash
chmod +x *.sh
```

## Method 3: Using GitHub (if scripts are in a repo)

```bash
# On server
cd /root
git clone https://github.com/yourusername/vnc-setup.git
cd vnc-setup
chmod +x *.sh
```

## Method 4: Create on Server Using Heredoc

```bash
# Connect to server
ssh root@152.42.229.221

# Create directory
mkdir -p /root/vnc-setup
cd /root/vnc-setup

# Create INSTALL.sh (example - repeat for each file)
cat > INSTALL.sh << 'ENDOFFILE'
[paste entire content of INSTALL.sh here]
ENDOFFILE

# Make executable
chmod +x *.sh
```

## Method 5: Download from Cloud Storage

If you upload the scripts to Google Drive, Dropbox, or similar:

```bash
# On server, use wget or curl
wget https://yoursharedlink.com/vnc-setup.zip
unzip vnc-setup.zip
cd vnc-setup
chmod +x *.sh
```

## Verify Transfer

After transfer, verify all files are present:

```bash
cd /root/vnc-setup
ls -lh

# You should see:
# 01_cleanup.sh
# 02_configure_vnc_dev_user.sh
# 03_start_vnc.sh
# 04_start_novnc.sh
# 05_install_clipboard_support.sh
# 06_create_antigravity_launcher.sh
# 07_create_systemd_service.sh
# 08_verify_setup.sh
# INSTALL.sh
# INSTALLATION_GUIDE.md
# README.md
# TROUBLESHOOTING.sh
# QUICK_REFERENCE.md
```

## Then Run Installation

```bash
cd /root/vnc-setup
./INSTALL.sh
```

## Troubleshooting Transfer

### Permission denied
```bash
chmod +x *.sh
```

### File not found
```bash
# Check if files exist
ls -la /root/vnc-setup/

# Check current directory
pwd
```

### Script has Windows line endings (^M)
```bash
# Convert to Unix format
apt install dos2unix
dos2unix *.sh
```

---

Choose whichever method is easiest for you!
