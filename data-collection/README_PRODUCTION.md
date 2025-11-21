# IndianKanoon Production Scraper

## 🎯 Project Overview

A production-ready web scraping system designed to download **1.4 million+ legal PDF documents** from IndianKanoon.org and store them in Google Drive. Built with Python, Selenium, and the Google Drive API.

### Key Features

- **Massive Scale**: Designed to handle 1.4M+ documents
- **Concurrent Downloads**: Multi-threaded downloading (10-20 workers)
- **Google Drive Integration**: Automatic batch upload with quota management
- **Robust Error Handling**: Automatic retries, graceful degradation
- **Progress Tracking**: SQLite database with comprehensive statistics
- **Resume Capability**: Continue from any interruption
- **Rate Limiting**: Respect server resources, avoid IP bans
- **Checkpoint System**: Never lose progress

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   IndianKanoon.org                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│             URL Collector (Selenium + BS4)                   │
│  • Pagination navigation                                     │
│  • URL extraction                                            │
│  • Checkpoint every 10K URLs                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│            Database (SQLite/PostgreSQL)                      │
│  • URL tracking table                                        │
│  • Download status management                                │
│  • Progress statistics                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│        Download Manager (ThreadPoolExecutor)                 │
│  • 10-20 concurrent workers                                  │
│  • PDF validation                                            │
│  • Automatic retries (3x)                                    │
│  • Rate limiting                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          Drive Manager (Google Drive API)                    │
│  • Batch uploads (50 files/batch)                            │
│  • Quota management                                          │
│  • Local cleanup after upload                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### Local Development
- Python 3.10+
- Google Chrome
- ChromeDriver
- Google Cloud account (for Drive API)

### Production (GCP VM)
- GCP account with billing enabled
- VM: `e2-standard-4` (4 vCPU, 16 GB RAM) recommended
- OS: Ubuntu 22.04 LTS
- Storage: 100 GB SSD
- Estimated cost: $30-60 for complete run

---

## 🚀 Quick Start

### 1. Setup (Local Development)

```bash
# Clone repository
git clone <your-repo-url>
cd data-collection

# Install dependencies
pip install -r requirements_production.txt

# Install Chrome and ChromeDriver
# On Ubuntu:
sudo apt-get install -y chromium-browser chromium-chromedriver

# On macOS:
brew install --cask google-chrome
brew install chromedriver

# Create directories
mkdir -p data/temp_pdfs logs config
```

### 2. Configure Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Desktop app**
6. Download `credentials.json`
7. Place in `./config/credentials.json`

### 3. Configure Settings

Edit `config/config_production.yaml`:

```yaml
scraper:
  num_threads: 10  # Adjust based on your machine
  batch_size: 1000

url_collection:
  max_pages: null  # null = all pages, 10 for testing

google_drive:
  enabled: true
  drive_folder_name: "IndianKanoon_PDFs"
```

### 4. Run

```bash
# Test with limited pages
python main_scraper.py --mode collect --max-pages 10

# Check status
python main_scraper.py --mode status

# Download PDFs (test with 100)
python main_scraper.py --mode scrape --batch-size 100

# Full production run
python main_scraper.py --mode collect  # Collect all URLs (~3-6 hours)
python main_scraper.py --mode scrape   # Download all PDFs (~3-7 days)
```

---

## 📦 GCP Deployment

### Create VM

```bash
gcloud compute instances create indiankanoon-scraper \
  --machine-type=e2-standard-4 \
  --zone=us-central1-a \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud
```

### SSH into VM

```bash
gcloud compute ssh indiankanoon-scraper --zone=us-central1-a
```

### Setup on VM

```bash
# Download repository
git clone <your-repo-url>
cd data-collection

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Upload credentials
# From your local machine:
gcloud compute scp ./config/credentials.json indiankanoon-scraper:~/indiankanoon-scraper/config/

# Authenticate Drive
./run.sh authenticate

# Start scraping in tmux
tmux new -s scraper
./run.sh collect
# Detach: Ctrl+B, then D

# Re-attach to monitor
tmux attach -t scraper
```

---

## 🎮 Usage Guide

### Commands

```bash
# URL Collection
python main_scraper.py --mode collect                    # Collect all URLs
python main_scraper.py --mode collect --max-pages 10     # Test with 10 pages

# PDF Download & Upload
python main_scraper.py --mode scrape                     # Download all pending
python main_scraper.py --mode scrape --batch-size 1000   # Process 1000 docs

# Status & Monitoring
python main_scraper.py --mode status                     # Show progress

# Resume
python main_scraper.py --mode resume                     # Resume failed/pending
```

### Using run.sh Helper Script

```bash
./run.sh collect          # Full collection
./run.sh collect-test     # Test (10 pages)
./run.sh scrape           # Full scrape
./run.sh scrape-test      # Test (100 docs)
./run.sh status           # Show status
./run.sh resume           # Resume downloads
./run.sh authenticate     # Setup Drive auth
```

---

## 📊 Progress Tracking

### View Status

```bash
python main_scraper.py --mode status
```

**Output:**
```
📊 OVERALL PROGRESS
────────────────────────────────────────────────
Total URLs collected: 1,400,000
PDFs downloaded: 450,230
Uploaded to Drive: 450,000
Download completion: 32.16%
Upload completion: 99.95%

📋 STATUS BREAKDOWN
────────────────────────────────────────────────
PENDING        : 949,770
IN_PROGRESS    : 0
COMPLETED      : 450,230
FAILED         : 0
SKIPPED        : 0

⏱️  ESTIMATED COMPLETION
────────────────────────────────────────────────
Remaining documents: 949,770
Estimated time (@ 500 docs/hr): 1,899.5 hours (79.1 days)
```

### Database Queries

```python
from src.database import CaseDatabase

db = CaseDatabase('sqlite:///data/indiankanoon_production.db')

# Get progress
progress = db.get_download_progress()
print(f"Completion: {progress['completion_rate']:.2f}%")

# Get failed URLs
failed = db.get_failed_urls(max_attempts=3, limit=100)
print(f"Failed URLs to retry: {len(failed)}")
```

---

## 🔧 Configuration Reference

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `num_threads` | 10 | Concurrent download workers (8-20) |
| `delay_between_requests` | 0.5 | Seconds between requests |
| `batch_upload_size` | 50 | Files per Drive batch upload |
| `max_retries` | 3 | Download retry attempts |
| `checkpoint_every` | 10000 | URLs per checkpoint save |

### Performance Tuning

**Conservative** (avoid IP ban):
```yaml
num_threads: 8
delay_between_requests: 1.0
```

**Balanced**:
```yaml
num_threads: 10
delay_between_requests: 0.5
```

**Aggressive** (risk IP ban):
```yaml
num_threads: 20
delay_between_requests: 0.2
```

---

## ⚠️ Troubleshooting

### Common Issues

**1. Google Drive Quota Exceeded**
```
Error: quotaExceeded
```
**Solution:** Wait 24 hours or upgrade Google Drive storage

**2. Chrome/ChromeDriver Mismatch**
```
SessionNotCreatedException: session not created
```
**Solution:**
```bash
# Update ChromeDriver
LATEST=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
```

**3. Too Many Errors**
```
WARNING: Too many consecutive errors (10)
```
**Solution:** Check network, reduce threads, increase delays

**4. Database Locked**
```
DatabaseError: database is locked
```
**Solution:** Only run one instance at a time, or switch to PostgreSQL

---

## 📈 Performance Estimates

### Time Estimates

| Configuration | Docs/Hour | Total Time (1.4M docs) |
|---------------|-----------|------------------------|
| Conservative (8 threads, 1s delay) | 400 | 146 days |
| Balanced (10 threads, 0.5s delay) | 500 | 117 days |
| Aggressive (20 threads, 0.2s delay) | 800 | 73 days |

**Actual** production run: ~500-600 docs/hour → **5-7 days continuous**

### Cost Estimates (GCP)

| VM Type | vCPUs | RAM | Cost/Day | Total Cost (7 days) |
|---------|-------|-----|----------|---------------------|
| e2-medium | 2 | 4 GB | $2 | $14 |
| e2-standard-4 | 4 | 16 GB | $5 | $35 |
| n2-standard-8 | 8 | 32 GB | $10 | $70 |

**Recommended:** `e2-standard-4` for balance of speed and cost

### Storage

- Total documents: 1.4M
- Average PDF size: 300 KB
- Total storage: **420 GB**
- Temporary local: 20-50 GB (with batch uploads)

---

## 🔐 Security Best Practices

1. **Never commit credentials**
   ```bash
   # Add to .gitignore
   config/credentials.json
   config/token.pickle
   .env
   ```

2. **Use service accounts** (for production)
3. **Rotate credentials** regularly
4. **Use Secret Manager** for GCP deployments
5. **Enable 2FA** on Google account
6. **Monitor API usage** in GCP Console

---

## 🐛 Debugging

### Enable Debug Logging

```yaml
# config_production.yaml
monitoring:
  log_level: "DEBUG"
```

### View Logs

```bash
# Real-time monitoring
tail -f logs/production_scraper.log

# Search for errors
grep ERROR logs/production_scraper.log

# Count status
grep "Downloaded:" logs/production_scraper.log | wc -l
```

### Database Inspection

```bash
# Open database
sqlite3 data/indiankanoon_production.db

# Count URLs
SELECT COUNT(*) FROM url_tracker;

# Check status distribution
SELECT download_status, COUNT(*) FROM url_tracker GROUP BY download_status;

# Find errors
SELECT doc_id, error_message FROM url_tracker WHERE download_status = 'FAILED' LIMIT 10;
```

---

## 🧪 Testing

### Unit Tests (TODO)

```bash
pytest tests/
```

### Integration Test

```bash
# Test URL collection (10 pages)
python main_scraper.py --mode collect --max-pages 10

# Test download (100 docs)
python main_scraper.py --mode scrape --batch-size 100

# Verify Drive upload
# Check Google Drive folder for uploaded files
```

---

## 📚 API Reference

### URL Collector

```python
from scraper.url_collector import URLCollector

collector = URLCollector(config)
stats = collector.collect_urls(start_page=0)
urls = collector.get_collected_urls()
```

### Drive Manager

```python
from scraper.drive_manager import DriveManager

drive = DriveManager(config)
drive.authenticate()
result = drive.upload_batch(file_paths, court="Supreme Court", year=2023)
drive.delete_local_files(file_paths)
```

### Download Manager

```python
from scraper.download_manager import DownloadManager

manager = DownloadManager(config, drive_manager)
result = manager.download_pdfs(urls)
stats = manager.get_stats()
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is for educational and research purposes. Ensure compliance with IndianKanoon.org terms of service.

---

## ⚖️ Legal & Ethical Considerations

- **Purpose:** This tool is designed for legitimate legal research and academic purposes
- **Rate Limiting:** Built-in delays respect server resources
- **Robots.txt:** Review and respect IndianKanoon's robots.txt
- **Terms of Service:** Ensure compliance with IndianKanoon.org ToS
- **Public Data:** IndianKanoon provides public legal documents
- **Attribution:** Credit IndianKanoon.org when using the data

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation:** This README and inline code comments
- **Logs:** Check `./logs/production_scraper.log`

---

## 🎉 Acknowledgments

- [IndianKanoon.org](https://indiankanoon.org) - Source of legal documents
- [Google Drive API](https://developers.google.com/drive) - Storage solution
- [Selenium](https://www.selenium.dev/) - Web automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

---

**Built with ❤️ for the Indian legal research community**
