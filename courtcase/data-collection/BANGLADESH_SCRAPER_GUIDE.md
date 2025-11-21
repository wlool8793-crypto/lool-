# Bangladesh Laws Scraper - Complete Guide

**Status:** ✅ READY TO USE
**Created:** October 21, 2025
**Architecture:** Unified Multi-Country Legal Scraper

---

## 🎯 What Was Built

A complete **unified multi-country legal document scraping framework** with:

### ✅ Core Infrastructure (100% Complete)

1. **Unified Database Schema** - Single database supporting all countries
2. **Base Scraper Framework** - Abstract class for all country scrapers
3. **Base Parser Utilities** - Common HTML parsing functions
4. **Bangladesh Laws Scraper** - Fully functional scraper for bdlaws.minlaw.gov.bd
5. **Unified CLI Tool** - Command-line interface for all operations
6. **Configuration System** - YAML-based country configs

---

## 📊 Architecture Overview

```
Unified Multi-Country Legal Scraper
│
├── Database Layer
│   ├── legal_documents (unified table)
│   ├── document_metadata (flexible storage)
│   └── Views & indexes
│
├── Base Framework
│   ├── BaseLegalScraper (abstract class)
│   ├── BaseParser (HTML utilities)
│   └── UnifiedDatabase (data layer)
│
├── Country Scrapers
│   ├── BangladeshLawsScraper ✅ COMPLETE
│   └── IndiaKanoonScraper ⏳ Coming Soon
│
└── CLI Interface
    └── unified_scraper.py ✅ READY
```

---

## 🚀 Quick Start - Scrape Bangladesh Laws

### 1. Verify Setup

```bash
# Test configuration
python unified_scraper.py test
```

**Expected output:**
```
🧪 Testing scraper configuration...

1. Testing database connection...
   ✓ Database OK (600 documents)

2. Testing Bangladesh configuration...
   ✓ Config loaded: Bangladesh Laws
   ✓ Base URL: http://bdlaws.minlaw.gov.bd

3. Testing website connectivity...
   ✓ Bangladesh Laws website is accessible

✅ Test complete!
```

### 2. Start Scraping

```bash
# Scrape all Bangladesh laws
python unified_scraper.py scrape --country bangladesh
```

**What it does:**
1. ✅ Scrapes chronological index (all laws by year)
2. ✅ Scrapes alphabetical index (validation/completeness)
3. ✅ Parses each law page
4. ✅ Extracts: title, year, type, ministry, full text
5. ✅ Downloads PDFs if available
6. ✅ Saves to unified database

**Progress output:**
```
======================================================================
Unified Multi-Country Legal Scraper
======================================================================

🇧🇩 Scraping Bangladesh Laws...
INFO - Starting bangladesh legal document scraper
INFO - Getting document list...
INFO - Scraping chronological index...
INFO - Found 1234 laws in chronological index
INFO - Scraping alphabetical index...
INFO - Found 1234 laws in alphabetical index
INFO - Total unique laws: 1234

INFO - Processing 1/1234: http://bdlaws.minlaw.gov.bd/act-1.html
INFO - Processing 2/1234: http://bdlaws.minlaw.gov.bd/act-2.html
...
```

### 3. View Statistics

```bash
# Overall stats
python unified_scraper.py stats

# Bangladesh-specific stats
python unified_scraper.py stats --country bangladesh

# Detailed stats with recent documents
python unified_scraper.py stats --country bangladesh --detailed
```

---

## 📋 CLI Commands Reference

### `scrape` - Start Scraping

```bash
# Scrape Bangladesh
python unified_scraper.py scrape --country bangladesh

# Resume interrupted scraping
python unified_scraper.py scrape --country bangladesh --resume

# Future: Scrape all countries
python unified_scraper.py scrape --country all
```

**Options:**
- `--country` - bangladesh, india, or all
- `--resume` - Resume from previous session (skips already scraped)
- `--limit` - Limit number of documents

### `stats` - View Statistics

```bash
# Overall stats
python unified_scraper.py stats

# Country-specific
python unified_scraper.py stats --country bangladesh

# Detailed with recent docs
python unified_scraper.py stats --detailed
```

### `search` - Search Documents

```bash
# Search all documents
python unified_scraper.py search "constitution"

# Search within Bangladesh only
python unified_scraper.py search "penal code" --country bangladesh
```

### `info` - System Information

```bash
python unified_scraper.py info
```

Shows:
- Database path and size
- Available countries
- Output directories
- Configuration files

### `test` - Test Setup

```bash
python unified_scraper.py test
```

Tests:
- Database connectivity
- Configuration loading
- Website accessibility

---

## 🗄️ Database Schema

### Main Table: `legal_documents`

All countries use the same unified schema:

```sql
legal_documents (
    id,
    country,              -- 'bangladesh', 'india', etc.
    country_doc_id,       -- Country-specific ID
    title,
    doc_type,             -- Act, Case, Ordinance, etc.
    year,
    court_or_ministry,    -- Court (India) or Ministry (Bangladesh)
    source_url,
    source_site,
    html_content,
    plain_text,
    pdf_url,
    pdf_downloaded,
    scraped_at,
    ...
)
```

### Query Examples

```sql
-- All Bangladesh laws
SELECT * FROM legal_documents WHERE country = 'bangladesh';

-- Acts from 2020 onwards
SELECT title, year FROM legal_documents
WHERE country = 'bangladesh' AND year >= 2020;

-- Count by document type
SELECT doc_type, COUNT(*) FROM legal_documents
WHERE country = 'bangladesh'
GROUP BY doc_type;

-- Search by title
SELECT * FROM legal_documents
WHERE country = 'bangladesh' AND title LIKE '%Penal%';

-- Stats view
SELECT * FROM country_stats WHERE country = 'bangladesh';
```

---

## 📂 Output Structure

After scraping, you'll have:

```
data-collection/
├── data/
│   ├── indiankanoon.db           # Unified database
│   ├── pdfs/
│   │   └── bangladesh/           # Bangladesh PDFs
│   │       ├── bangladesh_1_abc123.pdf
│   │       ├── bangladesh_2_def456.pdf
│   │       └── ...
│   └── html/
│       └── bangladesh/           # Bangladesh HTML
│           ├── bangladesh_act-1.html
│           ├── bangladesh_act-2.html
│           └── ...
│
└── logs/
    └── scraper.log               # Scraping logs
```

---

## 🔧 Configuration

### Bangladesh Configuration (`config/bangladesh.yaml`)

```yaml
country: bangladesh
name: "Bangladesh Laws"
base_url: "http://bdlaws.minlaw.gov.bd"

indexes:
  chronological: "/laws-of-bangladesh-chronological-index.html"
  alphabetical: "/laws-of-bangladesh-alphabetical-index.html"

request_delay: 2
use_selenium: false
download_pdfs: true

pdf_dir: "./data/pdfs/bangladesh"
html_dir: "./data/html/bangladesh"

estimated_total: 1500
```

### Customization

**To change scraping speed:**
```yaml
request_delay: 1  # Faster (be careful!)
request_delay: 3  # Slower (more respectful)
```

**To disable PDF downloads:**
```yaml
download_pdfs: false
```

---

## 📈 Expected Results

### Bangladesh Laws Website

**Estimated Content:**
- **~1,500 legal documents**
- Acts, Ordinances, Presidential Orders, Codes
- Coverage: 1947 - Present
- Mix of HTML pages and PDFs

**Scraping Time:**
- With 2-second delay: ~50 minutes for all pages
- PDF downloads: Additional time depending on size
- **Total: 1-2 hours for complete scraping**

### Database After Scraping

```sql
SELECT * FROM country_stats WHERE country = 'bangladesh';
```

**Expected:**
```
country:      bangladesh
total_docs:   ~1500
pdfs_downloaded: ~800-1000 (varies by availability)
doc_types:    4-6 (Act, Ordinance, etc.)
years_covered: 70+ (1947-2025)
```

---

## 🛠️ Technical Details

### What the Bangladesh Scraper Does

1. **Index Scraping**
   - Fetches chronological index
   - Fetches alphabetical index
   - Extracts all law URLs
   - Removes duplicates

2. **Document Parsing**
   - Fetches individual law pages
   - Extracts title (multiple fallback methods)
   - Extracts year from title/content
   - Determines document type (Act vs Ordinance vs Order)
   - Extracts act number/citation
   - Finds responsible ministry
   - Extracts full text content
   - Looks for PDF download links

3. **Data Storage**
   - Saves to unified database
   - Stores HTML locally
   - Downloads PDFs (if available)
   - Tracks metadata

4. **Error Handling**
   - Retries failed requests
   - Logs errors
   - Continues on failure
   - Resumable scraping

### Key Features

- ✅ **Smart parsing** - Multiple fallback strategies
- ✅ **Rate limiting** - Respects server with delays
- ✅ **Resumable** - Can stop and continue later
- ✅ **Deduplication** - Handles multiple indexes
- ✅ **PDF detection** - Automatically finds and downloads
- ✅ **Error recovery** - Continues despite failures
- ✅ **Progress tracking** - Real-time statistics

---

## 🔍 Troubleshooting

### Issue: "Connection refused"

```bash
# The Bangladesh Laws website might be down or blocking requests
# Try accessing in browser first: http://bdlaws.minlaw.gov.bd
```

**Solution:**
1. Check website is accessible
2. Try with VPN if blocked in your region
3. Increase `request_delay` in config

### Issue: "No documents found"

**Possible causes:**
- Website structure changed
- Index pages moved to different URLs
- Incorrect configuration

**Solution:**
1. Visit index pages manually in browser
2. Update URLs in `config/bangladesh.yaml`
3. Check parser logic in `bangladesh_scraper.py`

### Issue: "Failed to extract title"

**Cause:** HTML structure different than expected

**Solution:**
1. Add debug logging
2. Inspect actual HTML
3. Update `_extract_title()` method with new selectors

---

## 🚀 Next Steps

### Option 1: Scrape Bangladesh Laws Now

```bash
# Ready to use!
python unified_scraper.py scrape --country bangladesh
```

### Option 2: Add India Scraper

The framework is ready - just need to implement `IndiaKanoonScraper`:

```python
# src/scrapers/india_scraper.py
class IndiaKanoonScraper(BaseLegalScraper):
    # Implement abstract methods
    # Use existing bulk_download.py logic
    pass
```

### Option 3: Add More Countries

Easy to extend! Just:
1. Create new scraper class
2. Add YAML config
3. Update CLI

**Potential countries:**
- Pakistan (pakistancode.gov.pk)
- Sri Lanka
- Nepal
- Any legal database!

---

## 📚 Files Created

### Core Framework

```
src/
├── unified_database.py           # ✅ Database manager
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py           # ✅ Abstract base class
│   └── bangladesh_scraper.py     # ✅ Bangladesh implementation
└── parsers/
    ├── __init__.py
    └── base_parser.py             # ✅ HTML utilities
```

### Configuration

```
config/
└── bangladesh.yaml                # ✅ Bangladesh config
```

### CLI Tool

```
unified_scraper.py                 # ✅ Main command-line tool
```

### Database

```
migrations/
└── create_unified_schema.sql      # ✅ Unified schema
```

---

## 🎉 Summary

You now have a **production-ready** unified legal document scraper that:

✅ **Works immediately** for Bangladesh Laws
✅ **Extensible** - Easy to add more countries
✅ **Unified database** - All countries in one place
✅ **Command-line interface** - Simple to use
✅ **Configurable** - YAML-based settings
✅ **Robust** - Error handling, resumable, logging

### What You Can Do Right Now

```bash
# 1. Test setup
python unified_scraper.py test

# 2. Start scraping Bangladesh Laws
python unified_scraper.py scrape --country bangladesh

# 3. Monitor progress (in another terminal)
python unified_scraper.py stats --country bangladesh

# 4. Search documents
python unified_scraper.py search "constitution"

# 5. View all documents in database
sqlite3 data/indiankanoon.db "SELECT title FROM legal_documents WHERE country='bangladesh' LIMIT 10;"
```

**Scraping 1,500 Bangladesh laws will take approximately 1-2 hours.**

---

**Ready to scrape? Run:**
```bash
python unified_scraper.py scrape --country bangladesh
```

🎯 **Good luck!**
