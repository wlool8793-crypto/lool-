# Data Access Guide

## Where Your Scraped Data Is Stored

All scraped legal documents are stored in multiple locations for redundancy and easy access.

---

## 1. Main Database (PRIMARY)

**File:** `/workspaces/lool-/data-collection/data/indiankanoon.db`
**Size:** ~28 MB (growing)
**Format:** SQLite database

### Tables:
- `universal_legal_documents` - Main table with all documents
- `legal_cases` - Legacy India cases (600 documents)
- `sequence_tracker` - Global ID tracking
- `citations` - Document citations
- `document_metadata` - Additional metadata

### Current Data:
```
Total Documents: 749+ (and growing)
├─ India (IN):      600 cases
└─ Bangladesh (BD): 149+ laws (scraping in progress)
```

---

## 2. Quick SQLite Commands

### Open Database
```bash
cd /workspaces/lool-/data-collection
sqlite3 data/indiankanoon.db
```

### View All Bangladesh Laws
```sql
SELECT global_id, title_full, doc_year, subject_primary
FROM universal_legal_documents
WHERE country_code='BD'
ORDER BY doc_year DESC
LIMIT 20;
```

### Search by Keyword
```sql
SELECT global_id, title_full, doc_year
FROM universal_legal_documents
WHERE country_code='BD'
AND (title_full LIKE '%penal%' OR plain_text LIKE '%penal%')
LIMIT 10;
```

### Count by Subject
```sql
SELECT subject_primary, COUNT(*) as count
FROM universal_legal_documents
WHERE country_code='BD'
GROUP BY subject_primary
ORDER BY count DESC;
```

### Count by Year
```sql
SELECT doc_year, COUNT(*) as count
FROM universal_legal_documents
WHERE country_code='BD' AND doc_year IS NOT NULL
GROUP BY doc_year
ORDER BY doc_year DESC
LIMIT 20;
```

### Get Full Document Content
```sql
SELECT global_id, title_full, plain_text
FROM universal_legal_documents
WHERE global_id='ULEGAL-0000000887';
```

---

## 3. Export Data

### Export to CSV (All Fields)
```bash
sqlite3 -header -csv data/indiankanoon.db \
  "SELECT * FROM universal_legal_documents WHERE country_code='BD';" \
  > bangladesh_laws_full.csv
```

### Export to CSV (Summary)
```bash
sqlite3 -header -csv data/indiankanoon.db \
  "SELECT global_id, title_full, doc_year, subject_primary, source_url
   FROM universal_legal_documents
   WHERE country_code='BD';" \
  > bangladesh_laws_summary.csv
```

### Export to JSON
```bash
sqlite3 data/indiankanoon.db << 'EOF' > bangladesh_laws.json
.mode json
SELECT * FROM universal_legal_documents WHERE country_code='BD';
EOF
```

### Export by Subject
```bash
# Export only TAX laws
sqlite3 -header -csv data/indiankanoon.db \
  "SELECT * FROM universal_legal_documents
   WHERE country_code='BD' AND subject_primary='TAX';" \
  > bangladesh_tax_laws.csv
```

---

## 4. HTML Files (Raw Content)

**Location:** `/workspaces/lool-/data-collection/data/html/bangladesh/`

### List Files
```bash
ls data/html/bangladesh/
```

### Count Files
```bash
ls data/html/bangladesh/ | wc -l
```

### View a File
```bash
cat data/html/bangladesh/bangladesh_act-367.html
```

### Search HTML Files
```bash
grep -l "penal" data/html/bangladesh/*.html
```

---

## 5. Python Access

### Simple Query
```python
import sqlite3

# Connect
conn = sqlite3.connect('data/indiankanoon.db')
cursor = conn.cursor()

# Query Bangladesh laws
cursor.execute("""
    SELECT global_id, title_full, doc_year
    FROM universal_legal_documents
    WHERE country_code='BD'
    LIMIT 10
""")

# Print results
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} ({row[2]})")

conn.close()
```

### Get Full Document
```python
import sqlite3

conn = sqlite3.connect('data/indiankanoon.db')
conn.row_factory = sqlite3.Row  # Get dict-like rows

cursor = conn.cursor()
doc = cursor.execute("""
    SELECT * FROM universal_legal_documents
    WHERE global_id='ULEGAL-0000000887'
""").fetchone()

if doc:
    print(f"Title: {doc['title_full']}")
    print(f"Year: {doc['doc_year']}")
    print(f"Subject: {doc['subject_primary']}")
    print(f"Content: {doc['plain_text'][:500]}...")

conn.close()
```

### Export to Pandas
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/indiankanoon.db')

# Load all Bangladesh laws into DataFrame
df = pd.read_sql_query("""
    SELECT * FROM universal_legal_documents
    WHERE country_code='BD'
""", conn)

print(df.head())
print(f"Total records: {len(df)}")

# Save to CSV
df.to_csv('bangladesh_laws.csv', index=False)

# Save to Excel
df.to_excel('bangladesh_laws.xlsx', index=False)

conn.close()
```

---

## 6. Database Schema

### Universal Legal Documents Table

Key fields:
- `global_id` - Unique ID (ULEGAL-0000000001)
- `uuid` - UUID for distributed systems
- `country_code` - BD, IN, PK, etc.
- `country_name` - Bangladesh, India, etc.
- `doc_category` - ACT, CASE, RULE, ORDER
- `doc_year` - Year of enactment
- `title_full` - Full title
- `subject_primary` - CRIMINAL, CIVIL, TAX, etc.
- `subject_code` - CRM, CIV, TAX, etc.
- `plain_text` - Full text content
- `html_content` - HTML content
- `source_url` - Original URL
- `pdf_url` - PDF download URL (if available)
- `legal_status` - ACTIVE, REPEALED, etc.

### View Full Schema
```sql
.schema universal_legal_documents
```

---

## 7. Backup Database

```bash
# Create backup
cp data/indiankanoon.db data/indiankanoon_backup_$(date +%Y%m%d).db

# Verify backup
ls -lh data/indiankanoon_backup_*.db
```

---

## 8. Data Statistics

### Overall Stats
```sql
-- Total documents
SELECT COUNT(*) as total FROM universal_legal_documents;

-- By country
SELECT country_code, COUNT(*) as count
FROM universal_legal_documents
GROUP BY country_code;

-- By category
SELECT doc_category, COUNT(*) as count
FROM universal_legal_documents
GROUP BY doc_category;
```

### Bangladesh Stats
```sql
-- Total Bangladesh laws
SELECT COUNT(*) FROM universal_legal_documents WHERE country_code='BD';

-- By subject
SELECT subject_primary, COUNT(*)
FROM universal_legal_documents
WHERE country_code='BD'
GROUP BY subject_primary
ORDER BY COUNT(*) DESC;

-- By year (top 10)
SELECT doc_year, COUNT(*)
FROM universal_legal_documents
WHERE country_code='BD' AND doc_year IS NOT NULL
GROUP BY doc_year
ORDER BY COUNT(*) DESC
LIMIT 10;

-- Latest additions
SELECT global_id, title_full, created_at
FROM universal_legal_documents
WHERE country_code='BD'
ORDER BY created_at DESC
LIMIT 10;
```

---

## 9. Common Queries

### Find Penal Code
```sql
SELECT * FROM universal_legal_documents
WHERE country_code='BD'
AND title_full LIKE '%Penal Code%';
```

### Find Recent Laws (Last 10 years)
```sql
SELECT global_id, title_full, doc_year
FROM universal_legal_documents
WHERE country_code='BD'
AND doc_year >= 2014
ORDER BY doc_year DESC;
```

### Find by Multiple Subjects
```sql
SELECT global_id, title_full, subject_primary
FROM universal_legal_documents
WHERE country_code='BD'
AND subject_primary IN ('CRIMINAL', 'TAX', 'LABOR')
ORDER BY subject_primary;
```

### Full-Text Search
```sql
SELECT global_id, title_full, doc_year
FROM universal_legal_documents
WHERE country_code='BD'
AND (
    title_full LIKE '%murder%'
    OR plain_text LIKE '%murder%'
)
LIMIT 10;
```

---

## 10. File Locations Summary

```
/workspaces/lool-/data-collection/
├── data/
│   ├── indiankanoon.db                    ← Main database (28MB)
│   ├── indiankanoon_backup_*.db           ← Backups
│   ├── html/
│   │   └── bangladesh/                    ← HTML files (149+ files)
│   └── pdfs/
│       └── bangladesh/                    ← PDF files (if downloaded)
├── run_bangladesh_scraper.py              ← Scraper script
├── DATA_ACCESS_GUIDE.md                   ← This file
└── BDLEX_SCRAPER_PLAN.md                  ← BDLex plan
```

---

## 11. Monitoring Active Scraping

### Check Progress
```bash
# Count documents (updates in real-time)
sqlite3 data/indiankanoon.db \
  "SELECT COUNT(*) FROM universal_legal_documents WHERE country_code='BD';"

# View latest 5
sqlite3 data/indiankanoon.db \
  "SELECT global_id, title_full FROM universal_legal_documents
   WHERE country_code='BD' ORDER BY created_at DESC LIMIT 5;"
```

### Check Scraper Status
```bash
# Check if scraper is running
ps aux | grep bangladesh_scraper

# View scraper logs (if running)
tail -f logs/scraper.log
```

---

## 12. Troubleshooting

### Database Locked
```bash
# Check for open connections
lsof data/indiankanoon.db

# Force close all connections
pkill sqlite3
```

### Corrupted Database
```bash
# Check integrity
sqlite3 data/indiankanoon.db "PRAGMA integrity_check;"

# Restore from backup
cp data/indiankanoon_backup_*.db data/indiankanoon.db
```

### Large Database Size
```bash
# Vacuum database (optimize)
sqlite3 data/indiankanoon.db "VACUUM;"

# Check size
du -h data/indiankanoon.db
```

---

## Quick Reference Card

```bash
# View data
sqlite3 data/indiankanoon.db "SELECT * FROM universal_legal_documents WHERE country_code='BD' LIMIT 5;"

# Count
sqlite3 data/indiankanoon.db "SELECT COUNT(*) FROM universal_legal_documents WHERE country_code='BD';"

# Export CSV
sqlite3 -header -csv data/indiankanoon.db "SELECT * FROM universal_legal_documents WHERE country_code='BD';" > export.csv

# Search
sqlite3 data/indiankanoon.db "SELECT * FROM universal_legal_documents WHERE title_full LIKE '%penal%';"

# Backup
cp data/indiankanoon.db data/backup_$(date +%Y%m%d).db
```

---

**Last Updated:** October 22, 2025
**Database Size:** 28 MB
**Total Documents:** 749+ (growing)
