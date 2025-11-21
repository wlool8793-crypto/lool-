# BDLex.com Scraper Implementation Plan

**Target Site:** https://www.bdlex.com/
**Type:** Subscription-based legal database (requires authentication)
**Content:** Bangladesh case laws, historical cases (1870-1969), statutes/acts/ordinances
**Approach:** Authenticated scraping with Selenium

---

## Overview

BDLex.com is Bangladesh's largest legal database platform containing:
- **Bangladesh Case Laws** (1970-present)
- **Historical Cases** from India & Pakistan era (1870-1969)
- **Bangladesh Statutes, Ordinances & Orders**
- **Indian Supreme Court** judgments (1950-present)

This plan outlines building an authenticated scraper that:
1. Logs in with credentials
2. Scrapes all document types
3. Saves to universal schema with global IDs
4. Auto-classifies documents by subject
5. Downloads PDFs when available

---

## Phase 1: Manual Setup (YOU DO THIS FIRST) ⚠️

### Step 1: Register for Free Trial

1. Visit https://www.bdlex.com/
2. Click **"Free Trial"** or **"Register Now"**
3. Complete registration form:
   - Email address
   - Password
   - Organization (optional)
4. Verify email (if required)
5. Note your login credentials

### Step 2: Add Credentials to .env

Add these lines to `/workspaces/lool-/data-collection/.env`:

```bash
# ============================================================================
# BDLex.com Authentication
# ============================================================================
BDLEX_USERNAME=your_email@example.com
BDLEX_PASSWORD=your_secure_password_here
BDLEX_BASE_URL=https://www.bdlex.com
```

### Step 3: Explore Site Structure (IMPORTANT!)

After logging in, document the following information:

#### URLs to Document:
```
Login Page URL: _______________________________
Dashboard URL: _______________________________
Case Laws Search: _______________________________
Historical Cases: _______________________________
Statutes Browse: _______________________________
```

#### Features to Check:
- [ ] Search functionality (keyword search, filters)
- [ ] Browse by year
- [ ] Browse by court/jurisdiction
- [ ] Browse by subject/category
- [ ] Pagination (how many results per page?)
- [ ] Document detail page structure
- [ ] PDF download links available?
- [ ] HTML content available?

#### Sample URLs:
```
Example Case URL: _______________________________
Example Statute URL: _______________________________
Search Results URL: _______________________________
```

#### Take Screenshots:
- Login page
- Search interface
- Case detail page
- Statute detail page
- Filters/navigation

**Save all this information** - I'll need it to build the scraper!

---

## Phase 2: Implementation (I WILL BUILD THIS)

### File Structure

```
data-collection/
├── src/
│   ├── scrapers/
│   │   └── bdlex_scraper.py          ← New scraper class
│   └── parsers/
│       └── bdlex_parser.py           ← New parser class
├── config/
│   └── bdlex_config.json             ← Configuration
├── run_bdlex_scraper.py              ← Main script
└── BDLEX_SCRAPER_PLAN.md             ← This file
```

---

### File 1: `src/scrapers/bdlex_scraper.py`

**Purpose:** Main scraper class with authentication

**Key Components:**

```python
"""
BDLex.com Authenticated Scraper
Scrapes legal documents from Bangladesh's premier legal database
"""

from typing import List, Dict, Optional, Any
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base_scraper import BaseLegalScraper
from ..parsers.bdlex_parser import BDLexParser

class BDLexScraper(BaseLegalScraper):
    """
    Authenticated scraper for BDLex.com

    Features:
    - Login with credentials
    - Session management
    - Scrape case laws (1970-present)
    - Scrape historical cases (1870-1969)
    - Scrape statutes/acts/ordinances
    - Save to universal schema
    """

    def __init__(self, config: Dict[str, Any], database):
        super().__init__(config, database)

        # BDLex-specific settings
        self.username = config.get('username')
        self.password = config.get('password')
        self.login_url = config.get('login_url')
        self.is_authenticated = False

        # Initialize parser
        self.parser = BDLexParser()

    def login(self) -> bool:
        """
        Login to BDLex.com using Selenium

        Returns:
            True if login successful, False otherwise
        """
        try:
            self.logger.info("Attempting to login to BDLex.com...")

            # Navigate to login page
            self.driver.get(self.login_url)
            time.sleep(2)

            # Find and fill username field
            username_field = self.driver.find_element(By.ID, "username")  # Update selector
            username_field.send_keys(self.username)

            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "password")  # Update selector
            password_field.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.ID, "login-button")  # Update selector
            login_button.click()

            # Wait for redirect/dashboard
            WebDriverWait(self.driver, 10).until(
                EC.url_changes(self.login_url)
            )

            # Verify login successful
            if "dashboard" in self.driver.current_url or "search" in self.driver.current_url:
                self.is_authenticated = True
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.error("❌ Login failed - unexpected redirect")
                return False

        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            return False

    def get_case_laws(self, start_year: int = 1970, end_year: int = None) -> List[Dict]:
        """
        Scrape Bangladesh case laws

        Args:
            start_year: Starting year (default: 1970)
            end_year: Ending year (default: current year)

        Returns:
            List of case dictionaries
        """
        if not self.is_authenticated:
            if not self.login():
                raise RuntimeError("Authentication required")

        cases = []

        # Navigate to case laws section
        # Implement search/browse logic
        # Parse results
        # Extract case URLs
        # Scrape each case detail page

        return cases

    def get_historical_cases(self) -> List[Dict]:
        """
        Scrape historical cases (1870-1969)
        """
        if not self.is_authenticated:
            if not self.login():
                raise RuntimeError("Authentication required")

        # Implementation here
        pass

    def get_statutes(self) -> List[Dict]:
        """
        Scrape Bangladesh statutes, acts, ordinances
        """
        if not self.is_authenticated:
            if not self.login():
                raise RuntimeError("Authentication required")

        # Implementation here
        pass

    def scrape_document_detail(self, url: str) -> Dict:
        """
        Scrape a single document detail page

        Args:
            url: Document URL

        Returns:
            Dictionary with document data
        """
        html = self.fetch_page(url, use_selenium=True)

        if not html:
            return None

        # Parse with BDLexParser
        doc_data = self.parser.parse_document(html, url)

        return doc_data
```

---

### File 2: `src/parsers/bdlex_parser.py`

**Purpose:** Parse HTML content from BDLex pages

```python
"""
BDLex HTML Parser
Extracts metadata and content from BDLex.com pages
"""

from typing import Dict, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime

from .base_parser import BaseParser

class BDLexParser(BaseParser):
    """
    Parser for BDLex.com HTML content
    """

    def parse_case(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Parse case law page

        Returns:
            Dictionary with case metadata and content
        """
        data = {
            'country_code': 'BD',
            'country_name': 'Bangladesh',
            'doc_category': 'CASE',
            'source_url': url,
            'source_domain': 'bdlex.com'
        }

        # Extract title
        title_elem = soup.find('h1', class_='case-title')  # Update selector
        if title_elem:
            data['title_full'] = title_elem.get_text(strip=True)

        # Extract citation
        citation_elem = soup.find('div', class_='citation')  # Update selector
        if citation_elem:
            data['citation_primary'] = citation_elem.get_text(strip=True)

        # Extract court
        court_elem = soup.find('div', class_='court')  # Update selector
        if court_elem:
            data['court_name'] = court_elem.get_text(strip=True)

        # Extract date
        date_elem = soup.find('div', class_='date')  # Update selector
        if date_elem:
            data['date_enacted'] = self.parse_date(date_elem.get_text(strip=True))

        # Extract judges
        judges_elem = soup.find('div', class_='judges')  # Update selector
        if judges_elem:
            data['judges'] = judges_elem.get_text(strip=True)

        # Extract full text
        text_elem = soup.find('div', class_='judgment-text')  # Update selector
        if text_elem:
            data['html_content'] = str(text_elem)
            data['plain_text'] = text_elem.get_text(strip=True, separator='\n')

        # Extract summary/headnotes
        summary_elem = soup.find('div', class_='headnotes')  # Update selector
        if summary_elem:
            data['summary'] = summary_elem.get_text(strip=True)

        # Extract PDF link
        pdf_link = soup.find('a', href=re.compile(r'\.pdf'))
        if pdf_link:
            data['pdf_url'] = pdf_link['href']

        return data

    def parse_statute(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Parse statute/act page
        """
        data = {
            'country_code': 'BD',
            'country_name': 'Bangladesh',
            'doc_category': 'ACT',
            'source_url': url,
            'source_domain': 'bdlex.com'
        }

        # Extract act title
        title_elem = soup.find('h1', class_='act-title')  # Update selector
        if title_elem:
            data['title_full'] = title_elem.get_text(strip=True)

        # Extract act number
        number_elem = soup.find('div', class_='act-number')  # Update selector
        if number_elem:
            data['doc_number'] = number_elem.get_text(strip=True)

        # Extract year
        year_match = re.search(r'\b(18|19|20)\d{2}\b', data.get('title_full', ''))
        if year_match:
            data['doc_year'] = int(year_match.group(0))

        # Extract full text
        text_elem = soup.find('div', class_='act-text')  # Update selector
        if text_elem:
            data['html_content'] = str(text_elem)
            data['plain_text'] = text_elem.get_text(strip=True, separator='\n')

        # Extract preamble
        preamble_elem = soup.find('div', class_='preamble')  # Update selector
        if preamble_elem:
            data['preamble'] = preamble_elem.get_text(strip=True)

        return data

    def parse_document(self, html: str, url: str) -> Dict:
        """
        Main parse method - detects document type and routes to appropriate parser
        """
        soup = BeautifulSoup(html, 'lxml')

        # Detect document type from URL or page structure
        if '/case/' in url or '/judgment/' in url:
            return self.parse_case(soup, url)
        elif '/act/' in url or '/statute/' in url or '/ordinance/' in url:
            return self.parse_statute(soup, url)
        else:
            # Generic document parsing
            return self.parse_generic(soup, url)

    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        # Implement date parsing logic
        try:
            # Try common date formats
            for fmt in ['%d %B %Y', '%d-%m-%Y', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
        except:
            pass

        return None
```

---

### File 3: `config/bdlex_config.json`

**Purpose:** Configuration for BDLex scraper

```json
{
  "country": "BD",
  "country_name": "Bangladesh",
  "base_url": "https://www.bdlex.com",
  "login_url": "https://www.bdlex.com/login",

  "sections": {
    "case_laws": "/case-laws",
    "historical_cases": "/historical-cases",
    "statutes": "/statutes",
    "search": "/search"
  },

  "scraping": {
    "request_delay": 3,
    "use_selenium": true,
    "headless": true,
    "download_pdfs": true,
    "max_retries": 3,
    "timeout": 30
  },

  "filters": {
    "start_year": 1970,
    "end_year": 2024,
    "courts": ["Supreme Court", "High Court", "Appellate Division"]
  },

  "output": {
    "pdf_dir": "./data/pdfs/BD",
    "html_dir": "./data/html/BD",
    "database": "sqlite:///data/indiankanoon.db"
  },

  "checkpoint": {
    "enabled": true,
    "file": "./data/checkpoints/bdlex_checkpoint.json"
  }
}
```

---

### File 4: `run_bdlex_scraper.py`

**Purpose:** Easy-to-use command-line interface

```python
#!/usr/bin/env python3
"""
BDLex Scraper Runner

Usage:
    python run_bdlex_scraper.py --type all
    python run_bdlex_scraper.py --type cases --start-year 2020 --limit 100
    python run_bdlex_scraper.py --type statutes --limit 50
"""

import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from src.scrapers.bdlex_scraper import BDLexScraper
from src.unified_database import UnifiedDatabase

# Load environment variables
load_dotenv()


def load_config(config_path: str = 'config/bdlex_config.json'):
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Add credentials from environment
    config['username'] = os.getenv('BDLEX_USERNAME')
    config['password'] = os.getenv('BDLEX_PASSWORD')

    if not config['username'] or not config['password']:
        raise ValueError("BDLEX_USERNAME and BDLEX_PASSWORD must be set in .env file")

    return config


def main():
    parser = argparse.ArgumentParser(description='BDLex.com Scraper')

    parser.add_argument(
        '--type',
        choices=['cases', 'historical', 'statutes', 'all'],
        default='all',
        help='Type of documents to scrape'
    )

    parser.add_argument(
        '--start-year',
        type=int,
        default=1970,
        help='Starting year for case laws (default: 1970)'
    )

    parser.add_argument(
        '--end-year',
        type=int,
        default=datetime.now().year,
        help='Ending year for case laws (default: current year)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of documents to scrape (default: no limit)'
    )

    parser.add_argument(
        '--config',
        default='config/bdlex_config.json',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    # Load configuration
    print("Loading configuration...")
    config = load_config(args.config)

    # Initialize database
    print("Connecting to database...")
    db = UnifiedDatabase(config['output']['database'], use_universal=True)

    # Initialize scraper
    print("Initializing BDLex scraper...")
    scraper = BDLexScraper(config, db)

    # Login
    print("\n" + "="*60)
    print("AUTHENTICATION")
    print("="*60)
    if not scraper.login():
        print("❌ Login failed. Please check credentials in .env file.")
        return

    # Start scraping
    print("\n" + "="*60)
    print("SCRAPING")
    print("="*60)

    start_time = datetime.now()
    total_scraped = 0

    # Scrape based on type
    if args.type in ['cases', 'all']:
        print(f"\nScraping case laws ({args.start_year}-{args.end_year})...")
        cases = scraper.get_case_laws(args.start_year, args.end_year)

        if args.limit:
            cases = cases[:args.limit]

        for case in cases:
            # Save to database with universal schema
            db.save_universal_document(case)
            total_scraped += 1

            if total_scraped % 10 == 0:
                print(f"  Scraped {total_scraped} documents...")

    if args.type in ['historical', 'all']:
        print("\nScraping historical cases (1870-1969)...")
        historical = scraper.get_historical_cases()

        if args.limit:
            historical = historical[:args.limit]

        for case in historical:
            db.save_universal_document(case)
            total_scraped += 1

            if total_scraped % 10 == 0:
                print(f"  Scraped {total_scraped} documents...")

    if args.type in ['statutes', 'all']:
        print("\nScraping statutes/acts/ordinances...")
        statutes = scraper.get_statutes()

        if args.limit:
            statutes = statutes[:args.limit]

        for statute in statutes:
            db.save_universal_document(statute)
            total_scraped += 1

            if total_scraped % 10 == 0:
                print(f"  Scraped {total_scraped} documents...")

    # Statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    print(f"Total documents scraped: {total_scraped}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Average: {total_scraped/duration:.2f} docs/second")
    print("="*60)


if __name__ == '__main__':
    main()
```

---

## Phase 3: Testing

### Testing Checklist

#### Authentication Tests
- [ ] Login with valid credentials succeeds
- [ ] Login with invalid credentials fails gracefully
- [ ] Session persists across page navigation
- [ ] Can access authenticated pages after login

#### Scraping Tests
- [ ] Can fetch case laws list
- [ ] Can fetch historical cases list
- [ ] Can fetch statutes list
- [ ] Can scrape individual case detail page
- [ ] Can scrape individual statute detail page
- [ ] Handles missing fields gracefully
- [ ] Handles pagination correctly

#### Database Tests
- [ ] Documents save to `universal_legal_documents` table
- [ ] Global IDs generated correctly (ULEGAL-...)
- [ ] Subject classification works
- [ ] Filenames generated correctly
- [ ] Folder paths generated correctly
- [ ] No duplicate entries created

#### PDF Tests
- [ ] PDF links extracted correctly
- [ ] PDFs download successfully
- [ ] PDF paths saved in database

### Test Commands

```bash
# Test 1: Small sample of case laws
python run_bdlex_scraper.py --type cases --limit 5

# Test 2: Historical cases sample
python run_bdlex_scraper.py --type historical --limit 5

# Test 3: Statutes sample
python run_bdlex_scraper.py --type statutes --limit 5

# Test 4: Verify database
sqlite3 data/indiankanoon.db "SELECT global_id, title_full, doc_category, subject_primary FROM universal_legal_documents WHERE country_code='BD' LIMIT 5;"
```

### Expected Test Output

```
Loading configuration...
Connecting to database...
Initializing BDLex scraper...

============================================================
AUTHENTICATION
============================================================
Attempting to login to BDLex.com...
✅ Login successful!

============================================================
SCRAPING
============================================================

Scraping case laws (2020-2024)...
  Scraped 5 documents...

============================================================
SCRAPING COMPLETE
============================================================
Total documents scraped: 5
Duration: 45.2 seconds
Average: 0.11 docs/second
============================================================
```

---

## Phase 4: Production Scraping

### Pre-Flight Checklist

Before running production scrape:

- [ ] Credentials verified and working
- [ ] Database backup created
- [ ] Sufficient disk space available (estimate: 1-10GB)
- [ ] Stable internet connection
- [ ] Review BDLex terms of service
- [ ] Set appropriate rate limiting (3-5 seconds)
- [ ] Test run completed successfully

### Create Database Backup

```bash
# Backup current database
cp data/indiankanoon.db data/indiankanoon_backup_$(date +%Y%m%d_%H%M%S).db
```

### Production Run Commands

```bash
# Full scrape - ALL content types
python run_bdlex_scraper.py --type all

# Scrape only recent case laws (2020-2024)
python run_bdlex_scraper.py --type cases --start-year 2020

# Scrape only statutes
python run_bdlex_scraper.py --type statutes

# Scrape with limit (for testing)
python run_bdlex_scraper.py --type all --limit 1000
```

### Monitoring Progress

```bash
# Check database count
sqlite3 data/indiankanoon.db "SELECT COUNT(*) FROM universal_legal_documents WHERE country_code='BD';"

# Check by category
sqlite3 data/indiankanoon.db "SELECT doc_category, COUNT(*) FROM universal_legal_documents WHERE country_code='BD' GROUP BY doc_category;"

# Check recent additions
sqlite3 data/indiankanoon.db "SELECT global_id, title_full, doc_category FROM universal_legal_documents WHERE country_code='BD' ORDER BY created_at DESC LIMIT 10;"
```

### Resume After Interruption

The scraper uses checkpoints to resume:

```bash
# Scraping will automatically resume from last checkpoint
python run_bdlex_scraper.py --type all
```

---

## Expected Results

### Database Statistics

After full scrape:

```
Country: BD (Bangladesh)
├── Case Laws (1970-present): ~50,000-100,000 cases
├── Historical Cases (1870-1969): ~10,000-20,000 cases
└── Statutes/Acts/Ordinances: ~500-1,000 documents

Total: ~60,000-120,000 documents
```

### Sample Output

```sql
SELECT * FROM universal_legal_documents WHERE global_id='ULEGAL-0000000701';

global_id:       ULEGAL-0000000701
uuid:            550e8400-e29b-41d4-a716-446655440701
country_code:    BD
country_name:    Bangladesh
doc_category:    CASE
doc_year:        2023
title_full:      State vs. Rahman (Murder Case)
subject_primary: CRIMINAL
subject_code:    CRM
court_level:     HC
court_name:      High Court Division
citation:        2023 BLD (HC) 123
legal_status:    ACTIVE
filename:        BD_CASE_HC_2023_001_State_vs_Rahman_CRM_MUR_ULEGAL-0000000701.pdf
folder_path:     Legal_Database/BD/CASE/
```

---

## Troubleshooting

### Common Issues

#### 1. Login Fails
```
Error: Login failed - unexpected redirect
```

**Solution:**
- Verify credentials in .env file
- Check if free trial expired
- Update login selectors in scraper code
- Check for CAPTCHA or 2FA requirements

#### 2. Empty Results
```
Warning: No documents found
```

**Solution:**
- Verify logged in successfully
- Check URL patterns in config
- Update HTML selectors in parser
- Check if content requires additional navigation

#### 3. Database Errors
```
Error: UNIQUE constraint failed
```

**Solution:**
- Document already exists
- Scraper will skip duplicates
- Check checkpoint to resume

#### 4. Timeout Errors
```
Error: Timeout waiting for element
```

**Solution:**
- Increase timeout in config
- Check internet connection
- Verify page structure hasn't changed

---

## Maintenance

### Updating Selectors

If BDLex.com changes their HTML structure:

1. Inspect updated pages
2. Update selectors in `bdlex_parser.py`
3. Test with small sample
4. Run full scrape

### Adding New Features

To add new document types:

1. Add new method to `BDLexScraper` class
2. Add parser method to `BDLexParser` class
3. Update config with new section URLs
4. Add command-line option to runner script

---

## Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Register for BDLex | 30 mins | ⏳ TODO |
| 1 | Explore site structure | 30 mins | ⏳ TODO |
| 2 | Build scraper | 2-3 hours | ⏳ TODO |
| 2 | Build parser | 1-2 hours | ⏳ TODO |
| 2 | Create runner script | 30 mins | ⏳ TODO |
| 3 | Test authentication | 15 mins | ⏳ TODO |
| 3 | Test scraping | 30 mins | ⏳ TODO |
| 3 | Verify database | 15 mins | ⏳ TODO |
| 4 | Production scrape | 2-8 hours | ⏳ TODO |
| 4 | Validation | 30 mins | ⏳ TODO |

**Total Estimated Time:** 8-16 hours (including scraping time)

---

## Next Steps

### Immediate Actions (YOU)

1. ✅ **Read this plan** completely
2. ⏳ **Register** for BDLex free trial → Get credentials
3. ⏳ **Add credentials** to `.env` file
4. ⏳ **Explore site** structure (URLs, selectors, navigation)
5. ⏳ **Document findings** (URLs, selectors, pagination)
6. ⏳ **Share findings** with me so I can build the scraper

### Implementation Actions (ME)

7. ⏳ **Create** `bdlex_scraper.py` with your site structure info
8. ⏳ **Create** `bdlex_parser.py` with correct selectors
9. ⏳ **Create** `run_bdlex_scraper.py` command-line interface
10. ⏳ **Test** with small sample
11. ⏳ **Debug** and fix issues
12. ⏳ **Run** production scrape

---

## Resources

### Documentation Links
- BDLex.com: https://www.bdlex.com/
- Selenium Python: https://selenium-python.readthedocs.io/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Your existing scrapers: `src/scrapers/bangladesh_scraper.py`

### Support
- BDLex Support: Check their website for contact info
- Technical Issues: Document and share with me

---

## Notes

- **Legal & Ethical:** Ensure compliance with BDLex terms of service
- **Rate Limiting:** 3-5 second delays between requests to be respectful
- **Data Quality:** Validate sample before full scrape
- **Backup:** Always backup database before production runs
- **Monitoring:** Check progress regularly during scraping

---

**Plan Status:** Ready to execute Phase 1
**Last Updated:** October 22, 2025
**Next Review:** After Phase 1 completion

---

## Questions?

If you have questions or need clarification:
1. Review relevant section above
2. Check existing scrapers for examples
3. Ask me specific questions

**Ready to start?** Complete Phase 1 (registration) and share your findings!
