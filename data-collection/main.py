"""
IndianKanoon Data Collection System
Main application for scraping legal cases from indiankanoon.org
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.scraper import IndianKanoonScraper
from src.database import CaseDatabase
import argparse

# Load environment variables
load_dotenv()

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/scraper.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def scrape_search_results(scraper, db, query, year=None, doc_type='supremecourt', max_pages=10):
    """
    Scrape search results and save to database.

    Args:
        scraper: IndianKanoonScraper instance
        db: CaseDatabase instance
        query: Search query
        year: Year filter
        doc_type: Document type
        max_pages: Maximum pages to scrape
    """
    logger.info(f"Starting search: query='{query}', year={year}, doc_type={doc_type}")

    all_cases = []
    for page in range(max_pages):
        cases = scraper.search_cases(query, year=year, doc_type=doc_type, page=page)

        if not cases:
            logger.info(f"No more results found at page {page}")
            break

        all_cases.extend(cases)
        logger.info(f"Page {page}: Found {len(cases)} cases")

        # Save to database
        saved = db.bulk_save_cases(cases)
        logger.info(f"Saved {saved} new cases to database")

    logger.info(f"Total cases found: {len(all_cases)}")
    return all_cases


def scrape_case_details(scraper, db, limit=100):
    """
    Scrape full details for cases that only have basic info.

    Args:
        scraper: IndianKanoonScraper instance
        db: CaseDatabase instance
        limit: Maximum number of cases to process
    """
    logger.info(f"Fetching detailed information for cases...")

    cases = db.get_cases(limit=limit)
    processed = 0
    failed = 0
    total = len(cases)

    for i, case in enumerate(cases, 1):
        if not case.full_text:  # Only fetch if we don't have full text
            logger.info(f"[{i}/{total}] Fetching details for: {case.case_url}")

            try:
                details = scraper.get_case_details(case.case_url)

                if details:
                    case.full_text = details.get('full_text', '')
                    case.citation = details.get('citation', case.citation)
                    case.court = details.get('court', case.court)
                    case.pdf_link = details.get('pdf_link', case.pdf_link)
                    db.session.commit()
                    processed += 1
                    logger.info(f"[{i}/{total}] ✓ Success")
                else:
                    failed += 1
                    logger.warning(f"[{i}/{total}] ✗ Failed to get details")
            except Exception as e:
                failed += 1
                logger.error(f"[{i}/{total}] ✗ Error: {e}")
                continue

    logger.info(f"Processed {processed} case details, {failed} failed")


def download_pdfs(scraper, db, limit=100):
    """
    Download PDFs for cases that have PDF links with progress tracking.

    Args:
        scraper: IndianKanoonScraper instance
        db: CaseDatabase instance
        limit: Maximum number of PDFs to download
    """
    if not os.getenv('DOWNLOAD_PDFS', 'false').lower() == 'true':
        logger.info("PDF download is disabled")
        return

    logger.info(f"Downloading PDFs...")

    pdf_dir = Path(os.getenv('PDF_DOWNLOAD_PATH', './data/pdfs'))
    pdf_dir.mkdir(parents=True, exist_ok=True)

    cases = db.get_cases_without_pdfs(limit=limit)
    downloaded = 0
    failed = 0
    skipped = 0
    total = len(cases)

    logger.info(f"Found {total} cases to process")

    for i, case in enumerate(cases, 1):
        if not case.pdf_link:
            skipped += 1
            logger.warning(f"[{i}/{total}] Case {case.id}: No PDF link available")
            continue

        # Generate filename from case ID
        filename = f"case_{case.id}.pdf"
        filepath = pdf_dir / filename

        # Skip if already exists (resumption support)
        if filepath.exists():
            logger.info(f"[{i}/{total}] Case {case.id}: PDF already exists, skipping")
            skipped += 1
            continue

        logger.info(f"[{i}/{total}] Downloading PDF for case {case.id}: {case.title[:50]}...")

        try:
            # Use IndianKanoon-specific PDF download method with retry
            success = scraper.download_indiankanoon_pdf(case.pdf_link, str(filepath))

            if success:
                db.update_pdf_status(case.id, str(filepath))
                downloaded += 1
                logger.info(f"[{i}/{total}] ✓ Success ({os.path.getsize(filepath)/1024:.1f} KB)")
            else:
                failed += 1
                logger.warning(f"[{i}/{total}] ✗ Failed after retries")
        except Exception as e:
            failed += 1
            logger.error(f"[{i}/{total}] ✗ Error: {e}")
            continue

    logger.info(f"PDF Download Summary: {downloaded} downloaded, {failed} failed, {skipped} skipped")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='IndianKanoon Data Scraper')
    parser.add_argument('--query', type=str, default='', help='Search query')
    parser.add_argument('--year', type=int, help='Filter by year')
    parser.add_argument('--start-year', type=int, help='Start year for range scraping')
    parser.add_argument('--end-year', type=int, help='End year for range scraping')
    parser.add_argument('--doc-type', type=str, default='supremecourt',
                       help='Document type (supremecourt, highcourt, etc.)')
    parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to scrape')
    parser.add_argument('--fetch-details', action='store_true', help='Fetch full case details')
    parser.add_argument('--download-pdfs', action='store_true', help='Download PDFs')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("IndianKanoon Data Collection System Started")
    logger.info("=" * 70)

    # Initialize database
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/indiankanoon.db')
    db = CaseDatabase(db_url)

    # Show statistics
    if args.stats:
        stats = db.get_statistics()
        print("\n" + "=" * 70)
        print("DATABASE STATISTICS")
        print("=" * 70)
        print(f"Total Cases: {stats['total_cases']}")
        print(f"Cases with PDFs: {stats['cases_with_pdfs']}")
        print(f"Cases without PDFs: {stats['cases_without_pdfs']}")
        print(f"Unique Courts: {stats['unique_courts']}")
        print(f"Courts: {', '.join(stats['courts'][:5])}...")
        print("=" * 70 + "\n")

    # Initialize scraper
    headless = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
    delay = int(os.getenv('REQUEST_DELAY', '2'))

    with IndianKanoonScraper(headless=headless, delay=delay) as scraper:

        # Scrape by year range
        if args.start_year and args.end_year:
            logger.info(f"Scraping year range: {args.start_year} to {args.end_year}")
            for year in range(args.start_year, args.end_year + 1):
                scrape_search_results(scraper, db, args.query, year=year,
                                    doc_type=args.doc_type, max_pages=args.max_pages)

        # Scrape with query
        elif args.query or args.year:
            scrape_search_results(scraper, db, args.query, year=args.year,
                                doc_type=args.doc_type, max_pages=args.max_pages)

        # Fetch details for existing cases
        if args.fetch_details:
            scrape_case_details(scraper, db, limit=100)

        # Download PDFs
        if args.download_pdfs:
            download_pdfs(scraper, db, limit=100)

    # Final statistics
    stats = db.get_statistics()
    print("\n" + "=" * 70)
    print("SCRAPING COMPLETED - FINAL STATISTICS")
    print("=" * 70)
    print(f"Total Cases in Database: {stats['total_cases']}")
    print(f"Cases with PDFs: {stats['cases_with_pdfs']}")
    print("=" * 70 + "\n")

    db.close()
    logger.info("IndianKanoon Data Collection System Finished")


if __name__ == "__main__":
    main()
