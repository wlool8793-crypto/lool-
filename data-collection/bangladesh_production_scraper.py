#!/usr/bin/env python3
"""
Bangladesh Laws Production Scraper
Integrated scraper for bdlaws.minlaw.gov.bd with PostgreSQL and Google Drive

Features:
- Fetches all laws from bdlaws.minlaw.gov.bd
- Stores metadata in PostgreSQL
- Downloads PDFs (or generates from HTML)
- Uploads to Google Drive with organized folder structure
- Checkpointing and resume capability
"""

import os
import sys
import re
import json
import time
import yaml
import signal
import logging
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.postgresql_adapter import PostgreSQLAdapter

# Try to import Drive manager
try:
    from scraper.drive_manager import DriveManager
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False
    DriveManager = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bangladesh_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProgressState:
    """Tracks scraping progress"""
    total_documents: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    start_time: float = 0.0


class BangladeshProductionScraper:
    """Production scraper for Bangladesh Laws with PostgreSQL and Drive integration"""

    def __init__(self, config_path: str = "config/config_bangladesh.yaml"):
        """Initialize scraper with configuration"""
        self.config = self._load_config(config_path)

        # Database adapter
        self.db = self._init_database()

        # Google Drive manager
        self.drive_manager = None
        if DRIVE_AVAILABLE and self.config.get('google_drive', {}).get('enabled', False):
            self._init_drive()

        # Paths
        self.pdf_dir = Path(self.config['storage']['pdf_dir'])
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        # State management
        self.state = ProgressState()
        self.checkpoint_file = Path("checkpoints/bangladesh_progress.json")
        self.checkpoint_file.parent.mkdir(exist_ok=True)

        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config['scraper'].get('user_agent',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        })

        # Thread safety
        self.stats_lock = threading.Lock()
        self.shutdown_requested = False

        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Base URL
        self.base_url = self.config['source']['base_url']

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _init_database(self) -> PostgreSQLAdapter:
        """Initialize PostgreSQL database connection"""
        db_config = {
            'host': self.config['database'].get('host', 'localhost'),
            'port': self.config['database'].get('port', 5433),
            'database': self.config['database'].get('database', 'indiankanoon'),
            'user': self.config['database'].get('user', 'indiankanoon_user'),
            'password': self.config['database'].get('password', 'postgres')
        }

        adapter = PostgreSQLAdapter(db_config)

        try:
            adapter.test_connection()
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

        return adapter

    def _init_drive(self):
        """Initialize Google Drive manager"""
        try:
            self.drive_manager = DriveManager(self.config)
            if self.drive_manager.authenticate():
                logger.info("Google Drive authenticated")
            else:
                logger.warning("Google Drive authentication failed")
                self.drive_manager = None
        except Exception as e:
            logger.warning(f"Google Drive initialization failed: {e}")
            self.drive_manager = None

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("\nShutdown requested. Saving checkpoint...")
        self.shutdown_requested = True
        self._save_checkpoint()

    def _save_checkpoint(self):
        """Save current progress"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(asdict(self.state), f, indent=2)
        logger.info(f"Checkpoint saved: {self.state.processed}/{self.state.total_documents}")

    def _load_checkpoint(self) -> Optional[ProgressState]:
        """Load last checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                return ProgressState(**data)
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
        return None

    def get_act_list(self) -> List[Dict]:
        """
        Get list of all acts from bdlaws chronological index

        Returns:
            List of dicts with act info (number, title, url, year)
        """
        logger.info("Fetching act list from bdlaws.minlaw.gov.bd...")
        acts = []

        try:
            # Fetch chronological index
            index_url = f"{self.base_url}/laws-of-bangladesh-chronological-index.html"
            response = self.session.get(index_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all act links - they follow pattern act-{number}.html
            for link in soup.find_all('a', href=True):
                href = link['href']
                match = re.search(r'act-(\d+)\.html', href)
                if match:
                    act_number = int(match.group(1))
                    title = link.get_text(strip=True)

                    # Extract year from title if present
                    year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', title)
                    year = int(year_match.group(1)) if year_match else None

                    # Make absolute URL
                    act_url = href if href.startswith('http') else f"{self.base_url}/{href.lstrip('/')}"

                    acts.append({
                        'act_number': act_number,
                        'title': title,
                        'url': act_url,
                        'year': year
                    })

            # Remove duplicates by act_number
            seen = set()
            unique_acts = []
            for act in acts:
                if act['act_number'] not in seen:
                    seen.add(act['act_number'])
                    unique_acts.append(act)

            # Sort by act number
            unique_acts.sort(key=lambda x: x['act_number'])

            logger.info(f"Found {len(unique_acts)} unique acts")
            return unique_acts

        except Exception as e:
            logger.error(f"Failed to get act list: {e}")
            return []

    def scrape_act(self, act_info: Dict) -> Optional[Dict]:
        """
        Scrape a single act page and download PDF if available

        Args:
            act_info: Dict with act_number, title, url, year

        Returns:
            Dict with scraped data or None on failure
        """
        delay = self.config['scraper']['delay_between_requests']
        time.sleep(delay)

        try:
            # Fetch act page
            response = self.session.get(act_info['url'], timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content
            content_div = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
            content = content_div.get_text('\n', strip=True) if content_div else ''

            # Determine document type from title
            title_lower = act_info['title'].lower()
            if 'ordinance' in title_lower:
                doc_type = 'ORN'
            elif 'order' in title_lower:
                doc_type = 'ORD'
            elif 'rule' in title_lower:
                doc_type = 'RUL'
            elif 'code' in title_lower or 'act' in title_lower:
                doc_type = 'ACT'
            elif 'constitution' in title_lower:
                doc_type = 'CON'
            else:
                doc_type = 'ACT'

            # Look for PDF download link
            pdf_url = None
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf') or 'download' in href.lower():
                    pdf_url = href if href.startswith('http') else f"{self.base_url}/{href.lstrip('/')}"
                    break

            # Also check for print version (can be converted to PDF)
            print_url = f"{self.base_url}/act-print-{act_info['act_number']}.html"

            return {
                'act_number': act_info['act_number'],
                'title': act_info['title'],
                'url': act_info['url'],
                'year': act_info['year'] or 2024,
                'doc_type': doc_type,
                'content': content[:50000],  # Limit content size
                'pdf_url': pdf_url,
                'print_url': print_url,
                'doc_number': str(act_info['act_number'])
            }

        except Exception as e:
            logger.error(f"Failed to scrape act {act_info['act_number']}: {e}")
            return None

    def download_or_generate_pdf(self, act_data: Dict, doc_id: int) -> Optional[str]:
        """
        Download PDF or generate from print view

        Args:
            act_data: Scraped act data
            doc_id: Database document ID

        Returns:
            Path to PDF file or None
        """
        try:
            # Generate filename
            year = act_data.get('year', 2024)
            doc_type = act_data.get('doc_type', 'ACT')
            doc_number = act_data.get('doc_number', '0')
            safe_title = re.sub(r'[^\w\s-]', '', act_data.get('title', 'Unknown')[:40])
            safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
            filename = f"BD_{year}_{doc_type}_{doc_number}_{safe_title}.pdf"

            # Create year directory
            year_dir = self.pdf_dir / str(year)
            year_dir.mkdir(exist_ok=True)
            pdf_path = year_dir / filename

            # Try to download PDF if URL exists
            if act_data.get('pdf_url'):
                try:
                    response = self.session.get(act_data['pdf_url'], timeout=60)
                    if response.status_code == 200 and response.content.startswith(b'%PDF'):
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"Downloaded PDF: {filename}")
                        return str(pdf_path)
                except Exception as e:
                    logger.warning(f"PDF download failed: {e}")

            # Try print view
            try:
                response = self.session.get(act_data['print_url'], timeout=30)
                if response.status_code == 200:
                    # Save as HTML for now (can be converted to PDF later)
                    html_path = year_dir / filename.replace('.pdf', '.html')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info(f"Saved HTML: {html_path.name}")

                    # Try to convert to PDF using weasyprint if available
                    try:
                        from weasyprint import HTML
                        HTML(string=response.text, base_url=self.base_url).write_pdf(pdf_path)
                        logger.info(f"Generated PDF: {filename}")
                        return str(pdf_path)
                    except ImportError:
                        logger.debug("weasyprint not available, keeping HTML")
                        return str(html_path)

            except Exception as e:
                logger.warning(f"Print view failed: {e}")

            return None

        except Exception as e:
            logger.error(f"Failed to download/generate PDF: {e}")
            return None

    def process_act(self, act_info: Dict) -> bool:
        """
        Process a single act: scrape, save to DB, download PDF

        Args:
            act_info: Dict with act info

        Returns:
            True if successful
        """
        try:
            # Scrape act
            act_data = self.scrape_act(act_info)
            if not act_data:
                return False

            # Insert to PostgreSQL
            doc_id = self.db.insert_bangladesh_document(act_data)
            logger.info(f"Inserted act {act_info['act_number']} as doc_id={doc_id}")

            # Download/generate PDF
            pdf_path = self.download_or_generate_pdf(act_data, doc_id)

            if pdf_path:
                # Get file size
                pdf_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0

                # Insert file storage record
                self.db.insert_file_storage_bangladesh(doc_id, pdf_path, pdf_size)
                logger.info(f"Stored file record for act {act_info['act_number']}")

            return True

        except Exception as e:
            logger.error(f"Failed to process act {act_info['act_number']}: {e}")
            return False

    def upload_pending_to_drive(self):
        """Upload all pending files to Google Drive"""
        if not self.drive_manager:
            logger.warning("Google Drive not available, skipping upload")
            return

        logger.info("Uploading pending files to Google Drive...")

        # Get pending uploads
        pending = self.db.get_pending_uploads(limit=100)

        if not pending:
            logger.info("No pending uploads")
            return

        logger.info(f"Found {len(pending)} files to upload")

        # Group by year for folder organization
        by_year = {}
        for doc_id, pdf_path in pending:
            if pdf_path and os.path.exists(pdf_path):
                # Extract year from path
                match = re.search(r'/(\d{4})/', pdf_path)
                year = int(match.group(1)) if match else 2024
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append((doc_id, pdf_path))

        # Upload by year
        for year, files in by_year.items():
            logger.info(f"Uploading {len(files)} files for year {year}")

            # Get or create year folder
            folder_id = self.drive_manager.get_or_create_upload_folder(year=year)
            if not folder_id:
                logger.error(f"Failed to create folder for year {year}")
                continue

            for doc_id, pdf_path in files:
                try:
                    file_id = self.drive_manager.upload_file(pdf_path, folder_id)
                    if file_id:
                        # Update database with Drive info
                        self.db.update_drive_info(doc_id, file_id, f"BD/{year}/")
                        logger.info(f"Uploaded doc {doc_id} to Drive")
                except Exception as e:
                    logger.error(f"Failed to upload doc {doc_id}: {e}")

    def print_stats(self):
        """Print current statistics"""
        with self.stats_lock:
            elapsed = time.time() - self.state.start_time
            if elapsed == 0:
                return

            docs_per_hour = (self.state.processed / elapsed) * 3600

            # Get database stats
            try:
                db_stats = self.db.get_bangladesh_stats()
            except:
                db_stats = {}

            logger.info("=" * 70)
            logger.info(f"Progress: {self.state.processed}/{self.state.total_documents}")
            logger.info(f"Successful: {self.state.successful} | Failed: {self.state.failed}")
            logger.info(f"Rate: {docs_per_hour:.0f} docs/hour")
            if db_stats:
                logger.info(f"In DB: {db_stats.get('total_documents', 0)} docs, "
                           f"{db_stats.get('with_pdf', 0)} with PDFs, "
                           f"{db_stats.get('on_drive', 0)} on Drive")
            logger.info("=" * 70)

    def run(self, limit: Optional[int] = None, skip_existing: bool = True):
        """
        Main scraping loop

        Args:
            limit: Optional limit on number of acts to process
            skip_existing: Skip acts already in database
        """
        logger.info("=" * 70)
        logger.info("BANGLADESH LAWS PRODUCTION SCRAPER")
        logger.info("=" * 70)

        # Get act list
        acts = self.get_act_list()
        if not acts:
            logger.error("No acts found!")
            return

        if limit:
            acts = acts[:limit]

        # Initialize state
        self.state.total_documents = len(acts)
        self.state.start_time = time.time()

        logger.info(f"Processing {len(acts)} acts")
        logger.info(f"PDF directory: {self.pdf_dir}")
        logger.info(f"Google Drive: {'Enabled' if self.drive_manager else 'Disabled'}")

        # Process acts
        checkpoint_interval = self.config['checkpointing'].get('checkpoint_interval', 25)

        for i, act_info in enumerate(acts, 1):
            if self.shutdown_requested:
                logger.info("Shutting down...")
                break

            logger.info(f"\n[{i}/{len(acts)}] Processing: {act_info['title'][:60]}...")

            success = self.process_act(act_info)

            with self.stats_lock:
                self.state.processed += 1
                if success:
                    self.state.successful += 1
                else:
                    self.state.failed += 1

            # Progress report
            if i % 10 == 0:
                self.print_stats()

            # Checkpoint
            if i % checkpoint_interval == 0:
                self._save_checkpoint()

        # Final statistics
        self.print_stats()

        # Upload to Drive
        if self.drive_manager:
            self.upload_pending_to_drive()

        logger.info("\n" + "=" * 70)
        logger.info("SCRAPING COMPLETE")
        logger.info("=" * 70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Bangladesh Laws Production Scraper")
    parser.add_argument('--config', default='config/config_bangladesh.yaml', help='Config file')
    parser.add_argument('--limit', type=int, help='Limit number of acts to process')
    parser.add_argument('--upload-only', action='store_true', help='Only upload pending files to Drive')

    args = parser.parse_args()

    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)

    try:
        scraper = BangladeshProductionScraper(config_path=args.config)

        if args.upload_only:
            scraper.upload_pending_to_drive()
        else:
            scraper.run(limit=args.limit)

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
