# Proxy Integration Setup Guide

Complete guide for configuring and using 100 proxy IPs with the IndianKanoon scraper for maximum performance.

---

## Table of Contents

1. [Overview](#overview)
2. [WebShare.io Setup](#webshareio-setup)
3. [Configuration](#configuration)
4. [Worker-to-Proxy Ratios](#worker-to-proxy-ratios)
5. [Usage Examples](#usage-examples)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
8. [Google Cloud Deployment](#google-cloud-deployment)

---

## Overview

### Why Use Proxies?

- **Avoid rate limiting**: Distribute requests across 100 different IP addresses
- **Increase speed**: 10-20x faster downloads with parallel workers
- **Prevent IP bans**: Each proxy handles only a fraction of total requests
- **Scale confidently**: Download thousands of documents without interruption

### Architecture

```
100 Proxies (WebShare.io)
    ↓
Round-Robin Rotation
    ↓
100 Concurrent Workers
    ↓
ThreadPoolExecutor
    ↓
~1,500-2,000 PDFs/min
```

---

## WebShare.io Setup

### Step 1: Create Account

1. Visit https://www.webshare.io/
2. Sign up for a free or paid account
3. Choose plan based on proxy count:
   - **Free**: 10 proxies (limited, for testing)
   - **Starter**: 100 proxies (~$30/month)
   - **Professional**: 1000+ proxies

### Step 2: Get API Key

1. Log in to your account
2. Navigate to: https://proxy.webshare.io/userapi/dashboard
3. Copy your API key (looks like: `abc123def456...`)
4. Keep it secure - treat it like a password!

### Step 3: Verify Proxy List

1. Check "Proxy List" section
2. Verify you have 100 datacenter proxies
3. Note the proxy format: `host:port:username:password`

---

## Configuration

### Method 1: WebShare.io API (Recommended)

Edit `.env` file:

```bash
# Proxy Configuration
WEBSHARE_API_KEY=your_actual_api_key_here
PROXY_ROTATION_STRATEGY=round_robin

# Reduce delay when using proxies
REQUEST_DELAY=0.5
MAX_REQUESTS_PER_SECOND=200.0
```

### Method 2: Proxy File

If you have proxies from another provider:

1. Create `config/proxies.txt`:
```
proxy1.example.com:8080:user1:pass1
proxy2.example.com:8080:user2:pass2
proxy3.example.com:8080:user3:pass3
...
```

2. Edit `.env`:
```bash
PROXY_FILE=./config/proxies.txt
PROXY_ROTATION_STRATEGY=round_robin
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `PROXY_ROTATION_STRATEGY` | `round_robin` | Distribute evenly (recommended) |
|  | `least_used` | Use proxies with fewest requests |
|  | `best_performing` | Use fastest/most reliable proxies |
| `REQUEST_DELAY` | `0.5` - `2.0` | Seconds between requests (lower with proxies) |
| `MAX_REQUESTS_PER_SECOND` | `50` - `200` | Total requests/sec across all workers |

---

## Worker-to-Proxy Ratios

### Recommended Configurations

#### Configuration 1: Balanced (100 Workers, 100 Proxies)
```bash
python bulk_download.py --max-workers 100 --batch-size 100
```

**Performance:**
- Speed: ~1,500-2,000 PDFs/min
- Ratio: 1:1 (1 worker per proxy)
- Safety: High (each proxy handles ~2 requests/sec)
- Download 600 cases: ~20-30 seconds

**Best for:** Maximum speed with balanced load

#### Configuration 2: Conservative (50 Workers, 100 Proxies)
```bash
python bulk_download.py --max-workers 50 --batch-size 50
```

**Performance:**
- Speed: ~750-1,000 PDFs/min
- Ratio: 1:2 (1 worker per 2 proxies)
- Safety: Very high (each proxy handles ~1 request/sec)
- Download 600 cases: ~40-60 seconds

**Best for:** Long-term stability, protecting proxy health

#### Configuration 3: Aggressive (150 Workers, 100 Proxies)
```bash
python bulk_download.py --max-workers 150 --batch-size 100
```

**Performance:**
- Speed: ~2,000-2,500 PDFs/min
- Ratio: 1.5:1 (1.5 workers per proxy)
- Safety: Medium (each proxy handles ~3 requests/sec)
- Download 600 cases: ~15-20 seconds

**Best for:** One-time large downloads, can risk some proxy failures

---

## Usage Examples

### Basic Usage with Proxies

```bash
# 1. Set your API key in .env
export WEBSHARE_API_KEY=your_api_key_here

# 2. Test proxy integration
python test_proxy_integration.py

# 3. Run with 100 workers
python bulk_download.py --max-workers 100
```

### Advanced Usage

```bash
# Custom worker count and batch size
python bulk_download.py --max-workers 75 --batch-size 50

# With checkpoint intervals
python bulk_download.py --max-workers 100 --checkpoint-interval 200

# View statistics during run
tail -f logs/bulk_download_*.log
```

### Testing Progressive Scale-Up

```bash
# Step 1: Test with 20 workers (baseline)
python bulk_download.py --max-workers 20

# Step 2: Scale to 50 workers
python bulk_download.py --max-workers 50

# Step 3: Full scale 100 workers
python bulk_download.py --max-workers 100
```

---

## Performance Tuning

### Optimal Settings for 100 Proxies

```bash
# .env configuration
REQUEST_DELAY=0.5
MAX_REQUESTS_PER_SECOND=200.0
PROXY_ROTATION_STRATEGY=round_robin

# Command line
python bulk_download.py --max-workers 100 --batch-size 100
```

### Performance Comparison

| Workers | Proxies | Speed (PDFs/min) | Time for 600 cases |
|---------|---------|------------------|--------------------|
| 1 | 0 | 30 | ~20 min |
| 20 | 0 | 300 | ~2 min |
| 50 | 100 | 750-1,000 | ~40-60 sec |
| 100 | 100 | 1,500-2,000 | ~20-30 sec |
| 150 | 100 | 2,000-2,500 | ~15-20 sec |

### Rate Limit Guidelines

**Per Proxy:**
- Conservative: 1-2 requests/second
- Balanced: 2-3 requests/second
- Aggressive: 3-5 requests/second

**Total (100 proxies):**
- Conservative: 100-200 requests/second
- Balanced: 200-300 requests/second
- Aggressive: 300-500 requests/second

---

## Monitoring & Troubleshooting

### Real-Time Monitoring

```bash
# Watch download progress
tail -f logs/bulk_download_*.log

# Monitor proxy statistics
grep "PROXY POOL STATISTICS" logs/bulk_download_*.log -A 20
```

### Proxy Statistics Output

After each run, you'll see:

```
================================================================================
PROXY POOL STATISTICS
================================================================================
Total Proxies: 100
Active: 98 | Inactive: 2
Average Success Rate: 98.5%
Average Response Time: 0.85s
Total Requests: 15,234
Total Failures: 156
================================================================================

Top 5 Performing Proxies:
  1. 192.168.1.10:8080 (success: 99.8%, avg_time: 0.42s)
  2. 192.168.1.11:8080 (success: 99.6%, avg_time: 0.45s)
  3. 192.168.1.12:8080 (success: 99.4%, avg_time: 0.48s)
  4. 192.168.1.13:8080 (success: 99.2%, avg_time: 0.51s)
  5. 192.168.1.14:8080 (success: 99.0%, avg_time: 0.53s)
```

### Common Issues

#### Issue 1: Proxies Not Loading

```bash
# Error: "No proxy configuration found"
# Fix: Check .env has WEBSHARE_API_KEY set
grep WEBSHARE_API_KEY .env

# Verify API key is valid
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('WEBSHARE_API_KEY'))"
```

#### Issue 2: High Failure Rate

```bash
# Symptoms: "Average Success Rate: <90%"
# Fix 1: Reduce workers
python bulk_download.py --max-workers 50

# Fix 2: Increase delay
# Edit .env: REQUEST_DELAY=1.0
```

#### Issue 3: Proxies Getting Banned

```bash
# Symptoms: Many proxies inactive
# Fix: Use best_performing strategy (auto-avoids bad proxies)
# Edit .env: PROXY_ROTATION_STRATEGY=best_performing
```

#### Issue 4: Slow Performance

```bash
# Fix 1: Switch to round_robin (fastest)
# Edit .env: PROXY_ROTATION_STRATEGY=round_robin

# Fix 2: Reduce REQUEST_DELAY
# Edit .env: REQUEST_DELAY=0.3
```

---

## Google Cloud Deployment

### Recommended Instance Configuration

For optimal performance with 100 workers:

```bash
# Instance type: e2-standard-4
# - vCPUs: 4
# - Memory: 16 GB
# - Cost: ~$120/month (~$0.17/hour)
# - Network: Up to 16 Gbps

# Estimated bandwidth usage:
# 100 workers × 300 KB/PDF × 20 PDFs/sec = ~60 MB/s
```

### Setup Script for Google Cloud

```bash
#!/bin/bash
# deploy_to_gcloud.sh

# 1. Create VM
gcloud compute instances create indiankanoon-scraper \
    --machine-type=e2-standard-4 \
    --zone=us-central1-a \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB

# 2. SSH into instance
gcloud compute ssh indiankanoon-scraper --zone=us-central1-a

# 3. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip git docker.io docker-compose

# 4. Clone repository
git clone <your-repo-url>
cd data-collection

# 5. Setup environment
cp .env.example .env
nano .env  # Add your WEBSHARE_API_KEY

# 6. Install Python packages
pip3 install -r requirements.txt

# 7. Start PostgreSQL
docker-compose up -d postgres

# 8. Run scraper
python3 bulk_download.py --max-workers 100
```

### Cost Estimation

**For 600 cases with 100 workers:**

| Resource | Usage | Cost |
|----------|-------|------|
| Compute (e2-standard-4) | ~1 minute | $0.003 |
| Network egress | ~180 MB | $0.001 |
| Storage | 180 MB | $0.000 |
| **Total** | - | **~$0.004** |

**For 10,000 cases:**
- Time: ~5-10 minutes
- Cost: ~$0.05
- Well within $300 free credit!

---

## Best Practices

### Do's ✓

1. **Start small**: Test with 20 workers before scaling to 100
2. **Monitor logs**: Watch for error patterns
3. **Use round_robin**: Most balanced for equal proxy usage
4. **Set REQUEST_DELAY=0.5**: Safe with proxies
5. **Check proxy health**: Run health checks periodically

### Don'ts ✗

1. **Don't start at 150 workers**: May overwhelm proxies
2. **Don't use delay < 0.3s**: Too aggressive, risks bans
3. **Don't ignore failure rates**: >10% failures = slow down
4. **Don't commit API keys**: Keep .env in .gitignore
5. **Don't skip testing**: Always test before full deployment

---

## Quick Reference

### Test Proxy Setup

```bash
python test_proxy_integration.py
```

### Run with Proxies

```bash
# Balanced (recommended)
python bulk_download.py --max-workers 100

# Conservative
python bulk_download.py --max-workers 50

# Aggressive
python bulk_download.py --max-workers 150
```

### Check Proxy Status

```bash
# View recent logs
tail -100 logs/bulk_download_*.log

# Count active proxies
grep "Active:" logs/bulk_download_*.log | tail -1
```

### Update Configuration

```bash
# Edit environment
nano .env

# Reload and test
python test_proxy_integration.py
```

---

## Support & Resources

- **WebShare.io Docs**: https://docs.webshare.io/
- **WebShare.io Support**: https://proxy.webshare.io/support
- **Issue Tracker**: [GitHub Issues](your-repo-issues-url)

---

## Summary

With 100 proxy IPs from WebShare.io:

- **Optimal configuration**: 100 workers (1:1 ratio)
- **Expected speed**: 1,500-2,000 PDFs/min
- **Download 600 cases**: ~20-30 seconds
- **Cost on Google Cloud**: <$0.01 per run
- **Stability**: 98%+ success rate with proper configuration

**Ready to deploy!** 🚀
