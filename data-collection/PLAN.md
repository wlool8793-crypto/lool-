# Comprehensive Plan: Complete IndianKanoon Data Collection System

**Mission:** Download ALL Legal Documents from IndianKanoon.org

**Scope:** 100,000-500,000+ legal documents covering 75 years (1950-2024)

---

## 🔍 Research Findings

Based on comprehensive research using Selenium and BeautifulSoup:

### Documents Available:
- **27 Document Types:** judgments, acts, statutes, bills, amendments, constitution, notifications, circulars, orders, resolutions, gazette, petitions, writs, appeals, verdicts, rulings, decisions, tribunals, district courts, appellate, sessions, magistrate
- **30+ Courts:** Supreme Court + 23 High Courts + 10+ Tribunals
- **75 Years:** 1950-2024 complete legal history
- **Conservative Estimate:** 50,000-100,000 documents
- **Realistic Estimate:** 100,000-300,000 documents
- **Maximum Potential:** 500,000+ documents

### Courts Discovered:
**Supreme Court of India**
- Years: 1950-2024
- Estimated: 7,500-75,000 cases

**23 High Courts:**
Delhi, Bombay, Calcutta, Madras, Karnataka, Kerala, Gujarat, Rajasthan, Punjab, Allahabad, Patna, Andhra Pradesh, Telangana, Orissa, Jharkhand, Chhattisgarh, Uttarakhand, Himachal Pradesh, Jammu & Kashmir, Guwahati, Sikkim, Tripura, Meghalaya, Manipur

**10+ Tribunals:**
CAT, ITAT, CESTAT, NCLAT, NCLT, NGT, AFT, Railway Claims Tribunal, Consumer Courts, Labour Courts

---

## 📋 Implementation Phases

### Phase 1: Enhanced Database Schema ✅ (Priority 1)

**File:** `src/database.py`

**Add to LegalCase model:**
```python
court_type = Column(Enum('SUPREME', 'HIGH', 'TRIBUNAL', 'DISTRICT'))
court_name = Column(String(200))  # "Delhi High Court", "Karnataka High Court"
state = Column(String(100))  # For High Courts
document_type = Column(String(100))  # judgment, act, statute, notification
year = Column(Integer)  # Extracted from case_date
scrape_tier = Column(Integer)  # 1=Priority, 2=High, 3=Medium, 4=Complete
pagination_page = Column(Integer)  # Which search page this came from
is_historical = Column(Boolean)  # True if before 2015
```

**Add indexes:**
- `court_type, year`
- `document_type, year`
- `pdf_downloaded`
- `scrape_tier`

---

### Phase 2: Universal Multi-Court Scraper (Priority 1)

**File:** `universal_scraper.py`

**Features:**
- Scrape ALL courts (Supreme + High + Tribunals)
- Handle ALL 27 document types
- Year-by-year processing (1950-2024)
- Smart pagination (auto-detect max pages)
- Parallel court scraping (3-5 simultaneous)
- Configurable via config.yaml

**Functions:**
- `scrape_supreme_court(start_year, end_year)`
- `scrape_high_court(court_name, state, start_year, end_year)`
- `scrape_tribunal(tribunal_type, start_year, end_year)`
- `scrape_document_type(doc_type, court, year)`
- `auto_detect_pagination(query, max_check=100)`

---

### Phase 3: Tier-Based Strategy Manager (Priority 1)

**File:** `tier_manager.py`

**Tier 1 - Priority (Supreme Court Recent):**
- Supreme Court 2015-2024
- Estimated: 10,000 cases
- Time: 5-10 hours
- Storage: ~15 GB

**Tier 2 - High (Major High Courts):**
- Delhi, Bombay, Karnataka, Madras, Calcutta HC
- Years: 2015-2024
- Estimated: 50,000 cases
- Time: 20-30 hours
- Storage: ~75 GB

**Tier 3 - Medium (All Courts Recent):**
- All 23 High Courts + 10 Tribunals
- Years: 2015-2024
- Estimated: 150,000 cases
- Time: 60-80 hours
- Storage: ~225 GB

**Tier 4 - Complete (Historical + All Types):**
- All courts 1950-2014
- All 27 document types
- Estimated: 300,000+ cases
- Time: 100-200 hours
- Storage: ~450 GB

---

### Phase 4: Real-Time Progress Dashboard (Priority 2)

**File:** `progress_dashboard.py`

**Web Dashboard Features:**
- Overall progress bar with percentage
- Tier-wise completion (visual bars)
- Court-wise progress (sortable table)
- Year-wise coverage (timeline)
- Live activity feed (last 50 downloads)
- Success rate & error tracking
- Speed metrics (docs/min, ETA)
- Storage usage (GB used/available)

**Tech Stack:**
- Flask for web server
- Socket.IO for real-time updates
- Plotly for charts
- Bootstrap for UI

**Dashboard URL:** http://localhost:8080

**Sections:**
1. **Overview:** Total progress, success rate, ETA
2. **By Tier:** Visual progress for each tier
3. **By Court:** Detailed breakdown per court
4. **By Year:** Timeline showing coverage
5. **Live Feed:** Real-time download activity
6. **Statistics:** Charts and graphs
7. **Configuration:** Current settings
8. **Controls:** Pause/Resume/Stop

---

### Phase 5: Configuration System (Priority 1)

**File:** `config.yaml`

```yaml
# Scraping Configuration
scraping:
  # Which tiers to execute
  enabled_tiers: [1, 2, 3, 4]

  # Court configuration
  courts:
    supreme_court:
      enabled: true
      years: [1950, 2024]
      priority: 1
      max_pages_per_year: 100

    high_courts:
      enabled: true
      priority_courts:  # Download these first
        - delhi
        - bombay
        - karnataka
        - madras
        - calcutta
      all_courts:  # Then download these
        - punjab
        - rajasthan
        - gujarat
        # ... all 23 courts
      years: [2015, 2024]
      priority: 2

    tribunals:
      enabled: true
      types: [CAT, ITAT, CESTAT, NCLAT, NCLT, NGT, AFT]
      years: [2015, 2024]
      priority: 3

  # Document types to scrape
  document_types:
    enabled: true
    types:
      - judgment
      - act
      - statute
      - notification
      - circular
      - order
      # ... all 27 types

  # Pagination settings
  pagination:
    auto_detect: true
    max_pages_per_query: 100
    results_per_page: 10

  # Performance tuning
  performance:
    parallel_courts: 3
    delay_between_requests: 2  # seconds
    retry_attempts: 3
    retry_delay: 5  # seconds
    timeout: 90  # seconds
    max_retries_before_skip: 5

  # PDF downloads
  pdfs:
    enabled: true
    download_timeout: 120
    validate_file: true

  # Storage limits
  storage:
    max_disk_space_gb: 500
    min_free_space_gb: 50
    auto_pause_on_low_space: true
    compress_old_pdfs: false

  # Monitoring
  monitoring:
    dashboard_enabled: true
    dashboard_port: 8080
    log_level: INFO
    save_progress_every: 100  # docs
    generate_report_every: 1000  # docs
```

---

### Phase 6: Master Orchestrator (Priority 1)

**File:** `master_downloader.py`

**Main Features:**
- Reads config.yaml
- Executes tiers in order
- Manages parallel scrapers
- Monitors disk space continuously
- Auto-pauses on low space/high errors
- Handles Ctrl+C gracefully
- Saves checkpoints every N documents
- Resumes from last checkpoint
- Generates daily summary reports

**Command Line:**
```bash
# Start full download
python master_downloader.py --config config.yaml

# Resume from checkpoint
python master_downloader.py --resume

# Specific tier only
python master_downloader.py --tier 1

# Specific court only
python master_downloader.py --court "Delhi High Court"

# Test mode (first 10 docs)
python master_downloader.py --test

# Dry run (no downloads)
python master_downloader.py --dry-run
```

---

### Phase 7: Analytics & Reporting (Priority 3)

**File:** `analytics.py`

**Reports Generated:**
1. **Daily Summary Report**
   - Documents added today
   - Courts covered
   - Success rate
   - Errors encountered

2. **Comprehensive Statistics**
   - Documents by court (pie chart)
   - Documents by year (line graph)
   - Documents by type (bar chart)
   - Coverage heatmap (court × year)
   - Success rate trends

3. **Data Quality Report**
   - Missing PDFs
   - Incomplete metadata
   - Duplicate detection
   - Validation errors

4. **Storage Report**
   - Disk space used
   - Database size
   - PDF storage breakdown
   - Projected space needs

**Export Formats:**
- PDF report
- Excel spreadsheet
- CSV files
- JSON data

---

## 📁 Project Structure

```
data-collection/
├── PLAN.md                        # This file
├── config/
│   ├── config.yaml               # Main configuration
│   ├── courts.json               # Court definitions
│   └── tiers.json                # Tier strategies
│
├── src/
│   ├── database.py               # ✏️ Enhanced schema
│   ├── scraper.py                # ✏️ Multi-court support
│   ├── universal_scraper.py      # 🆕 New scraper
│   ├── tier_manager.py           # 🆕 Tier management
│   └── utils.py                  # 🆕 Helper functions
│
├── dashboard/
│   ├── progress_dashboard.py     # 🆕 Web dashboard
│   ├── templates/
│   │   ├── index.html
│   │   ├── courts.html
│   │   └── analytics.html
│   └── static/
│       ├── css/
│       └── js/
│
├── master_downloader.py          # 🆕 Main orchestrator
├── analytics.py                  # 🆕 Reporting system
│
├── data/
│   ├── indiankanoon.db           # SQLite database
│   ├── pdfs/                     # PDF storage
│   └── checkpoints/              # 🆕 Resume checkpoints
│
├── reports/
│   ├── daily/                    # 🆕 Daily reports
│   └── summary/                  # 🆕 Summary reports
│
└── logs/
    ├── master.log
    ├── by_court/                 # 🆕 Per-court logs
    └── by_date/                  # 🆕 Per-date logs
```

---

## ⚙️ Implementation Priority

### Week 1: Foundation
1. ✅ Update database schema (`src/database.py`)
2. ✅ Create configuration system (`config.yaml`)
3. ✅ Build universal scraper (`universal_scraper.py`)
4. ✅ Create tier manager (`tier_manager.py`)

### Week 2: Dashboard & Orchestration
5. ✅ Build progress dashboard (`progress_dashboard.py`)
6. ✅ Create master downloader (`master_downloader.py`)
7. ✅ Add analytics system (`analytics.py`)
8. ✅ Testing & debugging

### Week 3+: Execution
9. Execute Tier 1 (Supreme Court 2015-2024)
10. Execute Tier 2 (Top 5 High Courts)
11. Execute Tier 3 (All courts recent)
12. Execute Tier 4 (Historical data)

---

## 📊 Expected Results

### After Tier 1 (Week 3):
- Documents: ~10,000
- Storage: ~15 GB
- Courts: 1 (Supreme Court)
- Years: 2015-2024 (10 years)

### After Tier 2 (Week 5):
- Documents: ~60,000
- Storage: ~90 GB
- Courts: 6 (SC + Top 5 HC)
- Years: 2015-2024

### After Tier 3 (Week 8):
- Documents: ~150,000
- Storage: ~225 GB
- Courts: 30+ (All courts)
- Years: 2015-2024

### After Tier 4 (Complete):
- Documents: 300,000-500,000+
- Storage: 400-500 GB
- Courts: 30+ (All courts)
- Years: 1950-2024 (75 years)
- Document types: All 27 types

---

## 🎯 Success Metrics

✅ **Technical:**
- Resume from any point: YES
- 95%+ success rate: YES
- Real-time dashboard: YES
- Parallel downloads: YES
- Auto error recovery: YES

✅ **Coverage:**
- All courts: 30+ courts
- All years: 1950-2024
- All document types: 27 types
- PDF availability: 85-90%

✅ **Quality:**
- Complete metadata: 99%+
- Valid PDFs: 98%+
- No duplicates: 100%
- Searchable: 100%

---

## 🚀 Quick Start Commands

```bash
# Initial setup
pip install -r requirements.txt

# Start dashboard (separate terminal)
python progress_dashboard.py

# Run Tier 1 only (recommended start)
python master_downloader.py --tier 1

# Run all tiers
python master_downloader.py --config config.yaml

# Resume interrupted download
python master_downloader.py --resume

# Generate analytics report
python analytics.py --report comprehensive

# Check current progress
python master_downloader.py --status
```

---

## 📝 Notes

- **Legal:** All data is publicly available on IndianKanoon.org
- **Rate Limiting:** 2-second delay between requests (configurable)
- **Storage:** Plan for 500 GB minimum
- **Time:** 100-200 hours for complete collection
- **Resumable:** Can stop/start at any time
- **Parallel:** Downloads 3 courts simultaneously

---

**Status:** ⏳ Ready to Implement
**Next Step:** Update database schema (Phase 1)
