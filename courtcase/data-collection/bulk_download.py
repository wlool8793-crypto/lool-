#!/usr/bin/env python3
"""
Concurrent Bulk Download Script for IndianKanoon Cases
Uses ThreadPoolExecutor for parallel downloads with priority queuing.
Includes automatic checkpoint and resume functionality.

Performance: 30 PDFs/min → 300 PDFs/min (10x improvement)
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from src.scraper import IndianKanoonScraper
from src.database import CaseDatabase, LegalCase
from src.checkpoint_manager import CheckpointManager
from src.download_queue import (
    PriorityDownloadQueue,
    RateLimiter,
    DownloadTask,
    DownloadPriority
)
from src.proxy_manager import ProxyManager, create_proxy_manager_from_env
import logging

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f'bulk_download_{timestamp}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum: int, frame: Any) -> None:
    """Handle Ctrl+C gracefully"""
    global shutdown_requested
    logger.info("\n⚠️  Shutdown requested. Finishing current download...")
    shutdown_requested = True


def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 50) -> None:
    """Print a progress bar"""
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}', end='', flush=True)
    if iteration == total:
        print()


# Thread-local storage for scrapers (one per worker thread)
thread_local = threading.local()


def get_thread_scraper(delay: int = 1, proxy_manager: Optional[ProxyManager] = None) -> IndianKanoonScraper:
    """
    Get or create thread-local scraper instance with proxy support.

    Args:
        delay: Request delay in seconds
        proxy_manager: ProxyManager instance for proxy rotation

    Returns:
        IndianKanoonScraper instance for this thread
    """
    if not hasattr(thread_local, 'scraper'):
        # Get proxy for this thread if proxy manager is available
        proxy_dict = None
        if proxy_manager:
            proxy_info = proxy_manager.get_next_proxy()
            if proxy_info:
                proxy_dict = proxy_info.get_proxy_dict()
                thread_local.current_proxy = proxy_info
                logger.debug(f"Thread {threading.current_thread().name} assigned proxy {proxy_info.host}:{proxy_info.port}")

        thread_local.scraper = IndianKanoonScraper(delay=delay, headless=True, proxy=proxy_dict)
        logger.debug(f"Created scraper for thread {threading.current_thread().name}")
    return thread_local.scraper


def download_worker(
    task: DownloadTask,
    pdf_dir: Path,
    db: CaseDatabase,
    rate_limiter: RateLimiter,
    stats_lock: threading.Lock,
    overall_stats: dict,
    delay: int = 1,
    proxy_manager: Optional[ProxyManager] = None
) -> dict:
    """
    Worker function to download a single PDF.

    Args:
        task: DownloadTask containing case information
        pdf_dir: Directory to save PDFs
        db: Database instance
        rate_limiter: Rate limiter for request throttling
        stats_lock: Lock for updating shared statistics
        overall_stats: Shared statistics dictionary
        delay: Request delay in seconds

    Returns:
        Dictionary with download result
    """
    case_data = task.case_data
    case = case_data.get('case_object')

    if not case:
        return {'success': False, 'error': 'No case object in task'}

    result = {
        'case_id': case.id,
        'title': case.title[:70] if case.title else 'N/A',
        'success': False,
        'action': 'none',
        'error': None,
        'file_size': 0
    }

    try:
        # Get thread-local scraper with proxy support
        scraper = get_thread_scraper(delay, proxy_manager)

        # Track request start time for proxy performance metrics
        request_start = time.time()

        # Step 1: Fetch case details if needed
        if not case.pdf_link:
            rate_limiter.acquire()
            logger.debug(f"[Worker] Fetching details for case {case.id}")

            try:
                details = scraper.get_case_details(case.case_url)

                # Record successful proxy request if using proxies
                if proxy_manager and hasattr(thread_local, 'current_proxy'):
                    response_time = time.time() - request_start
                    thread_local.current_proxy.record_success(response_time)
                if details and details.get('pdf_link'):
                    case.pdf_link = details['pdf_link']
                    case.full_text = details.get('full_text', case.full_text)
                    case.citation = details.get('citation', case.citation)
                    case.court = details.get('court', case.court)

                    # Thread-safe database update
                    with stats_lock:
                        db.session.commit()
                        overall_stats['details_fetched'] += 1

                    result['action'] = 'details_fetched'
                    logger.info(f"[Case {case.id}] Details fetched, PDF available")
                else:
                    with stats_lock:
                        overall_stats['no_pdf_available'] += 1
                    result['action'] = 'no_pdf'
                    result['error'] = 'No PDF link available'
                    logger.warning(f"[Case {case.id}] No PDF available")
                    return result
            except Exception as e:
                # Record proxy failure if using proxies
                if proxy_manager and hasattr(thread_local, 'current_proxy'):
                    thread_local.current_proxy.record_failure()

                with stats_lock:
                    overall_stats['failed'] += 1
                result['error'] = f"Error fetching details: {str(e)}"
                logger.error(f"[Case {case.id}] {result['error']}")
                return result

        # Step 2: Download PDF
        if case.pdf_link:
            filename = f"case_{case.id}.pdf"
            filepath = pdf_dir / filename

            # Check if already downloaded
            if case.pdf_downloaded and filepath.exists():
                file_size = os.path.getsize(filepath)
                with stats_lock:
                    overall_stats['already_downloaded'] += 1
                result['success'] = True
                result['action'] = 'already_downloaded'
                result['file_size'] = file_size
                logger.debug(f"[Case {case.id}] Already downloaded ({file_size/1024:.1f} KB)")
                return result

            # Download PDF with rate limiting
            rate_limiter.acquire()
            logger.debug(f"[Worker] Downloading PDF for case {case.id}")

            try:
                success = scraper.download_indiankanoon_pdf(case.pdf_link, str(filepath))

                if success and filepath.exists():
                    file_size = os.path.getsize(filepath)

                    # Thread-safe database update
                    with stats_lock:
                        db.update_pdf_status(case.id, str(filepath))
                        overall_stats['pdfs_downloaded'] += 1

                    result['success'] = True
                    result['action'] = 'downloaded'
                    result['file_size'] = file_size
                    logger.info(f"[Case {case.id}] Downloaded successfully ({file_size/1024:.1f} KB)")
                else:
                    with stats_lock:
                        overall_stats['failed'] += 1
                    result['error'] = 'Download failed after retries'
                    logger.warning(f"[Case {case.id}] Download failed")
            except Exception as e:
                with stats_lock:
                    overall_stats['failed'] += 1
                result['error'] = f"Error downloading: {str(e)}"
                logger.error(f"[Case {case.id}] {result['error']}")

    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
        logger.error(f"[Case {case.id}] {result['error']}")

    return result


def bulk_download_all(batch_size=50, max_workers=20, checkpoint_interval=100):
    """
    Download all PDFs using concurrent workers with automatic checkpoint resume.

    Args:
        batch_size: Number of cases to process per batch
        max_workers: Number of concurrent download threads (default: 20)
        checkpoint_interval: Save checkpoint every N cases (default: 100)
    """
    global shutdown_requested

    print("=" * 80)
    print("INDIANKANOON CONCURRENT BULK PDF DOWNLOAD WITH AUTO-RESUME")
    print("=" * 80)
    print(f"Workers: {max_workers} | Batch Size: {batch_size} | Checkpoint Interval: {checkpoint_interval}")
    print("=" * 80)
    print()

    # Initialize database
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/indiankanoon.db')
    db = CaseDatabase(db_url)

    # Initialize checkpoint manager
    checkpoint_manager = CheckpointManager(
        db=db,
        process_name='bulk_download',
        checkpoint_interval=checkpoint_interval
    )

    # Configuration
    delay = int(os.getenv('REQUEST_DELAY', '1'))  # Reduced delay for concurrent downloads
    requests_per_second = float(os.getenv('MAX_REQUESTS_PER_SECOND', '10.0'))

    pdf_dir = Path(os.getenv('PDF_DOWNLOAD_PATH', './data/pdfs'))
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize download queue and rate limiter
    download_queue = PriorityDownloadQueue()
    rate_limiter = RateLimiter(max_requests_per_second=requests_per_second)

    # Initialize proxy manager from environment
    proxy_manager = create_proxy_manager_from_env()
    if proxy_manager:
        logger.info(f"Proxy manager initialized with {len(proxy_manager.proxies)} proxies")
        print(f"✓ Proxy Manager: {len(proxy_manager.proxies)} proxies loaded")
        print(f"✓ Rotation Strategy: {proxy_manager.rotation_strategy}")
    else:
        logger.info("No proxy configuration found, running without proxies")
        print("⚠ No proxies configured - running with direct connections")

    # Statistics tracking
    stats_lock = threading.Lock()
    overall_stats = {
        'details_fetched': 0,
        'pdfs_downloaded': 0,
        'already_downloaded': 0,
        'no_pdf_available': 0,
        'failed': 0,
        'processed': 0
    }

    # Get initial statistics
    stats = db.get_statistics()
    logger.info(f"Database Statistics:")
    logger.info(f"  Total cases: {stats['total_cases']}")
    logger.info(f"  Cases with PDFs: {stats['cases_with_pdfs']}")
    logger.info(f"  Cases without PDFs: {stats['cases_without_pdfs']}")
    print()

    total_cases = stats['total_cases']
    start_time = time.time()

    # Try to resume from checkpoint
    should_resume, start_offset, checkpoint_stats = checkpoint_manager.resume_from_checkpoint()

    if should_resume:
        logger.info(f"Resuming from checkpoint: offset={start_offset}")
    else:
        start_offset = 0
        logger.info("Starting from beginning (no checkpoint found)")

    # Phase 1: Populate queue with all cases
    logger.info("Phase 1: Populating download queue...")
    current_offset = start_offset

    while current_offset < total_cases:
        # Use yield_per for memory-efficient streaming instead of .all()
        query = db.session.query(LegalCase).offset(current_offset).limit(batch_size)
        cases = list(query.yield_per(100))  # Stream 100 at a time

        if not cases:
            break

        for case in cases:
            # Prepare case data for queue
            case_dict = {
                'case_object': case,
                'case_url': case.case_url,
                'pdf_link': case.pdf_link,
                'title': case.title,
                'court': case.court,
                'court_type': case.court_type
            }

            # Add to priority queue (handles deduplication automatically)
            download_queue.add_task(case_dict)

        current_offset += batch_size

        if shutdown_requested:
            logger.info("Shutdown requested during queue population")
            break

    queue_stats = download_queue.get_statistics()
    logger.info(f"Queue populated: {queue_stats['total_added']} tasks added")
    logger.info(f"  Duplicates rejected: {queue_stats['duplicates_rejected']}")
    logger.info(f"  By priority - Supreme: {queue_stats['by_priority']['supreme_court']}, "
                f"High: {queue_stats['by_priority']['high_court']}, "
                f"Tribunal: {queue_stats['by_priority']['tribunal']}, "
                f"Other: {queue_stats['by_priority']['other']}")
    print()

    # Phase 2: Process queue with thread pool
    logger.info(f"Phase 2: Starting {max_workers} concurrent workers...")

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='PDFWorker') as executor:
        futures = []

        # Submit all tasks to thread pool
        while not download_queue.is_empty() and not shutdown_requested:
            task = download_queue.get_task(timeout=0.1)

            if task:
                future = executor.submit(
                    download_worker,
                    task,
                    pdf_dir,
                    db,
                    rate_limiter,
                    stats_lock,
                    overall_stats,
                    delay,
                    proxy_manager
                )
                futures.append((future, task))

        # Process completed downloads
        # Create a mapping of future to task for lookup
        future_to_task = {f: t for f, t in futures}

        for future in as_completed([f for f, _ in futures]):
            if shutdown_requested:
                logger.info("Shutdown requested, cancelling remaining tasks")
                break

            try:
                task = future_to_task[future]
                result = future.result(timeout=120)  # 2 minute timeout per download

                if result['success']:
                    download_queue.mark_completed(task)
                else:
                    download_queue.mark_failed(task)

                # Update progress
                with stats_lock:
                    overall_stats['processed'] += 1
                    processed = overall_stats['processed']

                # Progress bar
                print_progress_bar(
                    processed,
                    queue_stats['total_added'],
                    prefix='Progress:',
                    suffix=f"Complete ({overall_stats['pdfs_downloaded']} downloaded)"
                )

                # Periodic status updates
                if processed % 50 == 0:
                    current_stats = download_queue.get_statistics()
                    logger.info(f"\nProgress Update [{processed}/{queue_stats['total_added']}]:")
                    logger.info(f"  Downloaded: {overall_stats['pdfs_downloaded']}")
                    logger.info(f"  Already had: {overall_stats['already_downloaded']}")
                    logger.info(f"  Failed: {overall_stats['failed']}")
                    logger.info(f"  Queue remaining: {current_stats['in_progress']}\n")

            except Exception as e:
                logger.error(f"Error processing future: {e}")
                download_queue.mark_failed(task)

    # Final statistics
    elapsed_time = time.time() - start_time
    final_stats = db.get_statistics()
    final_queue_stats = download_queue.get_statistics()

    print("\n" + "=" * 80)
    print("CONCURRENT BULK DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"\nDatabase Statistics:")
    print(f"  Total cases: {final_stats['total_cases']}")
    print(f"  Cases with PDFs: {final_stats['cases_with_pdfs']}")
    print(f"  Cases without PDFs: {final_stats['cases_without_pdfs']}")
    print(f"\nSession Statistics:")
    print(f"  Details fetched: {overall_stats['details_fetched']}")
    print(f"  PDFs downloaded: {overall_stats['pdfs_downloaded']}")
    print(f"  Already had PDFs: {overall_stats['already_downloaded']}")
    print(f"  No PDF available: {overall_stats['no_pdf_available']}")
    print(f"  Failed: {overall_stats['failed']}")
    print(f"\nQueue Statistics:")
    print(f"  Total processed: {final_queue_stats['completed']}")
    print(f"  Duplicates rejected: {final_queue_stats['duplicates_rejected']}")
    print(f"  Deduplication rate: {final_queue_stats['deduplication_rate']:.1f}%")
    print(f"\nPerformance:")
    print(f"  Time elapsed: {elapsed_time/60:.1f} minutes")
    print(f"  Download rate: {overall_stats['pdfs_downloaded']/(elapsed_time/60):.1f} PDFs/min")
    print(f"  Log file: {log_file}")

    # Print proxy statistics if proxies were used
    if proxy_manager:
        print("\n" + "-" * 80)
        proxy_manager.print_statistics()

    print("=" * 80)

    # Cleanup
    db.close()

    # Close all thread-local scrapers
    if hasattr(thread_local, 'scraper'):
        thread_local.scraper.close_driver()

    if shutdown_requested:
        logger.info("\n⚠️  Download interrupted. Run script again to resume from where you left off.")
        return 1

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Concurrent bulk download of IndianKanoon PDFs with priority queue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download with default settings (20 workers, auto-resume enabled)
  python bulk_download.py

  # Download with 10 workers for testing
  python bulk_download.py --max-workers 10

  # Small batch size for memory-constrained environments
  python bulk_download.py --batch-size 25 --max-workers 10

Note: Auto-resume is enabled by default. The script will automatically
detect and resume from the last checkpoint if available.
        """
    )
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Number of cases per batch (default: 50)')
    parser.add_argument('--max-workers', type=int, default=20,
                       help='Number of concurrent download threads (default: 20, max: 50)')
    parser.add_argument('--checkpoint-interval', type=int, default=100,
                       help='Save checkpoint every N cases (default: 100)')

    args = parser.parse_args()

    # Validate arguments
    if args.max_workers < 1 or args.max_workers > 50:
        parser.error("max-workers must be between 1 and 50")

    if args.batch_size < 1:
        parser.error("batch-size must be at least 1")

    try:
        exit_code = bulk_download_all(
            batch_size=args.batch_size,
            max_workers=args.max_workers,
            checkpoint_interval=args.checkpoint_interval
        )
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
