# IndianKanoon Scraper - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### Prerequisites
- Python 3.10+
- Chrome browser
- Google account (for Drive API)
- 100 GB free disk space

---

## 🚀 Local Development (Test)

### Step 1: Install Dependencies (2 minutes)

```bash
cd data-collection
pip install -r requirements_production.txt
```

### Step 2: Setup Google Drive (3 minutes)

1. Go to https://console.cloud.google.com/
2. Create new project → Enable "Google Drive API"
3. Credentials → Create OAuth 2.0 Client ID → Desktop app
4. Download `credentials.json`
5. Place in `./config/credentials.json`

### Step 3: Test Run (5 minutes)

```bash
# Test URL collection (10 pages = ~100 URLs)
python main_scraper.py --mode collect --max-pages 10

# Check status
python main_scraper.py --mode status

# Test download (50 PDFs)
python main_scraper.py --mode scrape --batch-size 50
```

**Done!** Check `./data/temp_pdfs/` for downloaded files and Google Drive for uploads.

---

## 🌐 GCP Production Deployment (20 minutes)

### Step 1: Create VM (5 minutes)

```bash
gcloud compute instances create indiankanoon-scraper \
  --machine-type=e2-standard-4 \
  --zone=us-central1-a \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud

# SSH into VM
gcloud compute ssh indiankanoon-scraper --zone=us-central1-a
```

### Step 2: Setup (10 minutes)

```bash
# Clone repository
git clone <your-repo> indiankanoon-scraper
cd indiankanoon-scraper

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate environment
source venv/bin/activate
```

### Step 3: Configure (3 minutes)

```bash
# Upload credentials from local machine
# On your LOCAL machine:
gcloud compute scp ./config/credentials.json \
  indiankanoon-scraper:~/indiankanoon-scraper/config/

# Back on VM, authenticate Drive
./run.sh authenticate
```

### Step 4: Production Run (2 minutes to start)

```bash
# Start tmux session
tmux new -s scraper

# Inside tmux:
./run.sh collect          # ~3-6 hours
./run.sh scrape           # ~5-7 days

# Detach: Ctrl+B, then D
```

### Step 5: Monitor

```bash
# Re-attach to session
tmux attach -t scraper

# Check status (from another SSH session)
./run.sh status

# Watch logs
tail -f logs/production_scraper.log
```

**Running!** System will download 1.4M PDFs to Google Drive over 5-7 days.

---

## 📊 Quick Commands

```bash
# URL Collection
./run.sh collect          # Full collection
./run.sh collect-test     # Test (10 pages)

# PDF Download
./run.sh scrape           # Full scrape
./run.sh scrape-test      # Test (100 docs)

# Monitoring
./run.sh status           # Show progress
tail -f logs/production_scraper.log  # Watch logs

# Resume
./run.sh resume           # Retry failed downloads
```

---

## 🔧 Configuration

Edit `config/config_production.yaml`:

```yaml
scraper:
  num_threads: 10           # 8-20 workers
  delay_between_requests: 0.5  # 0.5-2.0 seconds
  batch_upload_size: 50     # Files per batch

url_collection:
  max_pages: null           # null = all, 10 for testing

google_drive:
  enabled: true
  drive_folder_name: "IndianKanoon_PDFs"
```

---

## ✅ Verification

After test run:

```bash
# Check collected URLs
python main_scraper.py --mode status

# Check downloaded PDFs
ls -lh data/temp_pdfs/ | wc -l

# Check Google Drive
# Go to https://drive.google.com
# Verify folder "IndianKanoon_PDFs" exists

# Check database
sqlite3 data/indiankanoon_production.db \
  "SELECT download_status, COUNT(*) FROM url_tracker GROUP BY download_status;"
```

---

## ⚠️ Troubleshooting

**Chrome not found:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser chromium-chromedriver

# macOS
brew install --cask google-chrome
brew install chromedriver
```

**Drive authentication failed:**
```bash
# Re-authenticate
./run.sh authenticate

# Check credentials
ls -l config/credentials.json
```

**Downloads not starting:**
```bash
# Check pending URLs
python main_scraper.py --mode status

# Resume
./run.sh resume
```

---

## 📚 Full Documentation

- **Complete Guide:** `README_PRODUCTION.md`
- **Usage Examples:** `USAGE_EXAMPLES.md`
- **Project Overview:** `PROJECT_SUMMARY.md`

---

## 🎯 Success Checklist

- [  ] Dependencies installed
- [  ] credentials.json in place
- [  ] Drive authentication successful
- [  ] Test run completed (10 pages)
- [  ] PDFs downloaded successfully
- [  ] Files uploaded to Drive
- [  ] Production run started
- [  ] Monitoring setup (tmux/logs)

---

**Ready to collect 1.4M legal documents! 🚀**

**Estimated Timeline:**
- Setup: 20-30 minutes
- URL Collection: 3-6 hours
- PDF Download: 5-7 days
- **Total:** ~7 days end-to-end

**Estimated Cost:**
- GCP e2-standard-4: $5/day × 7 = **$35**
- Google Drive: Free (if under plan limit)
- **Total:** ~$35

---

**Need help?** Check `README_PRODUCTION.md` or logs at `logs/production_scraper.log`
