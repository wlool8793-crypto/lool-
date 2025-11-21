#!/usr/bin/env python3
"""
Bangladesh Laws Full Site Scraper
==================================
Comprehensive scraper for http://bdlaws.minlaw.gov.bd/

Features:
- Scrapes ALL laws from both chronological and alphabetical indexes
- Universal naming convention
- Progress tracking with tqdm
- Checkpoint/resume capability
- File organization
- PDF downloads
- Comprehensive logging
- Statistics reporting

Usage:
    python scrape_bangladesh_full.py                    # Full scrape
    python scrape_bangladesh_full.py --test             # Test mode (5 docs)
    python scrape_bangladesh_full.py --limit 100        # Limit to 100 docs
    python scrape_bangladesh_full.py --start-from 50    # Resume from index 50
    python scrape_bangladesh_full.py --no-pdfs          # Skip PDF downloads
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.scrapers.bangladesh_scraper import BangladeshLawsScraper
from src.unified_database import UnifiedDatabase
from src.naming.id_generator import IDGenerator
from src.naming.universal_namer import UniversalNamer
from src.taxonomy.subjects import SubjectClassifier
from src.file_organizer import FileOrganizer
from src.utils import parse_roman_numeral, sanitize_filename, format_file_size


class BangladeshFullScraper:
    """Comprehensive Bangladesh Laws scraper with all features"""

    def __init__(self, config: dict):
        self.config = config
        self.start_time = datetime.now()
        self.stats = {
            'total_urls': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'pdfs_downloaded': 0,
            'errors': []
        }

        # Setup logging
        self._setup_logging()

        # Initialize components
        self.logger.info("Initializing components...")
        self.db = UnifiedDatabase('data/indiankanoon.db', use_universal=True)
        self.scraper = BangladeshLawsScraper(config, self.db)
        self.id_gen = IDGenerator('data/indiankanoon.db')
        self.namer = UniversalNamer()
        self.classifier = SubjectClassifier()
        self.organizer = FileOrganizer()

        # Checkpoint file
        self.checkpoint_file = Path('data/checkpoints/bangladesh_scrape.json')
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"bangladesh_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging to: {log_file}")

    def load_checkpoint(self) -> dict:
        """Load checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                    self.logger.info(f"Loaded checkpoint: {checkpoint.get('processed', 0)} documents processed")
                    return checkpoint
            except Exception as e:
                self.logger.warning(f"Could not load checkpoint: {e}")

        return {'processed': 0, 'processed_urls': []}

    def save_checkpoint(self, processed: int, processed_urls: list):
        """Save checkpoint"""
        checkpoint = {
            'processed': processed,
            'processed_urls': processed_urls,
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats
        }

        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save checkpoint: {e}")

    def scrape_all(self, limit: int = None, start_from: int = 0):
        """Scrape all Bangladesh laws"""

        print("\n" + "="*80)
        print("BANGLADESH LAWS FULL SITE SCRAPER")
        print("="*80)
        print(f"Source: http://bdlaws.minlaw.gov.bd/")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: data/indiankanoon.db (universal schema)")
        print("="*80)

        # PHASE 1: Discover all documents
        print("\n📋 PHASE 1: DISCOVERING DOCUMENTS")
        print("-" * 80)

        self.logger.info("Fetching document list from indexes...")
        all_urls = self.scraper.get_document_list()

        if not all_urls:
            self.logger.error("No URLs found! Check the website structure.")
            return

        self.stats['total_urls'] = len(all_urls)

        print(f"✓ Found {len(all_urls)} unique documents")
        print(f"  - Chronological index")
        print(f"  - Alphabetical index")

        # Apply limit and start_from
        if start_from > 0:
            all_urls = all_urls[start_from:]
            print(f"  Starting from index {start_from}")

        if limit:
            all_urls = all_urls[:limit]
            print(f"  Limited to {limit} documents")

        print(f"\n📊 Will process {len(all_urls)} documents")

        # PHASE 2: Scrape documents
        print("\n📥 PHASE 2: SCRAPING DOCUMENTS")
        print("-" * 80)

        # Load checkpoint
        checkpoint = self.load_checkpoint()
        processed_urls = set(checkpoint.get('processed_urls', []))

        # Progress bar
        with tqdm(total=len(all_urls), desc="Scraping", unit="doc") as pbar:
            for idx, url in enumerate(all_urls):
                # Skip if already processed
                if url in processed_urls:
                    pbar.update(1)
                    self.stats['skipped'] += 1
                    continue

                try:
                    # Parse document
                    doc_data = self.scraper.parse_document(url)

                    if not doc_data:
                        self.stats['failed'] += 1
                        pbar.update(1)
                        continue

                    # Enhance with universal schema
                    doc_data = self._enhance_for_universal(doc_data)

                    # Save to database
                    try:
                        doc_id = self.db.save_universal_document(doc_data)
                        self.stats['successful'] += 1

                        # Download PDF if enabled
                        if self.config.get('download_pdfs') and doc_data.get('pdf_url'):
                            success = self._download_pdf(doc_data, doc_id)
                            if success:
                                self.stats['pdfs_downloaded'] += 1

                    except Exception as e:
                        self.logger.error(f"Error saving document: {e}")
                        self.stats['failed'] += 1

                    processed_urls.add(url)
                    self.stats['processed'] += 1

                    # Save checkpoint every 10 documents
                    if self.stats['processed'] % 10 == 0:
                        self.save_checkpoint(self.stats['processed'], list(processed_urls))

                    # Update progress
                    pbar.set_postfix({
                        'Success': self.stats['successful'],
                        'Failed': self.stats['failed'],
                        'PDFs': self.stats['pdfs_downloaded']
                    })

                except Exception as e:
                    self.logger.error(f"Error processing {url}: {e}")
                    self.stats['failed'] += 1
                    self.stats['errors'].append({
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })

                finally:
                    pbar.update(1)

                # Rate limiting
                time.sleep(self.config.get('request_delay', 2))

        # Final checkpoint
        self.save_checkpoint(self.stats['processed'], list(processed_urls))

        # PHASE 3: Report statistics
        self._print_final_report()

    def _enhance_for_universal(self, doc_data: dict) -> dict:
        """Enhance document data for universal schema"""

        # Add country code
        doc_data['country_code'] = 'BD'
        doc_data['country_name'] = 'Bangladesh'

        # Determine document category
        doc_type = doc_data.get('doc_type', 'ACT')
        if 'ordinance' in doc_type.lower():
            doc_data['doc_category'] = 'ORDINANCE'
        elif 'rule' in doc_type.lower():
            doc_data['doc_category'] = 'RULE'
        elif 'order' in doc_type.lower():
            doc_data['doc_category'] = 'ORDER'
        else:
            doc_data['doc_category'] = 'ACT'

        # Jurisdiction
        doc_data['jurisdiction_level'] = 'CENTRAL'

        # Extract year
        if not doc_data.get('year') or doc_data.get('year') == 0:
            # Try to extract from title
            title = doc_data.get('title', '')
            import re
            year_match = re.search(r'\b(1[7-9]\d{2}|20\d{2})\b', title)
            if year_match:
                doc_data['year'] = int(year_match.group(1))

        doc_data['doc_year'] = doc_data.get('year', 0)

        # Extract act number
        citation = doc_data.get('citation', '')
        if citation:
            # Try to extract Roman numeral
            roman_match = re.search(r'\b([IVXLCDM]+)\b', citation)
            if roman_match:
                doc_data['doc_number'] = roman_match.group(1)
                # Convert to decimal
                decimal = parse_roman_numeral(doc_data['doc_number'])
                if decimal:
                    doc_data['official_number_decimal'] = decimal

        # Title
        doc_data['title_full'] = doc_data.get('title', 'Untitled')
        doc_data['title_short'] = self._create_short_title(doc_data['title_full'])

        # Subject classification
        subject_info = self.classifier.classify(
            title=doc_data['title_full'],
            content=doc_data.get('plain_text', ''),
            country_code='BD'
        )

        if subject_info:
            doc_data['subject_primary'] = subject_info[0]
            doc_data['subject_subcategory'] = subject_info[1]
            doc_data['subject_code'] = subject_info[2]

        # Legal status
        doc_data['legal_status'] = 'ACTIVE'

        # Source info
        doc_data['source_domain'] = 'bdlaws.minlaw.gov.bd'

        return doc_data

    def _create_short_title(self, full_title: str) -> str:
        """Create short title from full title"""
        # Remove common patterns
        short = full_title.replace('The ', '').replace(' Act', '').replace(' Ordinance', '')

        # Remove year if present
        import re
        short = re.sub(r',?\s*\d{4}', '', short)

        # Truncate to 50 chars
        if len(short) > 50:
            short = short[:47] + '...'

        return short.strip()

    def _download_pdf(self, doc_data: dict, doc_id: int) -> bool:
        """Download PDF for document"""
        pdf_url = doc_data.get('pdf_url')
        if not pdf_url:
            return False

        try:
            # Generate filename
            filename = self.namer.generate_filename(doc_data)
            if not filename.endswith('.pdf'):
                filename += '.pdf'

            # Download to temp
            temp_dir = Path('data/temp_pdfs')
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_path = temp_dir / filename

            # Download
            success = self.scraper.download_pdf(pdf_url, str(temp_path))

            if success and temp_path.exists():
                # Move to final location
                final_path = self.organizer.move_temp_to_final(
                    temp_path=temp_path,
                    filename=filename,
                    metadata=doc_data,
                    validate_hash=True
                )

                if final_path:
                    # Update database
                    doc_data['pdf_path'] = str(final_path)
                    doc_data['pdf_downloaded'] = True
                    return True

        except Exception as e:
            self.logger.error(f"Error downloading PDF: {e}")

        return False

    def _print_final_report(self):
        """Print final statistics report"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print("\n" + "="*80)
        print("SCRAPING COMPLETE - FINAL REPORT")
        print("="*80)

        print(f"\n⏱️  Duration: {duration}")
        print(f"📊 Total URLs Found: {self.stats['total_urls']}")
        print(f"✓  Successfully Scraped: {self.stats['successful']}")
        print(f"✗  Failed: {self.stats['failed']}")
        print(f"⏭️  Skipped (already done): {self.stats['skipped']}")
        print(f"📄 PDFs Downloaded: {self.stats['pdfs_downloaded']}")

        if self.stats['successful'] > 0:
            success_rate = (self.stats['successful'] / self.stats['processed']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            print("   (Check log file for details)")

        print("\n💾 Database: data/indiankanoon.db")
        print(f"📁 PDFs: Legal_Database/BD/")
        print(f"📝 Logs: logs/")
        print(f"🔖 Checkpoint: {self.checkpoint_file}")

        print("\n" + "="*80)

        # Save final stats
        stats_file = Path('logs') / f"bangladesh_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            print(f"📊 Statistics saved to: {stats_file}")
        except Exception as e:
            self.logger.error(f"Could not save statistics: {e}")

        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive Bangladesh Laws Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scrape_bangladesh_full.py                    # Scrape all documents
  python scrape_bangladesh_full.py --test             # Test mode (5 docs)
  python scrape_bangladesh_full.py --limit 100        # Scrape 100 docs
  python scrape_bangladesh_full.py --start-from 50    # Resume from index 50
  python scrape_bangladesh_full.py --no-pdfs          # Skip PDF downloads
        """
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - only scrape first 5 documents'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of documents to scrape'
    )

    parser.add_argument(
        '--start-from',
        type=int,
        default=0,
        help='Start from index (for resuming)'
    )

    parser.add_argument(
        '--no-pdfs',
        action='store_true',
        help='Skip PDF downloads (metadata only)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )

    args = parser.parse_args()

    # Test mode
    if args.test:
        args.limit = 5
        args.start_from = 0
        print("🧪 TEST MODE: Scraping only 5 documents\n")

    # Configuration
    config = {
        'country': 'bangladesh',
        'base_url': 'http://bdlaws.minlaw.gov.bd',
        'request_delay': args.delay,
        'use_selenium': False,
        'headless': True,
        'download_pdfs': not args.no_pdfs,
        'pdf_dir': './Legal_Database/BD/ACT/',
        'html_dir': './data/html/bangladesh',
        'indexes': {
            'chronological': '/laws-of-bangladesh-chronological-index.html',
            'alphabetical': '/laws-of-bangladesh-alphabetical-index.html'
        }
    }

    try:
        # Create scraper
        scraper = BangladeshFullScraper(config)

        # Run scraping
        scraper.scrape_all(
            limit=args.limit,
            start_from=args.start_from
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Progress has been checkpointed.")
        print("   Resume with: python scrape_bangladesh_full.py --start-from N")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
