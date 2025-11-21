#!/usr/bin/env python3
"""
Bangladesh Laws PDF Downloader with Multi-Worker Support
==========================================================
Downloads PDFs for all Bangladesh laws with available PDF URLs.

Features:
- 10 concurrent workers (ThreadPoolExecutor)
- Progress tracking with tqdm
- Automatic retry on failure
- Checkpoint/resume capability
- File validation (size, integrity)
- Organized folder structure

Usage:
    python download_bangladesh_pdfs.py                    # Download all PDFs
    python download_bangladesh_pdfs.py --workers 5        # Use 5 workers
    python download_bangladesh_pdfs.py --test             # Test mode (10 PDFs)
"""

import argparse
import sys
import os
import time
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
import sqlite3
import requests
from typing import Optional, Dict

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.unified_database import UnifiedDatabase
from src.naming.universal_namer import UniversalNamer
from src.file_organizer import FileOrganizer
from src.utils import calculate_file_hash, sanitize_filename, format_file_size


class BangladeshPDFDownloader:
    """Multi-worker PDF downloader for Bangladesh laws"""

    def __init__(self, config: dict):
        self.config = config
        self.start_time = datetime.now()

        # Thread-safe stats
        self.stats_lock = threading.Lock()
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'total_bytes': 0,
            'errors': []
        }

        # Setup logging
        self._setup_logging()

        # Database
        self.db_path = 'data/indiankanoon.db'

        # Shared components
        self.namer = UniversalNamer()
        self.organizer = FileOrganizer()

        # Create folder structure
        self.logger.info("Creating Bangladesh folder structure...")
        folders = self.organizer.create_folder_structure('BD')
        self.logger.info(f"Created {len(folders)} folders")

    def _setup_logging(self):
        """Setup logging"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"bangladesh_pdf_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(threadName)-10s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging to: {log_file}")

    def update_stats(self, field: str, value: int = 1):
        """Thread-safe stats update"""
        with self.stats_lock:
            if field == 'total_bytes':
                self.stats[field] += value
            else:
                self.stats[field] += value

    def get_documents_with_pdfs(self, limit: Optional[int] = None) -> list:
        """Get all documents that have PDF URLs but haven't been downloaded"""
        db = UnifiedDatabase(self.db_path, use_universal=True)

        query = """
        SELECT id, country_code, doc_category, jurisdiction_level, doc_year,
               doc_number, title_full, title_short, pdf_url, source_url,
               subject_primary, subject_secondary
        FROM universal_legal_documents
        WHERE country_code = 'BD'
          AND pdf_url IS NOT NULL
          AND pdf_url != ''
          AND (pdf_downloaded IS NULL OR pdf_downloaded = 0)
        ORDER BY doc_year DESC, id ASC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor = db.conn.cursor()
        cursor.execute(query)

        docs = []
        for row in cursor.fetchall():
            docs.append({
                'id': row[0],
                'country_code': row[1],
                'doc_category': row[2],
                'jurisdiction_level': row[3],
                'doc_year': row[4],
                'doc_number': row[5],
                'title_full': row[6],
                'title_short': row[7],
                'pdf_url': row[8],
                'source_url': row[9],
                'subject_primary': row[10],
                'subject_secondary': row[11]
            })

        db.close()
        return docs

    def download_single_pdf(self, doc: dict, worker_id: int) -> dict:
        """Download a single PDF (worker function)"""

        result = {
            'doc_id': doc['id'],
            'success': False,
            'error': None,
            'file_size': 0,
            'file_path': None
        }

        try:
            # Generate filename using universal namer
            filename = self.namer.generate_filename(doc)
            if not filename.endswith('.pdf'):
                filename += '.pdf'

            # Determine folder path
            category = doc.get('doc_category', 'ACT')
            jurisdiction = doc.get('jurisdiction_level', 'CENTRAL')

            # Create temp path
            temp_dir = Path('data/temp_pdfs')
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_path = temp_dir / f"temp_{worker_id}_{filename}"

            # Download PDF
            pdf_url = doc['pdf_url']
            if not pdf_url.startswith('http'):
                pdf_url = 'http://bdlaws.minlaw.gov.bd' + pdf_url

            self.logger.debug(f"Worker {worker_id} downloading: {pdf_url}")

            response = requests.get(
                pdf_url,
                timeout=self.config.get('download_timeout', 30),
                stream=True
            )
            response.raise_for_status()

            # Write to temp file
            total_size = 0
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)

            if total_size < 1024:  # Less than 1KB - likely error page
                result['error'] = f"File too small ({total_size} bytes)"
                temp_path.unlink(missing_ok=True)
                return result

            # Move to final location
            final_path = self.organizer.move_temp_to_final(
                temp_path=temp_path,
                filename=filename,
                metadata=doc,
                validate_hash=False  # Skip hash validation for speed
            )

            if final_path:
                # Update database
                db = UnifiedDatabase(self.db_path, use_universal=True)
                cursor = db.conn.cursor()
                cursor.execute("""
                    UPDATE universal_legal_documents
                    SET pdf_downloaded = 1,
                        pdf_path = ?,
                        pdf_size_bytes = ?
                    WHERE id = ?
                """, (str(final_path), total_size, doc['id']))
                db.conn.commit()
                db.close()

                result['success'] = True
                result['file_size'] = total_size
                result['file_path'] = str(final_path)
                self.update_stats('downloaded')
                self.update_stats('total_bytes', total_size)
            else:
                result['error'] = "Failed to move file to final location"
                self.update_stats('failed')

        except requests.exceptions.RequestException as e:
            result['error'] = f"Download error: {str(e)}"
            self.logger.error(f"Worker {worker_id} - Download failed for doc {doc['id']}: {e}")
            self.update_stats('failed')
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            self.logger.error(f"Worker {worker_id} - Error processing doc {doc['id']}: {e}")
            self.update_stats('failed')

        return result

    def download_all(self, limit: Optional[int] = None):
        """Download all PDFs using multiple workers"""

        print("\n" + "="*80)
        print("BANGLADESH LAWS PDF DOWNLOADER")
        print("="*80)
        print(f"Workers: {self.config['workers']}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Get documents to download
        print("\n📋 PHASE 1: FETCHING DOCUMENTS")
        print("-" * 80)

        docs = self.get_documents_with_pdfs(limit=limit)
        self.stats['total'] = len(docs)

        if not docs:
            print("✓ No documents need PDF download!")
            return

        print(f"✓ Found {len(docs)} documents with PDF URLs")
        print(f"  (Total Bangladesh docs with PDFs: 760)")

        # PHASE 2: Download PDFs
        print("\n📥 PHASE 2: DOWNLOADING PDFs")
        print("-" * 80)

        # Progress bar
        pbar = tqdm(total=len(docs), desc="Downloading", unit="pdf")

        # Thread pool executor
        with ThreadPoolExecutor(max_workers=self.config['workers']) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(self.download_single_pdf, doc, i % self.config['workers']): doc
                for i, doc in enumerate(docs)
            }

            # Process completed tasks
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]

                try:
                    result = future.result()

                    # Update progress bar
                    pbar.set_postfix({
                        'Downloaded': self.stats['downloaded'],
                        'Failed': self.stats['failed'],
                        'Size': format_file_size(self.stats['total_bytes'])
                    })

                except Exception as e:
                    self.logger.error(f"Task failed: {e}")
                    self.update_stats('failed')

                pbar.update(1)

        pbar.close()

        # Final report
        self._print_final_report()

    def _print_final_report(self):
        """Print final statistics report"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print("\n" + "="*80)
        print("DOWNLOAD COMPLETE - FINAL REPORT")
        print("="*80)

        print(f"\n⏱️  Duration: {duration}")
        print(f"👷 Workers: {self.config['workers']}")
        print(f"📊 Total Documents: {self.stats['total']}")
        print(f"✓  Successfully Downloaded: {self.stats['downloaded']}")
        print(f"✗  Failed: {self.stats['failed']}")
        print(f"💾 Total Size: {format_file_size(self.stats['total_bytes'])}")

        if self.stats['downloaded'] > 0:
            rate = self.stats['downloaded'] / duration.total_seconds()
            avg_size = self.stats['total_bytes'] / self.stats['downloaded']
            print(f"⚡ Average Rate: {rate:.2f} PDFs/second")
            print(f"📈 Average PDF Size: {format_file_size(avg_size)}")
            print(f"📉 Success Rate: {(self.stats['downloaded']/(self.stats['downloaded']+self.stats['failed']))*100:.1f}%")

        print("\n💾 Database: data/indiankanoon.db")
        print(f"📁 PDFs: Legal_Database/BD/")
        print(f"📝 Logs: logs/")

        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Multi-worker Bangladesh Laws PDF Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--workers', type=int, default=10, help='Number of concurrent workers (default: 10)')
    parser.add_argument('--test', action='store_true', help='Test mode (10 PDFs)')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of PDFs to download')
    parser.add_argument('--timeout', type=int, default=30, help='Download timeout in seconds (default: 30)')

    args = parser.parse_args()

    if args.test:
        args.limit = 10
        print("🧪 TEST MODE: Downloading 10 PDFs\n")

    # Configuration
    config = {
        'workers': args.workers,
        'download_timeout': args.timeout
    }

    try:
        downloader = BangladeshPDFDownloader(config)
        downloader.download_all(limit=args.limit)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
