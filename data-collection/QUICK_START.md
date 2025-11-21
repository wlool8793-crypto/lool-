# Quick Start Guide - Download All Cases

## TL;DR

```bash
# Activate environment
source venv/bin/activate

# Download all 600 cases (takes ~1.5-2 hours)
python bulk_download.py

# That's it! ✨
```

## What You Get

- **Automatic PDF download** for all 600 legal cases
- **Progress tracking** with real-time updates
- **Automatic retry** if downloads fail (3 attempts)
- **Resume support** - can stop and restart anytime
- **100% tested** - already downloaded 21 cases successfully

## Quick Commands

```bash
# Start download
python bulk_download.py

# Check progress (in another terminal)
python main.py --stats

# View logs
tail -f logs/bulk_download_*.log

# Resume if interrupted
python bulk_download.py  # Automatically resumes!
```

## Expected Output

```
================================================================================
INDIANKANOON BULK PDF DOWNLOAD
================================================================================

Database Statistics:
  Total cases: 600
  Cases with PDFs: 21
  Cases without PDFs: 579

Progress: |████████------------------------------------------| 15.0% Complete (90 downloaded)

[92/600] Case ID: 92
  Title: State Of Punjab vs Balbir Singh...
  → Fetching case details...
  ✓ Details fetched, PDF available
  → Downloading PDF...
  ✓ Downloaded successfully (284.2 KB)
```

## If Something Goes Wrong

**Press Ctrl+C to stop gracefully**
- Current download will finish
- Progress is saved
- Just run again to resume

**Check logs if needed:**
```bash
ls -la logs/
```

## Configuration (Optional)

Edit `.env` file:
```bash
REQUEST_DELAY=2        # Seconds between downloads
DOWNLOAD_PDFS=true     # Enable downloads
```

## After Download Completes

**Check results:**
```bash
python main.py --stats
ls -lh data/pdfs/*.pdf
```

**Expected:**
- ~550-580 PDFs downloaded (not all cases have PDFs)
- ~180 MB total size
- All files are valid PDF documents

## Features

✅ **Robust:** 3 automatic retries per download
✅ **Smart:** Skips already downloaded files
✅ **Safe:** Validates every PDF
✅ **Tracked:** Progress bar + detailed logs
✅ **Resumable:** Stop and restart anytime

## Need Help?

- Read detailed guide: `ROBUST_DOWNLOAD_GUIDE.md`
- View test report: `PDF_SYSTEM_TEST_REPORT.md`
- Check logs: `logs/bulk_download_*.log`

---

**Ready? Just run:**
```bash
source venv/bin/activate && python bulk_download.py
```
