#!/usr/bin/env python3
"""
PostgreSQL Production Scraper for IndianKanoon
Production-grade scraper with PostgreSQL backend for extensive metadata extraction

Features:
- PostgreSQL database for production metadata storage
- 2 workers max (safe for single IP)
- Automatic checkpointing every 100 documents
- Resume from last checkpoint
- Progress tracking and ETA
- Connection pooling optimization
- Direct PDF download optimization
- Graceful error handling
"""

import os
import sys
import time
import json
import yaml
import signal
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import PostgreSQL adapter
from src.database.postgresql_adapter import PostgreSQLAdapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/postgresql_scraper.log'),
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
        self.checkpoint_file = self.checkpoint_dir / "postgresql_progress.json"

    def save_checkpoint(self, state: ProgressState):
        """Save current progress"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(asdict(state), f, indent=2)
        logger.info(f"Checkpoint saved: {state.processed}/{state.total_documents} documents")

    def load_checkpoint(self) -> Optional[ProgressState]:
        """Load last checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                state = ProgressState(**data)
                logger.info(f"Resuming from checkpoint: {state.processed}/{state.total_documents} documents")
                return state
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
        return None

    def clear_checkpoint(self):
        """Clear checkpoint file"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

class PostgreSQLScraper:
    """Production scraper with PostgreSQL backend"""

    def __init__(self, config_path: str = "config/config_postgresql.yaml"):
        """Initialize scraper with configuration"""
        self.config = self._load_config(config_path)

        # Database adapter
        self.db = self._init_database()

        # Paths
        self.pdf_dir = Path(self.config['output']['pdf_directory'])
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        # State management
        self.state = ProgressState()
        self.checkpoint_manager = CheckpointManager(
            self.config['checkpointing']['checkpoint_dir']
        )

        # Thread safety
        self.stats_lock = threading.Lock()
        self.shutdown_requested = False

        # OPTIMIZATION: Thread-local storage for HTTP sessions
        self.thread_local = threading.local()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _init_database(self) -> PostgreSQLAdapter:
        """Initialize PostgreSQL database connection"""
        db_url = self.config['database']['url']

        # Parse PostgreSQL URL
        # Format: postgresql://user:pass@host:port/database
        import re
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)

        if not match:
            raise ValueError(f"Invalid PostgreSQL URL: {db_url}")

        user, password, host, port, database = match.groups()

        db_config = {
            'host': host,
            'port': int(port),
            'database': database,
            'user': user,
            'password': password
        }

        adapter = PostgreSQLAdapter(db_config)

        # Test connection
        try:
            adapter.test_connection()
            logger.info(f" Connected to PostgreSQL: {database}@{host}:{port}")
        except Exception as e:
            logger.error(f"L Failed to connect to PostgreSQL: {e}")
            raise

        return adapter

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("\n  Shutdown requested. Saving checkpoint...")
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

    def download_document(self, doc_id: int, url: str) -> DownloadStats:
        """
        Download a single document
        OPTIMIZED: Direct PDF download, connection reuse, PostgreSQL storage
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

                # Parse HTML to find PDF link
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for PDF link
                pdf_link_elem = soup.find('a', href=lambda x: x and x.endswith('.pdf'))

                if not pdf_link_elem:
                    raise Exception("No PDF link found on page")

                pdf_link = pdf_link_elem['href']

                # Make absolute URL if needed
                if not pdf_link.startswith('http'):
                    base_url = '/'.join(url.split('/')[:3])
                    pdf_link = base_url + pdf_link

                # Download PDF
                pdf_response = session.get(pdf_link, timeout=60)
                pdf_response.raise_for_status()
                content = pdf_response.content

            # Validate PDF
            if not content.startswith(b'%PDF'):
                raise Exception("Downloaded content is not a valid PDF")

            # Save PDF
            pdf_path = self.pdf_dir / f"doc_{doc_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(content)

            size_bytes = len(content)

            # Mark as downloaded in PostgreSQL
            self.db.mark_document_downloaded(doc_id, str(pdf_path), size_bytes)

            download_time_ms = int((time.time() - start_time) * 1000)

            logger.info(f" [{doc_id}] Downloaded ({size_bytes:,} bytes, {download_time_ms}ms)")

            return DownloadStats(
                doc_id=doc_id,
                success=True,
                download_time_ms=download_time_ms,
                size_bytes=size_bytes
            )

        except Exception as e:
            download_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"L [{doc_id}] Failed: {str(e)}")

            return DownloadStats(
                doc_id=doc_id,
                success=False,
                download_time_ms=download_time_ms,
                error=str(e)
            )

    def print_progress(self):
        """Print progress statistics"""
        with self.stats_lock:
            elapsed = time.time() - self.state.start_time
            if elapsed == 0:
                return

            # Calculate rates
            docs_per_sec = self.state.processed / elapsed
            docs_per_hour = docs_per_sec * 3600

            # Calculate ETA
            remaining = self.state.total_documents - self.state.processed
            if docs_per_sec > 0:
                eta_seconds = remaining / docs_per_sec
                eta = str(timedelta(seconds=int(eta_seconds)))
            else:
                eta = "calculating..."

            # Success rate
            if self.state.processed > 0:
                success_rate = (self.state.successful / self.state.processed) * 100
            else:
                success_rate = 0.0

            logger.info("="*80)
            logger.info(f"Progress: {self.state.processed}/{self.state.total_documents} ({self.state.processed/self.state.total_documents*100:.1f}%)")
            logger.info(f"Success: {self.state.successful} | Failed: {self.state.failed}")
            logger.info(f"Success Rate: {success_rate:.1f}%")
            logger.info(f"Throughput: {docs_per_hour:.0f} docs/hour")
            logger.info(f"ETA: {eta}")
            logger.info("="*80)

    def print_final_stats(self):
        """Print final statistics"""
        elapsed = time.time() - self.state.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        docs_per_hour = (self.state.processed / elapsed) * 3600 if elapsed > 0 else 0
        success_rate = (self.state.successful / self.state.processed * 100) if self.state.processed > 0 else 0

        # Extrapolation
        total_docs = self.config['estimations']['total_documents']
        if docs_per_hour > 0:
            hours_needed = total_docs / docs_per_hour
            days_needed = hours_needed / 24
        else:
            hours_needed = days_needed = 0

        logger.info("\n" + "="*80)
        logger.info("SCRAPING SESSION COMPLETE")
        logger.info("="*80)
        logger.info("")
        logger.info("Documents:")
        logger.info(f"  Total: {self.state.total_documents}")
        logger.info(f"  Processed: {self.state.processed}")
        logger.info(f"  Successful: {self.state.successful}")
        logger.info(f"  Failed: {self.state.failed}")
        logger.info(f"  Success Rate: {success_rate:.1f}%")
        logger.info("")
        logger.info("Performance:")
        logger.info(f"  Total Time: {elapsed_str}")
        logger.info(f"  Throughput: {docs_per_hour:.1f} docs/hour")
        logger.info(f"  Avg Time per Doc: {elapsed/self.state.processed if self.state.processed > 0 else 0:.2f}s")
        logger.info("")
        logger.info(f"Extrapolation to {total_docs:,} documents:")
        logger.info(f"  Time needed: {int(hours_needed)} hours ({days_needed:.1f} days)")
        logger.info(f"  At current rate: {int(docs_per_hour)} docs/hour")
        logger.info("="*80)

    def run(self, limit: Optional[int] = None):
        """
        Main scraping loop

        Args:
            limit: Optional limit on number of documents to process
        """
        logger.info("="*80)
        logger.info("POSTGRESQL PRODUCTION SCRAPER STARTING")
        logger.info("="*80)

        # Get documents to process
        documents = self.db.get_documents_to_process(limit=limit)

        if not documents:
            logger.info(" No documents to process!")
            return

        # Initialize state
        self.state.total_documents = len(documents)
        self.state.start_time = time.time()

        logger.info(f"Found {len(documents)} documents to process")
        logger.info(f"Starting to process {len(documents)} documents")
        logger.info(f"Workers: {self.config['performance']['max_workers']}")
        logger.info(f"Rate limit: {self.config['safety']['max_requests_per_minute']} req/min")
        logger.info(f"Delay per request: {self.config['scraper']['delay_between_requests']}s")

        # Process documents with thread pool
        max_workers = self.config['performance']['max_workers']
        report_interval = self.config['progress']['report_interval']
        checkpoint_interval = self.config['checkpointing']['checkpoint_interval']

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(self.download_document, doc_id, url): (doc_id, url)
                for doc_id, url in documents
            }

            # Process as they complete
            for future in as_completed(future_to_doc):
                if self.shutdown_requested:
                    logger.info("Shutting down...")
                    break

                doc_id, url = future_to_doc[future]

                try:
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

                except Exception as e:
                    logger.error(f"Error processing document {doc_id}: {e}")
                    with self.stats_lock:
                        self.state.processed += 1
                        self.state.failed += 1

        # Final statistics
        self.print_final_stats()

        # Clear checkpoint if completed successfully
        if not self.shutdown_requested and self.state.processed >= self.state.total_documents:
            logger.info(" Collection complete! Clearing checkpoint.")
            self.checkpoint_manager.clear_checkpoint()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL Production Scraper")
    parser.add_argument('--config', default='config/config_postgresql.yaml', help='Config file path')
    parser.add_argument('--limit', type=int, help='Limit number of documents to process')

    args = parser.parse_args()

    try:
        scraper = PostgreSQLScraper(config_path=args.config)
        scraper.run(limit=args.limit)
    except KeyboardInterrupt:
        logger.info("\n  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"L Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
