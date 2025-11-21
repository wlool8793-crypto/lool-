# Universal System - Quick Start Guide

## 1. Test the System (5 minutes)

```bash
# Run complete test suite
python test_universal_system.py

# Expected output: ALL TESTS PASSED!
```

## 2. Initialize Production Database (2 minutes)

```bash
# Create database with universal schema
sqlite3 data/universal_legal.db < migrations/create_universal_schema.sql

# Verify tables created
sqlite3 data/universal_legal.db "SELECT name FROM sqlite_master WHERE type='table';"
```

## 3. Use in Your Code (Simple Example)

```python
from src.unified_database import UnifiedDatabase

# Initialize with universal schema
db = UnifiedDatabase('data/universal_legal.db', use_universal=True)

# Save a document (minimal data required)
doc_id = db.save_universal_document({
    'country_code': 'BD',
    'country_name': 'Bangladesh',
    'doc_category': 'ACT',
    'doc_year': 1860,
    'title_full': 'The Penal Code, 1860',
    'title_short': 'Penal Code',
    'source_url': 'http://bdlaws.minlaw.gov.bd/act-45.html',
    'source_domain': 'bdlaws.minlaw.gov.bd',
    'plain_text': 'Act relating to criminal offenses and punishments',
    'legal_status': 'ACTIVE'
})

# System automatically generates:
# - Global ID: ULEGAL-0000000001
# - UUID: <unique UUID>
# - Filename: BD_ACT_CENTRAL_1860_XLV_0001_0001_Penal_Code_CRM_PEN_1860_ACTIVE_0000000001.pdf
# - Folder: BD/ACT/1851-1900/
# - Subject: CRIMINAL (CRM)

print(f"Saved document with ID: {doc_id}")

db.close()
```

## 4. Query Documents

```python
from src.unified_database import UnifiedDatabase

db = UnifiedDatabase('data/universal_legal.db', use_universal=True)
cursor = db.conn.cursor()

# Get statistics
cursor.execute("SELECT * FROM v_overall_stats")
stats = dict(cursor.fetchone())
print(f"Total documents: {stats['total_documents']}")

# Find documents
cursor.execute("""
    SELECT global_id, title_full, filename_universal
    FROM universal_legal_documents
    WHERE country_code = 'BD' AND doc_year = 1860
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

db.close()
```

## 5. Generate Filenames Manually

```python
from src.naming.universal_namer import UniversalNamer

namer = UniversalNamer()

doc_data = {
    'country_code': 'BD',
    'doc_category': 'ACT',
    'jurisdiction_level': 'CENTRAL',
    'doc_year': 1860,
    'doc_number': 'XLV',
    'sequence': 45,
    'yearly_sequence': 45,
    'title_short': 'Penal Code',
    'subject_code': 'CRM',
    'subject_subcategory': 'PEN',
    'legal_status': 'ACTIVE',
    'global_id_numeric': 10045
}

filename = namer.generate_filename(doc_data)
folder = namer.generate_folder_path(doc_data)

print(f"Filename: {filename}.pdf")
print(f"Folder: Legal_Database/{folder}/")
```

## 6. Classify Subjects

```python
from src.taxonomy.subjects import SubjectClassifier

classifier = SubjectClassifier()

primary, subcat, code = classifier.classify(
    title='The Penal Code, 1860',
    content='Act relating to criminal offenses and punishments',
    country_code='BD'
)

print(f"Subject: {primary} ({code})")
print(f"Subcategory: {subcat}")
# Output: Subject: CRIMINAL (CRM), Subcategory: PEN
```

## 7. Generate IDs

```python
from src.naming.id_generator import IDGenerator

gen = IDGenerator('data/universal_legal.db')

# Global ID
numeric_id, formatted_id = gen.generate_global_id()
print(formatted_id)  # ULEGAL-0000000001

# UUID
uuid = gen.generate_uuid()
print(uuid)  # 550e8400-e29b-41d4-a716-446655440000

# Yearly sequence
seq = gen.get_next_yearly_sequence('BD', 'ACT', 1860)
print(seq)  # 1, 2, 3...
```

## 8. File Structure

```
Legal_Database/
├── _SYSTEM/
│   ├── taxonomy.json          # Subject classifications
│   ├── country_codes.json     # Country configurations
│   └── README.md
├── BD/ACT/1851-1900/          # Bangladesh acts from 1851-1900
├── BD/ACT/CENTRAL/            # Bangladesh central acts
├── IN/CASE/SC/                # India Supreme Court cases
├── IN/ACT/CENTRAL/            # India central acts
└── PK/ACT/FEDERAL/            # Pakistan federal acts
```

## 9. Filename Format

```
{CC}_{CAT}_{SUBCAT}_{YEAR}_{NUM}_{SEQ}_{YRSEQ}_{TITLE}_{SUBJ}_{SUB}_{DATE}_{STATUS}_{ID}.pdf

Example:
BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRIMINAL_PEN_1860_ACTIVE_0000010045.pdf

Where:
BD          = Bangladesh
ACT         = Act (document category)
CENTRAL     = Central/Federal jurisdiction
1860        = Year
XLV         = Act number (Roman numeral)
0045        = Sequence number
0045        = Yearly sequence
Penal_Code  = Short title
CRIMINAL    = Subject code
PEN         = Subject subcategory (Penal)
1860        = Date
ACTIVE      = Legal status
0000010045  = Global ID
```

## 10. Database Schema (Key Tables)

```sql
-- Main table
universal_legal_documents
  - id (primary key)
  - global_id (ULEGAL-0000000001)
  - uuid
  - country_code, country_name
  - doc_category, doc_type, doc_year
  - title_full, title_short
  - subject_primary, subject_code
  - filename_universal
  - file_path_relative
  - legal_status
  - ... (60+ fields total)

-- ID generation
sequence_tracker
  - sequence_type (GLOBAL, YEARLY)
  - country_code, doc_category, year
  - last_value

-- Views for statistics
v_overall_stats
v_country_stats
v_category_stats
```

## 11. Add a New Country

```bash
# 1. Edit Legal_Database/_SYSTEM/country_codes.json
# Add country configuration

# 2. Create folders
mkdir -p Legal_Database/XX/{CASE,ACT,RULE,ORDER,MISC}

# 3. Use existing code (no changes needed!)
db.save_universal_document({
    'country_code': 'XX',
    'country_name': 'New Country',
    # ... rest of data
})
```

## 12. Subject Categories

```
CRIMINAL (CRM)      - Penal codes, procedure, evidence
CIVIL (CIV)         - Civil procedure, contracts, torts
CONSTITUTIONAL (CON) - Fundamental rights, writs
PROPERTY (PRO)      - Land, tenancy, registration
FAMILY (FAM)        - Marriage, divorce, adoption
COMMERCIAL (COM)    - Companies, banking, insurance
TAX (TAX)           - Income tax, GST, customs
LABOR (LAB)         - Employment, industrial disputes
ENVIRONMENTAL (ENV) - Pollution, forests
IP                  - Patents, trademarks, copyright
ADMINISTRATIVE (ADM) - Service law, regulatory
CONSUMER (CNS)      - Consumer protection
IT                  - Cyber law, data protection
INTERNATIONAL (INT) - Treaties, extradition
HUMAN_RIGHTS (HR)   - Rights, discrimination
GENERAL (GEN)       - Miscellaneous
```

## 13. Common Queries

```sql
-- Total documents
SELECT * FROM v_overall_stats;

-- By country
SELECT * FROM v_country_stats;

-- Recent documents
SELECT global_id, title_full, filename_universal
FROM universal_legal_documents
ORDER BY created_at DESC
LIMIT 10;

-- Search by subject
SELECT global_id, title_full
FROM universal_legal_documents
WHERE subject_primary = 'CRIMINAL'
  AND country_code = 'BD';

-- Active documents only
SELECT COUNT(*)
FROM universal_legal_documents
WHERE legal_status = 'ACTIVE';
```

## 14. Documentation

- `UNIVERSAL_SYSTEM_GUIDE.md` - Complete implementation guide (500+ lines)
- `IMPLEMENTATION_COMPLETE_UNIVERSAL.md` - What was built (detailed summary)
- `Legal_Database/_SYSTEM/README.md` - Folder structure guide
- `migrations/create_universal_schema.sql` - Database schema (800+ lines)

## 15. Testing

```bash
# Run all tests
python test_universal_system.py

# Test individual components
python src/naming/id_generator.py
python src/naming/universal_namer.py
python src/taxonomy/subjects.py
```

---

## Troubleshooting

**Q: Import errors?**
```bash
# Make sure you're in the project directory
cd /workspaces/lool-/data-collection

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Q: Database not found?**
```bash
# Create data directory
mkdir -p data

# Initialize database
sqlite3 data/universal_legal.db < migrations/create_universal_schema.sql
```

**Q: How do I migrate existing data?**
```bash
# Run migration script
sqlite3 data/universal_legal.db < migrations/migrate_to_universal.sql
```

---

## Next Steps

1. ✅ Test the system: `python test_universal_system.py`
2. ✅ Initialize production DB
3. ✅ Update your scrapers to use `UnifiedDatabase(use_universal=True)`
4. ✅ Run a test scrape
5. ✅ Verify files created in `Legal_Database/`

**You're ready to go!** 🚀
