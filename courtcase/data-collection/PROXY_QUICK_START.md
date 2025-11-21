# Proxy Integration - Quick Start Guide

**Get up and running with 100 proxies in 5 minutes!**

---

## Step 1: Get WebShare.io Account (2 minutes)

1. Go to: https://www.webshare.io/
2. Sign up for account
3. Choose plan:
   - **Free**: 10 proxies (testing only)
   - **Starter**: 100 proxies (~$30/month) ⭐ RECOMMENDED
4. Navigate to: https://proxy.webshare.io/userapi/dashboard
5. Copy your API key (looks like: `abc123def456...`)

---

## Step 2: Configure Environment (1 minute)

Edit `/workspaces/lool-/data-collection/.env`:

```bash
# Add your API key
WEBSHARE_API_KEY=paste_your_api_key_here

# Optional: Adjust settings
PROXY_ROTATION_STRATEGY=round_robin
REQUEST_DELAY=0.5
MAX_REQUESTS_PER_SECOND=200.0
```

---

## Step 3: Test Integration (1 minute)

```bash
cd /workspaces/lool-/data-collection
python3 test_proxy_integration.py
```

**Expected output:**
```
✓ Created proxy manager with 100 proxies loaded
✓ Rotation Strategy: round_robin
```

---

## Step 4: Run Download (1 minute)

```bash
# Start with 20 workers (safe test)
python3 bulk_download.py --max-workers 20

# If successful, scale to 100 workers
python3 bulk_download.py --max-workers 100
```

---

## Performance Reference

| Workers | Speed | Time (600 cases) |
|---------|-------|------------------|
| 20 | 300/min | 2 min |
| 50 | 1,000/min | 36 sec |
| 100 | 2,000/min | 18 sec |

---

## Common Commands

```bash
# Test proxy setup
python3 test_proxy_integration.py

# Run with 100 workers (recommended)
python3 bulk_download.py --max-workers 100

# Conservative run (50 workers)
python3 bulk_download.py --max-workers 50

# Check logs
tail -f logs/bulk_download_*.log

# View proxy stats
grep "PROXY POOL" logs/bulk_download_*.log -A 10
```

---

## Troubleshooting

**Problem: "No proxies loaded"**
```bash
# Solution: Check API key
grep WEBSHARE_API_KEY .env
```

**Problem: High failure rate (>10%)**
```bash
# Solution: Reduce workers
python3 bulk_download.py --max-workers 50
```

**Problem: Slow performance**
```bash
# Solution: Reduce delay in .env
REQUEST_DELAY=0.3
```

---

## Full Documentation

- **Complete setup guide**: `PROXY_SETUP_GUIDE.md`
- **Implementation details**: `PROXY_INTEGRATION_SUMMARY.md`
- **Test suite**: `test_proxy_integration.py`

---

**Ready to download at 2,000 PDFs/min!** 🚀
