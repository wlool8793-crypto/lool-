#!/usr/bin/env python3
"""
Single-IP Production Scraper for IndianKanoon
Optimized for operation without proxy rotation
Conservative rate limiting to avoid blocks

Features:
- 2 workers max (safe for single IP)
- Automatic checkpointing every 100 documents
- Resume from last checkpoint
- Progress tracking and ETA
- Graceful error handling
"""

import os
import sys
import time
import json
import yaml
import signal
import sqlite3
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/single_ip_scraper.log'),
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
    skipped: int = 0
    start_time: float = 0.0
    last_checkpoint: int = 0
    current_batch: int = 0

@dataclass
class DownloadStats:
    """Statistics for a single download"""
    doc_id: int
    success: bool
    download_time_ms: int
    size_bytes: int = 0
    error: Optional[str] = None

class CheckpointManager:
    """Manages checkpointing and resume functionality"""

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / "single_ip_progress.json"

    def save_checkpoint(self, state: ProgressState):
        """Save current progress"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(asdict(state), f, indent=2)
        logger.info(f"💾 Checkpoint saved: {state.processed}/{state.total_documents} documents")

    def load_checkpoint(self) -> Optional[ProgressState]:
        """Load last checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                state = ProgressState(**data)
                logger.info(f"📂 Resuming from checkpoint: {state.processed}/{state.total_documents} documents")
                return state
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
        return None

    def clear_checkpoint(self):
        """Clear checkpoint file"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

class SingleIPScraper:
    """Production scraper optimized for single-IP operation"""

    def __init__(self, config_path: str = "config/config_single_ip.yaml"):
        """Initialize scraper with configuration"""
        self.config = self._load_config(config_path)
        self.db_path = self._get_db_path()
        self.checkpoint_manager = CheckpointManager()
        self.state = ProgressState()
        self.stats_lock = threading.Lock()
        self.shutdown_requested = False

        # OPTIMIZATION: Batch database writes
        self.db_batch = []
        self.db_batch_lock = threading.Lock()
        self.batch_size = 100  # Flush after 100 documents

        # OPTIMIZATION: Connection pooling (thread-local sessions)
        self.thread_local = threading.local()

        # Create output directories
        Path(self.config['output']['pdf_directory']).mkdir(parents=True, exist_ok=True)
        Path(self.config['output']['temp_directory']).mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(exist_ok=True)

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _get_db_path(self) -> str:
        """Extract database path from config"""
        db_url = self.config['database']['url']
        if 'sqlite:///' in db_url:
            return db_url.split('sqlite:///')[-1]
        raise ValueError("Only SQLite databases supported for single-IP operation")

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("\n⚠️  Shutdown requested. Saving checkpoint...")
        self.shutdown_requested = True
        if self.config['checkpointing']['save_on_interrupt']:
            self.checkpoint_manager.save_checkpoint(self.state)

    def _get_session(self) -> requests.Session:
        """
        OPTIMIZATION: Get or create thread-local HTTP session for connection reuse
        """
        if not hasattr(self.thread_local, 'session'):
            self.thread_local.session = requests.Session()
            self.thread_local.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
        return self.thread_local.session

    def get_documents_to_process(self, limit: Optional[int] = None) -> List[Tuple[int, str]]:
        """
        Get documents that need to be downloaded
        Returns: List of (doc_id, source_url) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get documents without PDFs
        query = """
            SELECT id, source_url
            FROM universal_legal_documents
            WHERE (pdf_downloaded = 0 OR pdf_downloaded IS NULL)
            AND source_url IS NOT NULL
            AND source_url LIKE '%indiankanoon.org%'
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        logger.info(f"Found {len(results)} documents to process")
        return results

    def download_document(self, doc_id: int, url: str) -> DownloadStats:
        """
        Download a single document
        OPTIMIZED: Direct PDF download, connection reuse, batch database writes
        """
        start_time = time.time()
        delay = self.config['scraper']['delay_between_requests']

        # Rate limiting delay
        time.sleep(delay)

        # OPTIMIZATION: Reuse session for connection pooling
        session = self._get_session()

        try:
            # OPTIMIZATION: Direct PDF download if URL ends in .pdf
            if url.lower().endswith('.pdf'):
                # Direct download, skip HTML parsing
                logger.debug(f"[{doc_id}] Direct PDF download from URL")
                pdf_response = session.get(url, timeout=60)
                pdf_response.raise_for_status()
                content = pdf_response.content
                pdf_link = url
            else:
                # Get the page and parse for PDF link
                response = session.get(url, timeout=self.config['scraper']['timeout_seconds'])
                response.raise_for_status()

                # Parse to find PDF link
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find download link
                pdf_link = None
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    text = link.get_text().lower()
                    if 'pdf' in text or '.pdf' in href or ('/doc/' in href and href != url):
                        pdf_link = href
                        break

                if pdf_link:
                    # Make absolute URL
                    if not pdf_link.startswith('http'):
                        from urllib.parse import urljoin
                        pdf_link = urljoin('https://indiankanoon.org', pdf_link)

                    # Download content
                    pdf_response = session.get(pdf_link, timeout=60)
                    pdf_response.raise_for_status()
                    content = pdf_response.content
                else:
                    raise Exception("No download link found")

            # Save PDF
            pdf_path = Path(self.config['output']['pdf_directory']) / f"doc_{doc_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(content)

            # OPTIMIZATION: Batch database writes (queue instead of immediate commit)
            self._mark_downloaded(doc_id, str(pdf_path), len(content))

            download_time_ms = int((time.time() - start_time) * 1000)

            logger.debug(f"✓ [{doc_id}] Downloaded {len(content)} bytes in {download_time_ms}ms")

            return DownloadStats(
                doc_id=doc_id,
                success=True,
                download_time_ms=download_time_ms,
                size_bytes=len(content)
            )

        except Exception as e:
            download_time_ms = int((time.time() - start_time) * 1000)
            logger.debug(f"✗ [{doc_id}] Failed: {str(e)[:100]}")

            return DownloadStats(
                doc_id=doc_id,
                success=False,
                download_time_ms=download_time_ms,
                error=str(e)
            )

    def _mark_downloaded(self, doc_id: int, pdf_path: str, size_bytes: int):
        """
        Mark document as downloaded in database
        Using immediate commit for SQLite thread safety
        """
        try:
            # Use a lock to ensure thread-safe database access
            with self.db_batch_lock:
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE universal_legal_documents
                    SET pdf_downloaded = 1,
                        pdf_path = ?,
                        pdf_size_bytes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (pdf_path, size_bytes, doc_id))

                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Failed to mark document {doc_id} as downloaded: {e}")

    def _flush_batch(self):
        """
        OPTIMIZATION: Flush batched database writes
        Commits all pending updates in a single transaction
        """
        with self.db_batch_lock:
            if not self.db_batch:
                return  # Nothing to flush

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Batch update all documents in single transaction
                cursor.executemany("""
                    UPDATE universal_legal_documents
                    SET pdf_downloaded = 1,
                        pdf_path = ?,
                        pdf_size_bytes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, self.db_batch)

                conn.commit()
                conn.close()

                logger.debug(f"✓ Flushed {len(self.db_batch)} database updates")
                self.db_batch = []  # Clear batch

            except Exception as e:
                logger.error(f"Failed to flush database batch: {e}")
                # Don't clear batch on error - will retry later
                raise

    def print_progress(self):
        """Print progress statistics"""
        with self.stats_lock:
            elapsed = time.time() - self.state.start_time
            if elapsed < 1:
                return

            docs_per_sec = self.state.processed / elapsed
            docs_per_hour = docs_per_sec * 3600

            remaining = self.state.total_documents - self.state.processed
            eta_seconds = remaining / docs_per_sec if docs_per_sec > 0 else 0
            eta = datetime.now() + timedelta(seconds=eta_seconds)

            success_rate = (self.state.successful / self.state.processed * 100) if self.state.processed > 0 else 0

            print(f"\n{'='*80}")
            print(f"Progress: {self.state.processed}/{self.state.total_documents} "
                  f"({self.state.processed/self.state.total_documents*100:.1f}%)")
            print(f"Successful: {self.state.successful} | Failed: {self.state.failed} | "
                  f"Success Rate: {success_rate:.1f}%")
            print(f"Throughput: {docs_per_hour:.1f} docs/hour ({docs_per_sec:.2f} docs/sec)")
            print(f"Elapsed: {timedelta(seconds=int(elapsed))} | ETA: {eta.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")

    def run(self, resume: bool = True, limit: Optional[int] = None):
        """
        Main scraping loop

        Args:
            resume: Resume from last checkpoint
            limit: Maximum documents to process (None = all)
        """
        logger.info("="*80)
        logger.info("SINGLE-IP PRODUCTION SCRAPER STARTING")
        logger.info("="*80)

        # Resume from checkpoint if enabled
        if resume and self.config['checkpointing']['auto_resume']:
            saved_state = self.checkpoint_manager.load_checkpoint()
            if saved_state:
                # Don't resume state in single-IP mode, just log it
                logger.info(f"Previous session: {saved_state.processed} documents processed")
                logger.info("Starting fresh collection (will skip already downloaded docs)")

        # Get documents to process
        documents = self.get_documents_to_process(limit)

        if not documents:
            logger.info("No documents to process!")
            return

        self.state.total_documents = len(documents)
        self.state.start_time = time.time()

        logger.info(f"Starting to process {len(documents)} documents")
        logger.info(f"Workers: {self.config['performance']['max_workers']}")
        logger.info(f"Rate limit: {self.config['safety']['max_requests_per_minute']} req/min")
        logger.info(f"Delay per request: {self.config['scraper']['delay_between_requests']}s")

        # Process in batches with ThreadPoolExecutor
        max_workers = self.config['performance']['max_workers']
        checkpoint_interval = self.config['checkpointing']['checkpoint_interval']
        report_interval = self.config['progress']['report_interval']

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for doc_id, url in documents:
                if self.shutdown_requested:
                    break

                future = executor.submit(self.download_document, doc_id, url)
                futures[future] = (doc_id, url)

            for future in as_completed(futures):
                if self.shutdown_requested:
                    logger.info("Shutdown requested, stopping...")
                    break

                result = future.result()

                with self.stats_lock:
                    self.state.processed += 1

                    if result.success:
                        self.state.successful += 1
                    else:
                        self.state.failed += 1

                    # Progress reporting
                    if self.state.processed % report_interval == 0:
                        self.print_progress()

                    # Checkpointing
                    if self.state.processed % checkpoint_interval == 0:
                        self.checkpoint_manager.save_checkpoint(self.state)

        # Final statistics
        self.print_final_stats()

        # Clear checkpoint if completed successfully
        if not self.shutdown_requested and self.state.processed >= self.state.total_documents:
            logger.info("✅ Collection complete! Clearing checkpoint.")
            self.checkpoint_manager.clear_checkpoint()

    def print_final_stats(self):
        """Print final statistics"""
        elapsed = time.time() - self.state.start_time

        print("\n" + "="*80)
        print("SCRAPING SESSION COMPLETE")
        print("="*80)

        print(f"\nDocuments:")
        print(f"  Total: {self.state.total_documents}")
        print(f"  Processed: {self.state.processed}")
        print(f"  Successful: {self.state.successful}")
        print(f"  Failed: {self.state.failed}")
        print(f"  Success Rate: {self.state.successful/self.state.processed*100:.1f}%")

        print(f"\nPerformance:")
        print(f"  Total Time: {timedelta(seconds=int(elapsed))}")
        print(f"  Throughput: {self.state.successful/elapsed*3600:.1f} docs/hour")
        print(f"  Avg Time per Doc: {elapsed/self.state.processed:.2f}s")

        # Extrapolation
        if self.state.successful > 0:
            total_docs = 1_400_000
            docs_per_hour = self.state.successful / elapsed * 3600
            hours_needed = total_docs / docs_per_hour
            days_needed = hours_needed / 24

            print(f"\nExtrapolation to 1.4M documents:")
            print(f"  Time needed: {hours_needed:.0f} hours ({days_needed:.1f} days)")
            print(f"  At current rate: {docs_per_hour:.0f} docs/hour")

        print("="*80)

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Single-IP Production Scraper for IndianKanoon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with auto-resume (default)
  python single_ip_production_scraper.py

  # Test with 100 documents
  python single_ip_production_scraper.py --limit 100

  # Start fresh (ignore checkpoint)
  python single_ip_production_scraper.py --no-resume

  # Custom config
  python single_ip_production_scraper.py --config config/my_config.yaml
        """
    )

    parser.add_argument('--config', type=str, default='config/config_single_ip.yaml',
                       help='Configuration file path')
    parser.add_argument('--limit', type=int, default=None,
                       help='Maximum documents to process (for testing)')
    parser.add_argument('--no-resume', action='store_true',
                       help='Start fresh, ignore checkpoint')

    args = parser.parse_args()

    try:
        scraper = SingleIPScraper(config_path=args.config)
        scraper.run(resume=not args.no_resume, limit=args.limit)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
