"""
Download Manager Module
Manages concurrent PDF downloads using ThreadPoolExecutor
"""

import logging
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Optional, Callable
from queue import Queue
import signal

# Import existing scraper (reuse proven PDF download logic)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scraper import IndianKanoonScraper

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manages concurrent PDF downloads with progress tracking and error handling."""

    def __init__(self, config: Dict, drive_manager=None):
        """
        Initialize Download Manager.

        Args:
            config: Configuration dictionary
            drive_manager: Optional DriveManager instance for uploads
        """
        self.config = config
        self.drive_manager = drive_manager

        # Configuration
        self.num_threads = config.get('scraper', {}).get('num_threads', 10)
        self.temp_dir = Path(config.get('storage', {}).get('temp_dir', './data/temp_pdfs'))
        self.batch_upload_size = config.get('scraper', {}).get('batch_upload_size', 50)
        self.delay = config.get('scraper', {}).get('delay_between_requests', 0.5)
        self.max_retries = config.get('scraper', {}).get('max_retries', 3)
        self.timeout = config.get('scraper', {}).get('timeout', 30)

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Thread-safe progress tracking
        self.lock = threading.Lock()
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'uploaded': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }

        # For batch uploads
        self.download_queue: Queue = Queue()

        # Graceful shutdown
        self.shutdown_event = threading.Event()
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            logger.warning("\n⚠ Shutdown signal received. Finishing current downloads...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def download_single_pdf(
        self,
        url: str,
        doc_id: str,
        metadata: Optional[Dict] = None,
        worker_id: int = 0
    ) -> Dict:
        """
        Download a single PDF using existing scraper logic.

        Args:
            url: Document URL
            doc_id: Document ID
            metadata: Optional metadata dictionary
            worker_id: Worker thread ID

        Returns:
            Dictionary with download result
        """
        result = {
            'url': url,
            'doc_id': doc_id,
            'success': False,
            'file_path': None,
            'error': None,
            'uploaded': False
        }

        try:
            # Create output path
            output_path = self.temp_dir / f"doc_{doc_id}.pdf"

            # Skip if already exists
            if output_path.exists():
                file_size = output_path.stat().st_size
                if file_size > 1024:  # > 1KB
                    with self.lock:
                        self.stats['skipped'] += 1
                    logger.info(f"[Worker-{worker_id}] ⊙ Already exists: doc_{doc_id}.pdf")
                    result['success'] = True
                    result['file_path'] = str(output_path)
                    return result

            # Create scraper instance (thread-safe)
            scraper = IndianKanoonScraper(delay=self.delay, headless=True)

            # Download PDF using proven method
            success = scraper.download_indiankanoon_pdf(
                url,
                str(output_path),
                max_retries=self.max_retries
            )

            if success and output_path.exists():
                file_size = output_path.stat().st_size
                if file_size > 1024:  # Validate minimum size
                    with self.lock:
                        self.stats['downloaded'] += 1

                    result['success'] = True
                    result['file_path'] = str(output_path)

                    logger.info(
                        f"[Worker-{worker_id}] ✓ Downloaded: doc_{doc_id}.pdf "
                        f"({file_size:,} bytes) [{self.stats['downloaded']}/{self.stats['total']}]"
                    )

                    # Add to upload queue if batch size reached
                    if self.drive_manager:
                        self.download_queue.put(str(output_path))

                        if self.download_queue.qsize() >= self.batch_upload_size:
                            self._process_upload_batch()
                else:
                    with self.lock:
                        self.stats['failed'] += 1
                    result['error'] = f"File too small: {file_size} bytes"
                    logger.warning(f"[Worker-{worker_id}] ⚠ Invalid PDF: doc_{doc_id}.pdf (too small)")
            else:
                with self.lock:
                    self.stats['failed'] += 1
                result['error'] = "Download failed"
                logger.error(f"[Worker-{worker_id}] ✗ Failed: doc_{doc_id}.pdf")

        except Exception as e:
            with self.lock:
                self.stats['failed'] += 1
            result['error'] = str(e)
            logger.error(f"[Worker-{worker_id}] ✗ Error downloading doc_{doc_id}: {e}")

        return result

    def _process_upload_batch(self):
        """Process accumulated downloads and upload to Drive."""
        if not self.drive_manager:
            return

        with self.lock:
            # Get files from queue
            files_to_upload = []
            while not self.download_queue.empty() and len(files_to_upload) < self.batch_upload_size:
                files_to_upload.append(self.download_queue.get())

            if not files_to_upload:
                return

            logger.info(f"\n{'─' * 70}")
            logger.info(f"📤 Uploading batch of {len(files_to_upload)} files to Google Drive")
            logger.info(f"{'─' * 70}")

        try:
            # Upload batch
            upload_result = self.drive_manager.upload_batch(files_to_upload)

            if upload_result.get('success'):
                # Delete local files after successful upload
                uploaded_files = upload_result.get('uploaded_files', [])
                self.drive_manager.delete_local_files(uploaded_files)

                with self.lock:
                    self.stats['uploaded'] += upload_result.get('uploaded', 0)

                logger.info(f"✓ Batch upload complete: {len(uploaded_files)} files")
            else:
                logger.error("✗ Batch upload failed")

        except Exception as e:
            logger.error(f"Error during batch upload: {e}")
            # Re-queue failed files
            for file_path in files_to_upload:
                self.download_queue.put(file_path)

    def download_pdfs(
        self,
        urls: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Download PDFs concurrently using ThreadPoolExecutor.

        Args:
            urls: List of dictionaries with 'url', 'doc_id', and optional metadata
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary with download statistics
        """
        self.stats['total'] = len(urls)
        self.stats['start_time'] = time.time()

        logger.info("\n" + "=" * 70)
        logger.info("Starting Concurrent PDF Downloads")
        logger.info("=" * 70)
        logger.info(f"Total documents: {len(urls)}")
        logger.info(f"Worker threads: {self.num_threads}")
        logger.info(f"Batch upload size: {self.batch_upload_size}")
        logger.info(f"Max retries: {self.max_retries}")
        logger.info(f"Temp directory: {self.temp_dir}")
        logger.info("=" * 70)

        results = []

        try:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                # Submit all tasks
                future_to_url = {}
                for i, url_data in enumerate(urls):
                    if self.shutdown_event.is_set():
                        logger.warning("Shutdown requested, stopping submission of new tasks")
                        break

                    future = executor.submit(
                        self.download_single_pdf,
                        url_data['url'],
                        url_data['doc_id'],
                        url_data.get('metadata'),
                        i % self.num_threads
                    )
                    future_to_url[future] = url_data

                # Process completed futures
                for future in as_completed(future_to_url):
                    if self.shutdown_event.is_set():
                        logger.warning("Shutdown requested, waiting for running tasks to complete")
                        break

                    url_data = future_to_url[future]
                    try:
                        result = future.result()
                        results.append(result)

                        # Progress callback
                        if progress_callback:
                            progress_callback(self.stats)

                        # Print progress every 100 downloads
                        if self.stats['downloaded'] % 100 == 0 and self.stats['downloaded'] > 0:
                            self._print_progress()

                    except Exception as e:
                        logger.error(f"Task failed for {url_data.get('doc_id')}: {e}")
                        with self.lock:
                            self.stats['failed'] += 1

            # Process any remaining files in queue
            if self.drive_manager and not self.download_queue.empty():
                logger.info("\n📤 Uploading remaining files...")
                while not self.download_queue.empty():
                    self._process_upload_batch()

        except Exception as e:
            logger.error(f"Error during concurrent downloads: {e}")

        finally:
            self.stats['end_time'] = time.time()
            self._print_final_summary()

        return {
            'results': results,
            'stats': self.stats.copy()
        }

    def _print_progress(self):
        """Print current progress."""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['downloaded'] / elapsed if elapsed > 0 else 0
        remaining = (self.stats['total'] - self.stats['downloaded']) / rate if rate > 0 else 0

        logger.info(
            f"\n{'─' * 70}\n"
            f"📊 Progress: {self.stats['downloaded']}/{self.stats['total']} "
            f"({self.stats['downloaded']/self.stats['total']*100:.1f}%)\n"
            f"   Downloaded: {self.stats['downloaded']} | Failed: {self.stats['failed']} | "
            f"Skipped: {self.stats['skipped']} | Uploaded: {self.stats['uploaded']}\n"
            f"   Rate: {rate:.2f} docs/sec | Elapsed: {elapsed/60:.1f}min | "
            f"ETA: {remaining/60:.1f}min\n"
            f"{'─' * 70}"
        )

    def _print_final_summary(self):
        """Print final summary statistics."""
        elapsed = self.stats['end_time'] - self.stats['start_time']
        rate = self.stats['downloaded'] / elapsed if elapsed > 0 else 0

        logger.info("\n" + "=" * 70)
        logger.info("Download Complete - Final Summary")
        logger.info("=" * 70)
        logger.info(f"Total documents: {self.stats['total']}")
        logger.info(f"Downloaded: {self.stats['downloaded']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Uploaded to Drive: {self.stats['uploaded']}")
        logger.info(f"Success rate: {self.stats['downloaded']/self.stats['total']*100:.2f}%")
        logger.info(f"Total time: {elapsed/3600:.2f} hours")
        logger.info(f"Average rate: {rate:.2f} docs/sec ({rate*3600:.0f} docs/hour)")
        logger.info("=" * 70)

    def get_stats(self) -> Dict:
        """
        Get current statistics.

        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return self.stats.copy()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Upload any remaining files
        if self.drive_manager and not self.download_queue.empty():
            logger.info("Uploading remaining files before exit...")
            while not self.download_queue.empty():
                self._process_upload_batch()
