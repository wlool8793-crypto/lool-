# Unified Multi-Country Legal Scraper - Implementation Status

**Last Updated:** October 21, 2025
**Status:** 🚧 In Progress - Phase 1 Complete

---

## ✅ Phase 1: Database Schema (COMPLETE)

### What Was Done

1. **Created unified database schema** (`migrations/create_unified_schema.sql`)
   - `legal_documents` - Main unified table supporting all countries
   - `document_metadata` - Flexible key-value metadata storage
   - `document_citations` - Track references between documents
   - `scraping_queue` - Manage large scraping jobs

2. **Applied migration** to existing database
   - ✅ All tables created successfully
   - ✅ Indexes created for fast queries
   - ✅ Views created for statistics
   - ✅ Triggers added for auto-timestamps

3. **Migrated existing data**
   - ✅ 600 Indian Kanoon cases migrated to unified schema
   - ✅ 71 PDFs already downloaded
   - ✅ All metadata preserved

### Verification

```bash
# Check schema
sqlite3 data/indiankanoon.db "SELECT * FROM overall_stats;"
# Result: 600 total documents, 71 PDFs, all from India

# Check country stats
sqlite3 data/indiankanoon.db "SELECT * FROM country_stats;"
# Result: india | 600 docs | 71 PDFs
```

---

## 🚧 Phase 2: Base Architecture (NEXT)

### To Be Created

1. **`src/scrapers/base_scraper.py`** - Abstract base class
   ```python
   class BaseLegalScraper(ABC):
       - get_document_list() -> List[str]
       - parse_document(url) -> Dict
       - extract_pdf_url(html) -> Optional[str]
       - scrape_all()
       - save_document(doc_data)
   ```

2. **`src/scrapers/__init__.py`** - Scraper package initialization

3. **`src/parsers/base_parser.py`** - HTML parsing utilities
   ```python
   class BaseParser:
       - extract_title(html)
       - extract_year(html)
       - extract_text(html)
       - clean_html(html)
   ```

---

## 📋 Phase 3: Country-Specific Scrapers (PLANNED)

### India Scraper

**File:** `src/scrapers/india_scraper.py`

**Features:**
- Extends `BaseLegalScraper`
- Reuses existing Indian Kanoon scraping logic
- Implements abstract methods for India-specific parsing
- Handles search pagination
- Extracts court, case details, citations

**Status:** ⬜ Not started

### Bangladesh Scraper

**File:** `src/scrapers/bangladesh_scraper.py`

**Features:**
- Extends `BaseLegalScraper`
- Scrapes both chronological and alphabetical indexes
- Parses Acts, Ordinances, Presidential Orders
- Extracts ministry, year, act number
- Downloads PDFs if available

**Status:** ⬜ Not started

---

## ⚙️ Phase 4: Configuration System (PLANNED)

### Files to Create

1. **`config/countries.yaml`** - Global settings
   ```yaml
   countries:
     - india
     - bangladesh

   default_settings:
     concurrent_requests: 5
     request_delay: 2
   ```

2. **`config/india.yaml`** - India-specific config
   ```yaml
   country: india
   base_url: "https://indiankanoon.org"
   start_year: 2020
   end_year: 2024
   ```

3. **`config/bangladesh.yaml`** - Bangladesh-specific config
   ```yaml
   country: bangladesh
   base_url: "http://bdlaws.minlaw.gov.bd"
   indexes:
     - chronological
     - alphabetical
   ```

---

## 🖥️ Phase 5: Unified CLI (PLANNED)

**File:** `unified_scraper.py`

**Commands:**
```bash
# Scrape all countries
python unified_scraper.py scrape --country all

# Scrape specific country
python unified_scraper.py scrape --country bangladesh

# Show statistics
python unified_scraper.py stats
python unified_scraper.py stats --country india

# Resume interrupted scraping
python unified_scraper.py resume
```

---

## 📊 Phase 6: Dashboard Updates (PLANNED)

**File:** `dashboard.py` (update existing)

**New Features:**
- Multi-country statistics
- Per-country progress bars
- Combined total across all countries
- Filter by country dropdown

---

## 🗂️ Current Project Structure

```
data-collection/
├── data/
│   └── indiankanoon.db                # ✅ Unified schema applied
│
├── migrations/
│   └── create_unified_schema.sql      # ✅ Created
│
├── src/
│   ├── scrapers/                      # ✅ Directory created
│   │   ├── __init__.py               # ⬜ To create
│   │   ├── base_scraper.py           # ⬜ To create
│   │   ├── india_scraper.py          # ⬜ To create
│   │   └── bangladesh_scraper.py     # ⬜ To create
│   │
│   ├── parsers/                       # ✅ Directory created
│   │   ├── __init__.py               # ⬜ To create
│   │   ├── base_parser.py            # ⬜ To create
│   │   ├── india_parser.py           # ⬜ To create
│   │   └── bangladesh_parser.py      # ⬜ To create
│   │
│   └── (existing files...)
│
├── config/                            # ⬜ To create
│   ├── countries.yaml                # ⬜ To create
│   ├── india.yaml                    # ⬜ To create
│   └── bangladesh.yaml               # ⬜ To create
│
├── unified_scraper.py                 # ⬜ To create
├── UNIFIED_SCRAPER_STATUS.md          # ✅ This file
└── (existing files...)
```

---

## 📈 Progress Summary

| Phase | Status | Progress |
|-------|--------|----------|
| 1. Database Schema | ✅ Complete | 100% |
| 2. Base Architecture | 🚧 In Progress | 10% |
| 3. Country Scrapers | ⬜ Not Started | 0% |
| 4. Configuration | ⬜ Not Started | 0% |
| 5. Unified CLI | ⬜ Not Started | 0% |
| 6. Dashboard Updates | ⬜ Not Started | 0% |
| 7. Testing | ⬜ Not Started | 0% |
| 8. Documentation | ⬜ Not Started | 0% |
| **Overall** | **🚧 In Progress** | **15%** |

---

## ⏱️ Estimated Remaining Time

- Phase 2: Base Architecture - 45 minutes
- Phase 3: Country Scrapers - 2.5 hours
- Phase 4: Configuration - 30 minutes
- Phase 5: Unified CLI - 45 minutes
- Phase 6: Dashboard - 30 minutes
- Phase 7: Testing - 45 minutes
- Phase 8: Documentation - 30 minutes

**Total Remaining: ~5.5 hours**

---

## 🎯 Next Steps

1. Create `base_scraper.py` with abstract class
2. Create `base_parser.py` with HTML utilities
3. Build `bangladesh_scraper.py` (new)
4. Refactor existing code into `india_scraper.py`
5. Create YAML configuration files
6. Build unified CLI tool
7. Update dashboard
8. Test end-to-end
9. Write documentation

---

## ✅ What You Can Do Now

Even though the unified scraper isn't complete yet, you can still:

1. **Use the unified database:**
   ```bash
   sqlite3 data/indiankanoon.db "SELECT * FROM country_stats;"
   ```

2. **Query documents by country:**
   ```sql
   SELECT title, year FROM legal_documents
   WHERE country = 'india' LIMIT 10;
   ```

3. **Check overall stats:**
   ```sql
   SELECT * FROM overall_stats;
   ```

4. **Use existing Indian Kanoon scraper** (still works):
   ```bash
   python bulk_download.py
   ```

---

## 🚀 When Ready to Continue

Let me know and I'll continue implementing:
- ✅ **Option A:** Continue building all phases (5.5 hours total)
- ✅ **Option B:** Build just Bangladesh scraper first (test quickly)
- ✅ **Option C:** Skip ahead to specific phase you want

**Current Status:** Database layer complete and ready for scrapers!

---

**Questions? Ready to continue? Just say the word!** 🎯
