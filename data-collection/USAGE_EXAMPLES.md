# IndianKanoon Production Scraper - Usage Examples

This document provides practical examples for using the production scraper system.

---

## 🎯 Common Workflows

### 1. First Time Setup (Local Development)

```bash
# Install Python dependencies
pip install -r requirements_production.txt

# Create necessary directories
mkdir -p data/temp_pdfs logs config

# Setup Google Drive credentials
# 1. Download credentials.json from Google Cloud Console
# 2. Place in ./config/credentials.json

# Authenticate with Google Drive
python - << 'EOF'
from scraper.drive_manager import DriveManager
import yaml

with open('./config/config_production.yaml', 'r') as f:
    config = yaml.safe_load(f)

dm = DriveManager(config)
if dm.authenticate():
    print("✓ Authentication successful!")
else:
    print("✗ Authentication failed")
EOF
```

### 2. Testing Before Production Run

```bash
# Test URL collection (10 pages only)
python main_scraper.py --mode collect --max-pages 10

# Check what was collected
python main_scraper.py --mode status

# Test download (100 documents)
python main_scraper.py --mode scrape --batch-size 100

# Verify PDFs in temp directory
ls -lh data/temp_pdfs/ | head -20

# Check Google Drive folder
# Go to https://drive.google.com and verify "IndianKanoon_PDFs" folder
```

### 3. Production Run (Full Scale)

```bash
# Step 1: Collect all URLs (~3-6 hours)
python main_scraper.py --mode collect

# Step 2: Monitor progress
python main_scraper.py --mode status

# Step 3: Start downloading (can run multiple times)
python main_scraper.py --mode scrape --batch-size 5000

# Step 4: Resume if interrupted
python main_scraper.py --mode resume

# Step 5: Keep running until complete
while true; do
    python main_scraper.py --mode scrape --batch-size 5000
    sleep 60  # 1 minute pause between batches
done
```

### 4. Running in Background (tmux)

```bash
# Start new tmux session
tmux new -s scraper

# Inside tmux session
cd ~/indiankanoon-scraper
source venv/bin/activate

# Collect URLs
python main_scraper.py --mode collect

# Start scraping
while true; do
    python main_scraper.py --mode scrape --batch-size 5000
    python main_scraper.py --mode status
    sleep 300  # 5 minutes between batches
done

# Detach from tmux: Ctrl+B, then D

# Re-attach later
tmux attach -t scraper

# View session list
tmux list-sessions

# Kill session
tmux kill-session -t scraper
```

---

## 🔍 Monitoring & Debugging

### Check Progress

```bash
# Simple status
python main_scraper.py --mode status

# Watch logs in real-time
tail -f logs/production_scraper.log

# Filter for errors
grep ERROR logs/production_scraper.log | tail -20

# Count downloads
grep "✓ Downloaded:" logs/production_scraper.log | wc -l
```

### Database Queries

```python
# Check database manually
from src.database import CaseDatabase

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')

# Overall progress
progress = db.get_download_progress()
print(f"Total URLs: {progress['total_urls']:,}")
print(f"Downloaded: {progress['pdfs_downloaded']:,}")
print(f"Completion: {progress['completion_rate']:.2f}%")

# Status breakdown
for status, count in progress['status_breakdown'].items():
    print(f"{status}: {count:,}")

# Failed URLs to investigate
from src.database import DownloadStatus
failed = db.get_failed_urls(max_attempts=3, limit=10)
for url in failed:
    print(f"Doc ID: {url.doc_id}")
    print(f"  Attempts: {url.download_attempts}")
    print(f"  Error: {url.error_message}")
    print()
```

### Performance Monitoring

```bash
# System resources
htop

# Disk space
df -h

# Network activity
nethogs

# Process info
ps aux | grep python

# Log download rate
grep "Downloaded:" logs/production_scraper.log | tail -1000 | \
    awk '{print $1, $2}' | uniq -c
```

---

## 🔧 Configuration Adjustments

### Scenario: Getting Rate Limited (429 errors)

```yaml
# config_production.yaml
scraper:
  num_threads: 5  # Reduce from 10
  delay_between_requests: 2.0  # Increase from 0.5
  max_retries: 5  # Increase from 3
```

### Scenario: Maximize Speed (at your own risk)

```yaml
# config_production.yaml
scraper:
  num_threads: 20  # Increase from 10
  delay_between_requests: 0.2  # Decrease from 0.5
  batch_upload_size: 100  # Increase from 50
```

### Scenario: Low Disk Space

```yaml
# config_production.yaml
scraper:
  batch_upload_size: 20  # Upload more frequently

storage:
  min_free_space_gb: 5  # Lower threshold
  auto_cleanup_after_upload: true  # Enable cleanup
```

---

## 📊 Data Analysis After Collection

### Export URLs to CSV

```python
import pandas as pd
from src.database import CaseDatabase

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')

# Get all URLs
from src.database import URLTracker
urls = db.session.query(URLTracker).all()

# Convert to DataFrame
data = []
for url in urls:
    data.append({
        'doc_id': url.doc_id,
        'title': url.title,
        'citation': url.citation,
        'court': url.court,
        'pdf_downloaded': url.pdf_downloaded,
        'uploaded_to_drive': url.uploaded_to_drive,
        'download_status': url.download_status.value if url.download_status else None
    })

df = pd.DataFrame(data)

# Save to CSV
df.to_csv('indiankanoon_dataset.csv', index=False)
print(f"Exported {len(df)} URLs to CSV")

# Statistics
print("\nStatistics:")
print(f"Total URLs: {len(df)}")
print(f"Downloaded: {df['pdf_downloaded'].sum()}")
print(f"Uploaded: {df['uploaded_to_drive'].sum()}")
print("\nBy Court:")
print(df['court'].value_counts())
```

### Generate Statistics Report

```python
from src.database import CaseDatabase
import json

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')
progress = db.get_download_progress()

report = {
    'timestamp': datetime.now().isoformat(),
    'total_urls': progress['total_urls'],
    'pdfs_downloaded': progress['pdfs_downloaded'],
    'uploaded_to_drive': progress['uploaded_to_drive'],
    'completion_rate': progress['completion_rate'],
    'status_breakdown': progress['status_breakdown']
}

# Save report
with open('progress_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Report saved to progress_report.json")
```

---

## 🚨 Troubleshooting Scenarios

### Scenario: Downloads Stuck

```bash
# Check if process is running
ps aux | grep python

# Check logs for errors
tail -50 logs/production_scraper.log

# Check database status
python main_scraper.py --mode status

# Solution: Resume
python main_scraper.py --mode resume
```

### Scenario: Google Drive Quota Exceeded

```python
# Check Drive upload status
from src.database import CaseDatabase

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')
progress = db.get_download_progress()

print(f"PDFs downloaded: {progress['pdfs_downloaded']}")
print(f"Uploaded to Drive: {progress['uploaded_to_drive']}")
print(f"Pending upload: {progress['pdfs_downloaded'] - progress['uploaded_to_drive']}")

# Solution: Wait 24 hours or upgrade Google Drive storage
# Then resume uploads
```

### Scenario: Database Locked

```bash
# Check for multiple processes
ps aux | grep main_scraper.py

# Kill extra processes
kill <PID>

# If still locked, restart
# (Progress is saved, safe to restart)
```

---

## 🎛️ Advanced Usage

### Custom URL Collection (Specific Courts)

```python
from scraper.url_collector import URLCollector
import yaml

# Load config
with open('./config/config_production.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Override search URL for specific court
config['url_collection']['base_search_url'] = \
    "https://indiankanoon.org/search/?formInput=doctype:%20supremecourt%20year:2023"

# Collect
collector = URLCollector(config)
stats = collector.collect_urls()
print(f"Collected {stats['urls_collected']} URLs")
```

### Selective Re-download (Failed Only)

```python
from src.database import CaseDatabase, DownloadStatus

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')

# Get failed URLs
failed = db.get_failed_urls(max_attempts=3, limit=1000)
print(f"Found {len(failed)} failed URLs")

# Reset their status to pending for retry
for url in failed:
    db.update_download_status(
        url.id,
        DownloadStatus.PENDING,
        error_message=None
    )

print("Reset failed URLs to pending. Run scraper to retry.")
```

### Parallel Processing on Multiple VMs

```bash
# VM 1: Process first half
python - << 'EOF'
from src.database import CaseDatabase

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')
urls = db.get_urls_to_download(batch_size=500000)

# Save first half
with open('urls_vm1.json', 'w') as f:
    json.dump(urls[:250000], f)
EOF

# VM 2: Process second half
# (Split URLs and distribute)
```

---

## 📈 Performance Optimization Tips

### 1. Optimize Database

```bash
# For SQLite
sqlite3 data/indiankanoon_production.db "VACUUM;"
sqlite3 data/indiankanoon_production.db "ANALYZE;"

# Consider PostgreSQL for better concurrency
```

### 2. Monitor Network

```bash
# Test download speed
curl -o /dev/null -w "%{speed_download}\n" https://indiankanoon.org/doc/1/

# Monitor bandwidth
iftop
```

### 3. Batch Processing Strategy

```yaml
# For stable long-term execution
scraper:
  num_threads: 8
  batch_size: 2000  # Process 2000 at a time
  delay_between_requests: 1.0
```

---

## 🎓 Learning Examples

### Example 1: Simple Test Run

```bash
# 1. Collect 10 pages of URLs
python main_scraper.py --mode collect --max-pages 10

# 2. Check how many URLs collected
python main_scraper.py --mode status

# 3. Download first 50 PDFs
python main_scraper.py --mode scrape --batch-size 50

# 4. Verify files
ls -lh data/temp_pdfs/ | wc -l
```

### Example 2: Medium Scale Run (1000 documents)

```bash
# Collect URLs (limit to ~100 pages = ~1000 docs)
python main_scraper.py --mode collect --max-pages 100

# Download all
python main_scraper.py --mode scrape

# Check completion
python main_scraper.py --mode status
```

### Example 3: Production Run with Monitoring

```bash
# Terminal 1: Run scraper
tmux new -s scraper
python main_scraper.py --mode collect
python main_scraper.py --mode scrape

# Terminal 2: Monitor progress
watch -n 60 'python main_scraper.py --mode status'

# Terminal 3: Watch logs
tail -f logs/production_scraper.log | grep "Progress:"

# Terminal 4: Monitor system
htop
```

---

## 💡 Pro Tips

1. **Start Small**: Always test with `--max-pages 10` first
2. **Use tmux**: Essential for long-running tasks
3. **Monitor Regularly**: Check status every few hours
4. **Save Logs**: Rotate logs to prevent huge files
5. **Backup Database**: Copy SQLite file periodically
6. **Check Drive Space**: Ensure you have enough Google Drive storage
7. **Rate Limiting**: Start conservative, increase gradually
8. **Resume Often**: Use `--mode resume` to retry failed downloads
9. **Checkpoints**: System auto-saves, but monitor progress
10. **Stay Legal**: Respect ToS and rate limits

---

## 📞 Getting Help

If you encounter issues:

1. Check logs: `tail -100 logs/production_scraper.log`
2. Run status: `python main_scraper.py --mode status`
3. Review README: `README_PRODUCTION.md`
4. Check database: SQLite queries above
5. File issue: GitHub Issues with logs

---

**Happy Scraping! 🚀**
