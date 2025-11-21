# Universal Legal Document Management System

## Folder Structure

This system uses a standardized folder structure for organizing legal documents from any country.

### Structure Pattern

```
Legal_Database/
├── _SYSTEM/
│   ├── taxonomy.json          # Subject classification system
│   ├── country_codes.json     # Country codes and court systems
│   └── README.md              # This file
│
├── {COUNTRY_CODE}/            # Two-letter ISO country code
│   ├── CASE/                  # Court judgments/cases
│   │   ├── {COURT_LEVEL}/     # SC, HC, DISTRICT, etc.
│   │   └── {YEAR}/            # Optional year-based organization
│   │
│   ├── ACT/                   # Acts/Statutes
│   │   ├── CENTRAL/           # Central/Federal acts
│   │   ├── STATE/             # State/Provincial acts
│   │   └── {TIME_PERIOD}/     # e.g., 1799-1850, 1851-1900
│   │
│   ├── RULE/                  # Rules and Regulations
│   ├── ORDER/                 # Government/Executive Orders
│   └── MISC/                  # Miscellaneous documents
```

### Examples

#### India (IN)
```
Legal_Database/IN/
├── CASE/
│   ├── SC/                    # Supreme Court
│   ├── HC/                    # High Courts
│   └── DISTRICT/              # District Courts
├── ACT/
│   ├── CENTRAL/               # Central Acts
│   └── STATE/                 # State Acts
```

#### Bangladesh (BD)
```
Legal_Database/BD/
├── ACT/
│   ├── CENTRAL/
│   ├── 1799-1850/             # Historical acts by period
│   ├── 1851-1900/
│   ├── 1901-1950/
│   ├── 1951-2000/
│   └── 2001-2025/
```

## Universal Filename Convention

### Format
```
{CC}_{CAT}_{SUBCAT}_{YEAR}_{NUM}_{SEQ}_{YRSEQ}_{SHORT_TITLE}_{SUBJ}_{SUBJSUB}_{DATE}_{STATUS}_{GLOBALID}.pdf
```

### Components

| Field | Description | Example |
|-------|-------------|---------|
| CC | Country Code (ISO 3166-1 Alpha-2) | BD, IN, PK |
| CAT | Document Category | CASE, ACT, RULE, ORDER |
| SUBCAT | Subcategory | CENTRAL, SC, HC, STATE |
| YEAR | Year (4 digits) | 1860, 2023 |
| NUM | Official Number (padded) | XLV, 045 |
| SEQ | Sequence within category (4 digits) | 0001, 0045 |
| YRSEQ | Yearly sequence (4 digits) | 0001, 0123 |
| SHORT_TITLE | Abbreviated title (snake_case) | Penal_Code |
| SUBJ | Subject code (3 letters) | CRM, CIV, CON |
| SUBJSUB | Subject subcategory (3 letters) | PEN, PRO, CPC |
| DATE | Enactment date (YYYYMMDD or YYYY) | 18601006, 1860 |
| STATUS | Legal status | ACTIVE, REPEALED, AMENDED |
| GLOBALID | Sequential global ID (10 digits) | 0000000001 |

### Example Filenames

**Bangladesh Penal Code (1860):**
```
BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRIMINAL_PEN_1860_ACTIVE_0000010045.pdf
```

**India Supreme Court Case:**
```
IN_CASE_SC_2023_0123_0001_0234_Kesavananda_Bharati_CONSTITUTIONAL_FUN_20230515_ACTIVE_0000020234.pdf
```

**Pakistan Companies Act:**
```
PK_ACT_FEDERAL_2017_XIX_0019_0019_Companies_Act_COMMERCIAL_CMP_2017_ACTIVE_0000030019.pdf
```

## Subject Classification

Subjects are hierarchical with codes:

### Primary Subjects
- **CRIMINAL** (CRM) - Criminal law
- **CIVIL** (CIV) - Civil law
- **CONSTITUTIONAL** (CON) - Constitutional matters
- **COMMERCIAL** (COM) - Business/commercial
- **TAX** (TAX) - Taxation
- **LABOR** (LAB) - Employment/labor
- **PROPERTY** (PRO) - Real estate/property
- **FAMILY** (FAM) - Family law
- **ENVIRONMENTAL** (ENV) - Environment
- **IP** - Intellectual Property
- **ADMINISTRATIVE** (ADM) - Administrative law
- **CONSUMER** (CNS) - Consumer protection
- **IT** - Information technology/cyber
- **INTERNATIONAL** (INT) - International law
- **HUMAN_RIGHTS** (HR) - Human rights
- **GENERAL** (GEN) - Miscellaneous

### Subcategories
Each primary subject has subcategories (e.g., CRIMINAL.PEN for Penal Code, CIVIL.CPC for Civil Procedure Code).

See `taxonomy.json` for complete classification.

## Database Schema

All documents are stored in the `universal_legal_documents` table with:

- **Global ID**: Sequential unique identifier (ULEGAL-0000000001)
- **UUID**: UUID v4 for distributed systems
- **Country Code**: ISO 3166-1 Alpha-2
- **Classification**: Category, type, subcategory
- **Identification**: Document number, year, sequences
- **Titles**: Full, short, alternate
- **Subject**: Multi-level taxonomy
- **Court/Authority**: Court or issuing authority details
- **Citations**: Primary and alternate citations
- **Legal Status**: ACTIVE, REPEALED, AMENDED, etc.
- **Dates**: Enacted, effective, published, amended, repealed
- **Content**: HTML, plain text, summary
- **Files**: Universal filename, paths
- **PDF**: URL, path, metadata
- **Source**: Original URL, domain, database
- **Relationships**: Parent docs, amendments, citations
- **Metadata**: Versioning, quality scores
- **Scraping**: Scraper info, timestamps, status

## Usage

1. **Adding a new country**: Add entry to `country_codes.json`
2. **Adding documents**: Use `UniversalNamer` to generate filenames
3. **Searching**: Use subject codes and country codes
4. **Migration**: Use `migrator.py` to migrate existing data

## Version History

- **1.0** (2025-10-22): Initial universal system
