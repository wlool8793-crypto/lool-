# IndianKanoon Data Collection System

A comprehensive web scraping system for collecting legal case data from [IndianKanoon.org](https://indiankanoon.org/), India's premier legal search engine.

## Features

- **Multi-level scraping**: Search results, case details, and PDF downloads
- **Flexible search**: Filter by court, year, keywords
- **Database storage**: SQLite/PostgreSQL support with SQLAlchemy
- **Rate limiting**: Configurable delays to respect server resources
- **Robust error handling**: Logging and recovery mechanisms
- **PDF management**: Automated document downloads
- **Statistics tracking**: Monitor scraping progress

## Architecture

The system uses:
- **BeautifulSoup** for HTML parsing
- **Selenium** for JavaScript-heavy pages
- **SQLAlchemy** for database operations
- **Requests** for HTTP requests

## Installation

1. **Navigate to project directory:**
```bash
cd data-collection
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Basic Search

Search Supreme Court cases:
```bash
python main.py --query "criminal law" --doc-type supremecourt --max-pages 5
```

### Search by Year

Search cases from a specific year:
```bash
python main.py --year 2023 --doc-type supremecourt
```

### Scrape Year Range

Scrape multiple years:
```bash
python main.py --start-year 2020 --end-year 2023 --doc-type supremecourt --max-pages 10
```

### Fetch Full Case Details

Get complete case information for stored cases:
```bash
python main.py --fetch-details
```

### Download PDFs

Download PDF documents for cases:
```bash
python main.py --download-pdfs
```

### View Statistics

Check database statistics:
```bash
python main.py --stats
```

### Combined Operations

Scrape and fetch details in one command:
```bash
python main.py --query "constitutional law" --year 2023 --fetch-details --max-pages 5
```

## Project Structure

```
data-collection/
├── src/
│   ├── __init__.py
│   ├── scraper.py       # Web scraping logic
│   └── database.py      # Database operations
├── data/
│   ├── pdfs/           # Downloaded PDF files
│   └── indiankanoon.db # SQLite database
├── logs/
│   └── scraper.log     # Application logs
├── main.py             # Main application
├── requirements.txt    # Dependencies
├── .env.example        # Configuration template
└── README.md          # Documentation
```

## Configuration (.env)

```bash
# Database
DATABASE_URL=sqlite:///data/indiankanoon.db

# Scraping
BASE_URL=https://indiankanoon.org
HEADLESS_MODE=true
DOWNLOAD_PDFS=true
PDF_DOWNLOAD_PATH=./data/pdfs
REQUEST_DELAY=2

# Search defaults
START_YEAR=2020
END_YEAR=2024
COURTS=supremecourt,highcourt

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/scraper.log
```

## Document Types

Available document types for scraping:
- `supremecourt` - Supreme Court of India
- `highcourt` - High Courts
- `tribunal` - Tribunals
- `district` - District Courts

## Data Model

Cases are stored with the following fields:
- `case_url` - Unique case URL
- `title` - Case title
- `citation` - Legal citation
- `court` - Court name
- `case_date` - Date of judgment
- `snippet` - Case summary
- `full_text` - Complete judgment text
- `pdf_link` - PDF download URL
- `pdf_downloaded` - Download status
- `pdf_path` - Local PDF path

## Search Examples

**Criminal cases from 2023:**
```bash
python main.py --query "criminal" --year 2023 --max-pages 20
```

**Constitutional law cases:**
```bash
python main.py --query "constitutional" --doc-type supremecourt
```

**High Court cases:**
```bash
python main.py --query "property" --doc-type highcourt --year 2022
```

**Multi-year scraping:**
```bash
python main.py --start-year 2018 --end-year 2023 --max-pages 50
```

## Rate Limiting

The scraper includes built-in delays between requests (default: 2 seconds) to:
- Respect server resources
- Avoid IP blocking
- Ensure sustainable scraping

Adjust `REQUEST_DELAY` in `.env` if needed.

## Database Queries

Access the database directly:

```python
from src.database import CaseDatabase

db = CaseDatabase('sqlite:///data/indiankanoon.db')

# Get recent cases
cases = db.get_cases(limit=10)

# Get cases by court
supreme_cases = db.get_cases(court='Supreme Court')

# Get statistics
stats = db.get_statistics()
print(stats)
```

## Logging

Logs are written to:
- Console (stdout)
- `logs/scraper.log` file

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Legal & Ethical Considerations

- **Respect robots.txt**: Check site policies
- **Rate limiting**: Use appropriate delays
- **Fair use**: Only collect publicly available data
- **Attribution**: Cite IndianKanoon.org as data source
- **Purpose**: Use for research, education, or legal analysis only

## Troubleshooting

**Selenium driver issues:**
```bash
pip install --upgrade selenium webdriver-manager
```

**Database locked:**
- Close other connections to the database
- Use PostgreSQL for concurrent access

**Memory issues with large scrapes:**
- Process data in smaller batches
- Increase REQUEST_DELAY
- Reduce MAX_PAGES

## Advanced Usage

### Custom Database

Use PostgreSQL for production:
```bash
DATABASE_URL=postgresql://user:password@localhost/indiankanoon
```

### Scheduled Scraping

Use cron for automated scraping:
```bash
# Daily scrape at 2 AM
0 2 * * * cd /path/to/data-collection && /path/to/venv/bin/python main.py --year $(date +\%Y)
```

## Contributing

Contributions welcome! Areas for improvement:
- Additional courts/tribunals support
- Advanced search filters
- Export formats (CSV, JSON, Excel)
- Analytics and visualization
- API endpoint creation

## Disclaimer

This tool is for educational and research purposes. Ensure compliance with:
- IndianKanoon.org terms of service
- Copyright laws
- Data protection regulations

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check logs in `logs/scraper.log`
2. Review configuration in `.env`
3. Verify network connectivity
4. Check IndianKanoon.org accessibility

## Resources

- **IndianKanoon**: https://indiankanoon.org/
- **Legal Research**: https://indiankanoon.org/about.html
- **API Documentation**: Contact IndianKanoon for official API access
