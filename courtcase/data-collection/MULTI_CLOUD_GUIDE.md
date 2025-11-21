# Multi-Cloud VM Deployment Guide
## Indian Kanoon Scraper Project

Complete guide to deploying a distributed proxy infrastructure across multiple cloud providers to scrape 1.4M legal documents.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Cloud Provider Setup](#cloud-provider-setup)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Monitoring](#monitoring)
8. [Cost Management](#cost-management)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This system deploys 40+ VMs across multiple cloud providers (DigitalOcean, Vultr, Linode, Oracle Cloud) and configures them as Squid proxy servers for distributed web scraping.

### Benefits

- **80+ rotating proxy IPs** for avoiding rate limits
- **Geographic distribution** across multiple regions
- **Cost-effective** using free tier credits (~$400 total)
- **Automated deployment** and configuration
- **Real-time monitoring** dashboard

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Cloud Providers                        │
├─────────────────────────────────────────────────────────┤
│  DigitalOcean (15 VMs) │ Vultr (10 VMs)                │
│  Linode (10 VMs)       │ Oracle Cloud (4 VMs)          │
└───────────────┬─────────────────────────────────────────┘
                │
                ↓ Squid Proxy (port 3128)
                │
┌───────────────┴─────────────────────────────────────────┐
│           Indian Kanoon Scraper                         │
│  - Rotating proxy selection                             │
│  - Concurrent requests (32)                             │
│  - PDF downloads                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### Required Software

- **Python 3.10+**
- **pip** (Python package manager)
- **SSH key pair** (for VM access)

### Generate SSH Keys (if needed)

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Press Enter to use default location (`~/.ssh/id_rsa`)

---

## ☁️ Cloud Provider Setup

### 1. DigitalOcean ($200 Free Credit)

**Sign Up:**
1. Visit: https://www.digitalocean.com/
2. Sign up with email
3. Verify email address
4. Add payment method (required for free credit)
5. Claim $200 free credit (valid 60 days)

**Get API Token:**
1. Go to: https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: "Indian Kanoon Scraper"
4. Check "Write" scope
5. Copy token (save immediately - shown once!)

**Pricing:** $5/month per VM (s-1vcpu-1gb droplet)

---

### 2. Vultr ($100 Free Credit)

**Sign Up:**
1. Visit: https://www.vultr.com/
2. Sign up with email
3. Verify email
4. Add payment method
5. Claim $100 free credit (valid 30 days)

**Get API Key:**
1. Go to: https://my.vultr.com/settings/#settingsapi
2. Click "Enable API"
3. Copy API key

**Pricing:** $6/month per VM (1 vCPU, 1GB RAM)

---

### 3. Linode ($100 Free Credit)

**Sign Up:**
1. Visit: https://www.linode.com/
2. Sign up with email
3. Verify email
4. Add payment method
5. Claim $100 free credit (valid 60 days)

**Get Personal Access Token:**
1. Go to: https://cloud.linode.com/profile/tokens
2. Click "Create a Personal Access Token"
3. Label: "Indian Kanoon Scraper"
4. Set expiry: Never
5. Check all permissions
6. Copy token

**Pricing:** $5/month per VM (Nanode 1GB)

---

### 4. Oracle Cloud (Always Free Tier)

**Sign Up:**
1. Visit: https://www.oracle.com/cloud/free/
2. Sign up for free account
3. Verify email and phone
4. Add payment method (not charged for free tier)

**Get API Credentials:**
1. Go to: https://cloud.oracle.com/
2. Profile → User Settings
3. API Keys → Add API Key
4. Download private key (.pem file)
5. Copy User OCID, Tenancy OCID, Fingerprint

**Pricing:** FREE (4 VMs always free: VM.Standard.E2.1.Micro)

---

## 📦 Installation

### 1. Clone Repository

```bash
cd /workspaces/lool-/data-collection
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit `.env` File

```bash
nano .env  # or use your preferred editor
```

### 3. Add Cloud Credentials

```env
# DigitalOcean
DIGITALOCEAN_TOKEN=dop_v1_xxxxxxxxxxxxxxxxxxxx
DIGITALOCEAN_VM_COUNT=15
DIGITALOCEAN_VM_SIZE=s-1vcpu-1gb

# Vultr
VULTR_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VULTR_VM_COUNT=10
VULTR_VM_PLAN=vc2-1c-1gb

# Linode
LINODE_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINODE_VM_COUNT=10
LINODE_VM_TYPE=g6-nanode-1

# Oracle Cloud (optional)
ORACLE_USER_OCID=ocid1.user.oc1..xxxxx
ORACLE_TENANCY_OCID=ocid1.tenancy.oc1..xxxxx
ORACLE_FINGERPRINT=xx:xx:xx:xx:xx
ORACLE_PRIVATE_KEY_PATH=/path/to/oracle_api_key.pem
ORACLE_VM_COUNT=4

# SSH Keys
SSH_PUBLIC_KEY_PATH=~/.ssh/id_rsa.pub
SSH_PRIVATE_KEY_PATH=~/.ssh/id_rsa
```

### 4. Verify Configuration

```bash
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✓ Config loaded')"
```

---

## 🚀 Deployment

### Step 1: Deploy VMs

```bash
python deploy_vms.py
```

**What happens:**
1. ✓ Authenticates with cloud providers
2. ✓ Deploys VMs across multiple regions
3. ✓ Installs Squid proxy on each VM
4. ✓ Configures firewall rules
5. ✓ Saves proxy list to `config/proxy_list.json`

**Expected output:**
```
╔══════════════════════════════════════════════════════════════╗
║       Multi-Cloud Proxy Infrastructure Deployment           ║
╚══════════════════════════════════════════════════════════════╝

Deploying 40 VMs...
✓ Deployed: digitalocean-proxy-1 (165.227.xxx.xxx)
✓ Deployed: vultr-proxy-1 (144.202.xxx.xxx)
...

Successfully deployed: 40/40
Proxies installed: 40/40
```

**Duration:** 10-15 minutes

---

### Step 2: Test Proxies

```bash
python test_proxies.py
```

**What it does:**
- Tests each proxy for connectivity
- Measures response time
- Verifies IP anonymization
- Generates health report

**Output:**
```
Testing 40 proxies...
✓ 165.227.xxx.xxx - 1.23s
✓ 144.202.xxx.xxx - 0.98s

PROXY TEST REPORT
==================
Total Proxies: 40
Working: 38 (95.0%)
Failed: 2 (5.0%)
Avg Response Time: 1.15s
```

---

### Step 3: Estimate Costs

```bash
python estimate_cost.py
```

**Output:**
```
INFRASTRUCTURE COSTS
====================
Total Monthly Cost: $215.00

SCRAPING TIME ESTIMATES
=======================
1.4M documents:
  • Time: 28.5 days
  • Cost: $203.75
  • Completion: 2025-11-19

FREE CREDIT USAGE
=================
Available Credits: $400
Credits will cover: 1.9 months
```

---

### Step 4: Start Scraping

```bash
# Use bulk_download.py with proxies
python bulk_download.py --use-proxies --batch-size 100
```

The scraper will automatically:
- Load proxies from `config/proxy_list.txt`
- Rotate through proxies for each request
- Track failed proxies
- Resume on interruption

---

### Step 5: Monitor Progress

```bash
python dashboard.py
```

Open browser: http://127.0.0.1:5000

**Dashboard Features:**
- 📊 Real-time case count
- 🌐 Proxy health status
- ⏱️ Progress percentage
- 📈 Scraping rate (cases/day)
- 📄 Recent cases
- 📋 Live logs

---

## 💰 Cost Management

### Check Current Usage

```bash
python estimate_cost.py
```

### Monitor Free Credits

**DigitalOcean:**
- Dashboard: https://cloud.digitalocean.com/billing
- $200 credit valid for 60 days

**Vultr:**
- Dashboard: https://my.vultr.com/billing/
- $100 credit valid for 30 days

**Linode:**
- Dashboard: https://cloud.linode.com/account/billing
- $100 credit valid for 60 days

**Oracle:**
- Always free tier (no expiry)

### Set Billing Alerts

**Important:** Set alerts to avoid unexpected charges!

1. DigitalOcean: Set alert at $190
2. Vultr: Set alert at $90
3. Linode: Set alert at $90

---

## 🧹 Cleanup

### Delete All VMs

**IMPORTANT:** Run this when done scraping to avoid charges!

```bash
python cleanup_vms.py
```

**Confirmation required:**
```
⚠️  WARNING: VM DELETION
You are about to DELETE 40 VMs
Type 'DELETE' to confirm:
```

Type `DELETE` and press Enter.

**What happens:**
- Deletes all VMs across all providers
- Removes proxy configuration files
- Frees up all resources

### Verify Deletion

Check each provider's dashboard:
- DigitalOcean: https://cloud.digitalocean.com/droplets
- Vultr: https://my.vultr.com/instances/
- Linode: https://cloud.linode.com/linodes

---

## 🐛 Troubleshooting

### VM Deployment Fails

**Error:** "Authentication failed"
- ✓ Check API token/key is correct
- ✓ Verify token has write permissions
- ✓ Check account is verified

**Error:** "SSH connection timeout"
- ✓ Wait 1-2 minutes for VM to fully boot
- ✓ Check SSH key path in `.env`
- ✓ Verify firewall allows port 22

### Proxy Not Working

**Error:** "Connection refused"
- ✓ Check Squid is running: `systemctl status squid`
- ✓ Verify firewall allows port 3128
- ✓ Test manually: `curl -x http://IP:3128 http://ifconfig.me`

**Low success rate (<90%)**
- ✓ Run `python test_proxies.py` again
- ✓ Delete failed VMs and redeploy
- ✓ Check provider status pages

### Scraping Too Slow

- ✓ Deploy more VMs (increase VM_COUNT)
- ✓ Reduce REQUEST_DELAY in `.env`
- ✓ Check proxy response times
- ✓ Use faster regions (US, EU)

### Out of Free Credits

- ✓ Check credit balance on each provider
- ✓ Delete unused VMs immediately
- ✓ Consider switching to Oracle Cloud (always free)
- ✓ Use fewer VMs to reduce costs

---

## 📊 Performance Expectations

### With 40 Proxies

- **Requests per hour:** 72,000
- **Documents per day:** 50,000-60,000
- **PDF downloads per day:** 40,000-50,000
- **Time to complete 1.4M:** 25-30 days
- **Total cost:** $200-250

### Optimization Tips

1. **Increase VMs:** Deploy 60-80 VMs for faster scraping
2. **Reduce delay:** Lower REQUEST_DELAY to 1s (careful!)
3. **Parallel downloads:** Use concurrent PDF downloads
4. **Skip PDFs:** Scrape metadata only first, download PDFs later
5. **Regional focus:** Deploy more VMs in faster regions

---

## 🔒 Security Best Practices

1. **Never commit `.env`** file with real credentials
2. **Use strong SSH keys** (4096-bit RSA minimum)
3. **Rotate API tokens** regularly
4. **Delete VMs** when not in use
5. **Monitor billing** daily
6. **Use firewall rules** on all VMs
7. **Keep software updated** on VMs

---

## 📚 Additional Resources

- [DigitalOcean API Docs](https://docs.digitalocean.com/reference/api/)
- [Vultr API Docs](https://www.vultr.com/api/)
- [Linode API Docs](https://www.linode.com/docs/api/)
- [Oracle Cloud Docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/usingapi.htm)
- [Squid Proxy Documentation](http://www.squid-cache.org/Doc/)

---

## 🆘 Support

If you encounter issues:

1. Check logs: `logs/scraper.log`
2. Review VM status on cloud dashboards
3. Test individual proxy: `curl -x http://IP:3128 http://ifconfig.me`
4. Check proxy test report: `config/proxy_test_report.json`

---

## ✅ Quick Start Checklist

- [ ] Sign up for all cloud providers
- [ ] Get API tokens/keys
- [ ] Generate SSH keys
- [ ] Configure `.env` file
- [ ] Install dependencies
- [ ] Run `python deploy_vms.py`
- [ ] Run `python test_proxies.py`
- [ ] Run `python estimate_cost.py`
- [ ] Start scraping with proxies
- [ ] Monitor with `python dashboard.py`
- [ ] **Clean up with `python cleanup_vms.py` when done!**

---

## 🎉 Success Metrics

**Goal:** Scrape 1.4M legal documents within budget

- ✅ 40+ proxies deployed
- ✅ 90%+ proxy success rate
- ✅ 50K+ documents per day
- ✅ Completion within 30 days
- ✅ Total cost < $400 (free credits)

---

**Happy Scraping! 🚀**
