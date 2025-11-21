# Multi-Cloud Proxy - Quick Start Guide
## Get 40+ Proxies Running in 15 Minutes

---

## 🚀 Super Quick Setup (5 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
nano .env  # Add your API tokens

# 3. Deploy VMs (10-15 min)
python deploy_vms.py

# 4. Test proxies
python test_proxies.py

# 5. Start scraping!
python bulk_download.py --use-proxies
```

---

## 📝 Minimal Configuration

Edit `.env` and add just these (others optional):

```env
# DigitalOcean (Required - $200 free credit)
DIGITALOCEAN_TOKEN=your_token_here

# Vultr (Optional but recommended - $100 free credit)
VULTR_API_KEY=your_key_here

# SSH Keys (will use defaults if not specified)
# SSH_PUBLIC_KEY_PATH=~/.ssh/id_rsa.pub
# SSH_PRIVATE_KEY_PATH=~/.ssh/id_rsa
```

---

## 🎯 Where to Get API Tokens

| Provider | Free Credit | Get Token URL |
|----------|------------|---------------|
| DigitalOcean | $200 (60 days) | https://cloud.digitalocean.com/account/api/tokens |
| Vultr | $100 (30 days) | https://my.vultr.com/settings/#settingsapi |
| Linode | $100 (60 days) | https://cloud.linode.com/profile/tokens |
| Oracle | Free Forever | https://cloud.oracle.com/ (more complex setup) |

---

## ✅ Pre-Flight Checklist

Before running `deploy_vms.py`:

- [ ] Python 3.10+ installed
- [ ] `pip install -r requirements.txt` completed
- [ ] `.env` file created with at least `DIGITALOCEAN_TOKEN`
- [ ] SSH keys exist at `~/.ssh/id_rsa` (or custom path in `.env`)
- [ ] Cloud provider account verified
- [ ] Payment method added (for free credits)

---

## 🎮 Command Cheat Sheet

```bash
# Deploy all VMs
python deploy_vms.py

# Test proxy health
python test_proxies.py

# Estimate costs and time
python estimate_cost.py

# Start monitoring dashboard
python dashboard.py  # Open http://127.0.0.1:5000

# Start scraping with proxies
python bulk_download.py --use-proxies --batch-size 100

# IMPORTANT: Cleanup when done!
python cleanup_vms.py
```

---

## 📊 What You'll Get

### Default Setup (DigitalOcean + Vultr)

- **25 proxy servers** across multiple regions
- **~50K documents/day** scraping rate
- **~28 days** to complete 1.4M documents
- **$165/month** cost (covered by $300 free credits)

### Full Setup (All 4 Providers)

- **39 proxy servers** globally distributed
- **~80K documents/day** scraping rate
- **~18 days** to complete 1.4M documents
- **$215/month** cost (covered by $400 free credits)

---

## ⚡ After Deployment

### Check Everything Works

```bash
# 1. Verify proxies deployed
ls config/proxy_list.json

# 2. Test proxies
python test_proxies.py

# 3. Check costs
python estimate_cost.py
```

### Start Scraping

```bash
# Option 1: Use existing bulk_download.py
python bulk_download.py --use-proxies

# Option 2: Direct integration (if your scraper supports it)
# Proxies are saved in: config/proxy_list.txt
# Format: http://IP:3128 (one per line)
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named X" | Run `pip install -r requirements.txt` |
| "Authentication failed" | Check API token in `.env` is correct |
| "SSH connection timeout" | Wait 2-3 minutes, VMs need time to boot |
| "All proxies failed" | Run `python test_proxies.py` to diagnose |
| "Out of credits" | Run `python cleanup_vms.py` to stop charges |

---

## 💰 Cost Tracking

### Check Your Credits

```bash
python estimate_cost.py
```

### Real-Time Monitoring

```bash
python dashboard.py
# Open: http://127.0.0.1:5000
```

### Provider Dashboards

- DigitalOcean: https://cloud.digitalocean.com/billing
- Vultr: https://my.vultr.com/billing/
- Linode: https://cloud.linode.com/account/billing

---

## 🧹 Cleanup (IMPORTANT!)

### When Scraping is Done

```bash
python cleanup_vms.py
# Type "DELETE" to confirm
```

### What Gets Deleted

- ✓ All VMs across all providers
- ✓ Proxy configuration files
- ✓ No more charges!

### Verify Deletion

Check provider dashboards to ensure all VMs deleted:
- No droplets/instances should remain
- Billing should show $0.00/month

---

## 📈 Expected Timeline

| Step | Duration | Action |
|------|----------|--------|
| Setup | 5 min | Configure .env, install deps |
| Deploy VMs | 10-15 min | `python deploy_vms.py` |
| Test Proxies | 2-3 min | `python test_proxies.py` |
| Start Scraping | Instant | `python bulk_download.py --use-proxies` |
| Monitor | Ongoing | `python dashboard.py` |
| Complete | 18-30 days | Automatic (based on VM count) |
| Cleanup | 2-3 min | `python cleanup_vms.py` |

---

## 🎯 Success Criteria

After running `deploy_vms.py`, you should see:

```
Successfully deployed: 25/25  # Or your configured count
Proxies installed: 25/25
✓ Saved proxy list to config/proxy_list.json
✓ Saved proxy URLs to config/proxy_list.txt
```

After running `test_proxies.py`:

```
Working: 24 (96.0%)  # Should be >90%
Failed: 1 (4.0%)
Avg Response Time: 1.2s  # Should be <3s
```

---

## 💡 Pro Tips

1. **Start small:** Deploy 15-20 VMs first, scale up if needed
2. **Test first:** Always run `test_proxies.py` before scraping
3. **Monitor costs:** Check `estimate_cost.py` daily
4. **Set alerts:** Configure billing alerts on each provider
5. **Clean up fast:** Delete VMs immediately when done

---

## 🔥 Emergency Stop

If something goes wrong:

```bash
# Stop all VMs immediately
python cleanup_vms.py

# This prevents further charges
```

---

## 📚 Need More Help?

- **Full Guide:** See `MULTI_CLOUD_GUIDE.md`
- **Proxy Setup:** See `PROXY_SETUP_GUIDE.md`
- **Main README:** See `README.md`

---

## 🎉 You're Ready!

Now run:

```bash
python deploy_vms.py
```

And watch the magic happen! ✨

---

**Remember:** Run `python cleanup_vms.py` when done! 🧹
