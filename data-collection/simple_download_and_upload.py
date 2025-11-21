#!/usr/bin/env python3
"""
Simple Sequential Download Script for IndianKanoon Cases
Very conservative approach to avoid rate limiting - 1 request every 10 seconds.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper import IndianKanoonScraper
from src.database import CaseDatabase

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f'simple_download_{timestamp}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)



def simple_download():
    """Download all PDFs sequentially with very conservative rate limiting."""

    print("=" * 80)
    print("INDIANKANOON SIMPLE SEQUENTIAL PDF DOWNLOAD")
    print("=" * 80)
    print("Conservative mode: 1 request every 10 seconds to avoid rate limiting")
    print("=" * 80)
    print()

    # Initialize database
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/indiankanoon.db')
    db = CaseDatabase(db_url)

    # Configuration
    delay = 10  # 10 seconds between requests (ultra conservative)
    pdf_dir = Path(os.getenv('PDF_DOWNLOAD_PATH', './data/pdfs'))
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Initialize scraper
    scraper = IndianKanoonScraper(delay=delay, headless=True)

    # Get initial statistics
    stats = db.get_statistics()
    logger.info(f"Database Statistics:")
    logger.info(f"  Total cases: {stats['total_cases']}")
    logger.info(f"  Cases with PDFs: {stats['cases_with_pdfs']}")
    logger.info(f"  Cases without PDFs: {stats['cases_without_pdfs']}")
    print()

    # Get cases that need PDF downloads
    from src.database import LegalCase
    query = db.session.query(LegalCase).filter(
        (LegalCase.pdf_downloaded == False) | (LegalCase.pdf_downloaded == None)
    ).limit(600)

    cases_to_process = list(query)
    total_cases = len(cases_to_process)

    logger.info(f"Found {total_cases} cases to process")
    print()

    # Statistics tracking
    stats_counters = {
        'details_fetched': 0,
        'pdfs_downloaded': 0,
        'already_downloaded': 0,
        'no_pdf_available': 0,
        'failed': 0,
        'processed': 0
    }

    start_time = time.time()

    # Process cases one by one
    for idx, case in enumerate(cases_to_process, 1):
        logger.info(f"\\n[{idx}/{total_cases}] Processing case {case.id}")

        try:
            # Step 1: Fetch case details if needed
            if not case.pdf_link:
                logger.info(f"  Fetching details from: {case.case_url[:80]}...")
                time.sleep(delay)  # Rate limiting

                try:
                    details = scraper.get_case_details(case.case_url)
                    if details and details.get('pdf_link'):
                        case.pdf_link = details['pdf_link']
                        case.full_text = details.get('full_text', case.full_text)
                        case.citation = details.get('citation', case.citation)
                        case.court = details.get('court', case.court)

                        db.session.commit()
                        stats_counters['details_fetched'] += 1

                        logger.info(f"  ✓ Details fetched, PDF available")
                    else:
                        stats_counters['no_pdf_available'] += 1
                        logger.warning(f"  ✗ No PDF available for this case")
                        stats_counters['processed'] += 1
                        continue
                except Exception as e:
                    stats_counters['failed'] += 1
                    logger.error(f"  ✗ Error fetching details: {str(e)[:100]}")
                    stats_counters['processed'] += 1
                    continue

            # Step 2: Download PDF if available
            if case.pdf_link:
                filename = f"case_{case.id}.pdf"
                filepath = pdf_dir / filename

                # Check if already downloaded
                if case.pdf_downloaded and filepath.exists():
                    file_size = os.path.getsize(filepath)
                    stats_counters['already_downloaded'] += 1
                    logger.info(f"  ↓ Already downloaded ({file_size/1024:.1f} KB)")
                    stats_counters['processed'] += 1
                    continue

                # Download PDF
                logger.info(f"  Downloading PDF...")
                time.sleep(delay)  # Rate limiting

                try:
                    success = scraper.download_indiankanoon_pdf(case.pdf_link, str(filepath))

                    if success and filepath.exists():
                        file_size = os.path.getsize(filepath)
                        db.update_pdf_status(case.id, str(filepath))
                        stats_counters['pdfs_downloaded'] += 1
                        logger.info(f"  ✓ Downloaded successfully ({file_size/1024:.1f} KB)")
                    else:
                        stats_counters['failed'] += 1
                        logger.warning(f"  ✗ Download failed")
                except Exception as e:
                    stats_counters['failed'] += 1
                    logger.error(f"  ✗ Error downloading: {str(e)[:100]}")

            stats_counters['processed'] += 1

            # Progress update every 10 cases
            if idx % 10 == 0:
                elapsed = time.time() - start_time
                rate = stats_counters['pdfs_downloaded'] / (elapsed / 60) if elapsed > 0 else 0
                est_remaining = ((total_cases - idx) * delay * 2) / 3600  # Estimate hours remaining
                logger.info(f"\\n{'='*60}")
                logger.info(f"Progress: {idx}/{total_cases} ({idx/total_cases*100:.1f}%)")
                logger.info(f"  New downloads: {stats_counters['pdfs_downloaded']}")
                logger.info(f"  Already had: {stats_counters['already_downloaded']}")
                logger.info(f"  No PDF: {stats_counters['no_pdf_available']}")
                logger.info(f"  Failed: {stats_counters['failed']}")
                logger.info(f"  Download rate: {rate:.1f} PDFs/min")
                logger.info(f"  Elapsed: {elapsed/60:.1f} min | Est. remaining: {est_remaining:.1f} hrs")
                logger.info(f"{'='*60}\\n")

        except Exception as e:
            logger.error(f"  ✗ Unexpected error: {str(e)[:100]}")
            stats_counters['failed'] += 1
            stats_counters['processed'] += 1

    # Final statistics
    elapsed_time = time.time() - start_time
    final_stats = db.get_statistics()

    print("\\n" + "=" * 80)
    print("DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"\\nDatabase Statistics:")
    print(f"  Total cases: {final_stats['total_cases']}")
    print(f"  Cases with PDFs: {final_stats['cases_with_pdfs']}")
    print(f"  Cases without PDFs: {final_stats['cases_without_pdfs']}")
    print(f"\\nSession Statistics:")
    print(f"  Details fetched: {stats_counters['details_fetched']}")
    print(f"  PDFs downloaded: {stats_counters['pdfs_downloaded']}")
    print(f"  Already had PDFs: {stats_counters['already_downloaded']}")
    print(f"  No PDF available: {stats_counters['no_pdf_available']}")
    print(f"  Failed: {stats_counters['failed']}")
    print(f"\\nPerformance:")
    print(f"  Time elapsed: {elapsed_time/60:.1f} minutes ({elapsed_time/3600:.1f} hours)")
    if elapsed_time > 0:
        print(f"  Download rate: {stats_counters['pdfs_downloaded']/(elapsed_time/60):.1f} PDFs/min")
    print(f"  Log file: {log_file}")
    print("=" * 80)

    # Cleanup
    scraper.close_driver()
    db.close()

    return 0


if __name__ == "__main__":
    try:
        exit_code = simple_download()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
