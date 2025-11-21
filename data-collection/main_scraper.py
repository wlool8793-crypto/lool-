#!/usr/bin/env python3
"""
IndianKanoon Production Scraper - Main Orchestrator
Command-line interface for collecting and downloading 1.4M+ legal documents
"""

import argparse
import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.url_collector import URLCollector
from scraper.drive_manager import DriveManager
from scraper.download_manager import DownloadManager
from src.database import CaseDatabase

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/production_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = './config/config_production.yaml') -> Dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"✓ Configuration loaded from: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)


def mode_collect(config: Dict, args):
    """
    Mode 1: Collect all document URLs from IndianKanoon.

    Args:
        config: Configuration dictionary
        args: Command-line arguments
    """
    logger.info("\n" + "=" * 70)
    logger.info("MODE: COLLECT URLS")
    logger.info("=" * 70)

    # Initialize database
    db_path = config.get('database', {}).get('url', 'sqlite:///data/indiankanoon_production.db')
    db = CaseDatabase(db_path)

    try:
        # Initialize URL collector
        with URLCollector(config) as collector:
            # Collect URLs
            stats = collector.collect_urls(start_page=args.start_page)

            # Save URLs to database
            logger.info("\nSaving URLs to database...")
            url_metadata = collector.get_url_metadata()

            saved_count = db.bulk_save_urls(url_metadata)
            logger.info(f"✓ Saved {saved_count} URLs to database")

            # Print final stats
            progress = db.get_download_progress()
            logger.info("\n" + "=" * 70)
            logger.info("Database Status")
            logger.info("=" * 70)
            logger.info(f"Total URLs in database: {progress['total_urls']}")
            logger.info(f"Pending download: {progress['status_breakdown'].get('PENDING', 0)}")
            logger.info("=" * 70)

    finally:
        db.close()


def mode_scrape(config: Dict, args):
    """
    Mode 2: Download PDFs and upload to Google Drive.

    Args:
        config: Configuration dictionary
        args: Command-line arguments
    """
    logger.info("\n" + "=" * 70)
    logger.info("MODE: DOWNLOAD & UPLOAD PDFs")
    logger.info("=" * 70)

    # Initialize database
    db_path = config.get('database', {}).get('url', 'sqlite:///data/indiankanoon_production.db')
    db = CaseDatabase(db_path)

    try:
        # Check for URLs
        progress = db.get_download_progress()
        if progress['total_urls'] == 0:
            logger.error("No URLs found in database. Run with --mode collect first.")
            return

        logger.info(f"Total URLs in database: {progress['total_urls']}")
        logger.info(f"Pending downloads: {progress['status_breakdown'].get('PENDING', 0)}")

        # Get URLs to download
        batch_size = args.batch_size or config.get('scraper', {}).get('batch_size', 1000)
        urls_to_download = db.get_urls_to_download(batch_size)

        if not urls_to_download:
            logger.info("✓ No pending URLs. All downloads complete!")
            return

        logger.info(f"\nProcessing {len(urls_to_download)} documents...")

        # Initialize Drive Manager if enabled
        drive_manager = None
        if config.get('google_drive', {}).get('enabled', True):
            try:
                drive_manager = DriveManager(config)
                drive_manager.authenticate()
                logger.info("✓ Google Drive authenticated")
            except Exception as e:
                logger.warning(f"Google Drive authentication failed: {e}")
                logger.warning("Continuing without Drive upload...")

        # Initialize Download Manager
        download_manager = DownloadManager(config, drive_manager)

        # Start downloads
        result = download_manager.download_pdfs(urls_to_download)

        # Update database with results
        logger.info("\nUpdating database...")
        for download_result in result['results']:
            url_id = next((u['id'] for u in urls_to_download if u['url'] == download_result['url']), None)

            if url_id:
                if download_result['success']:
                    from src.database import DownloadStatus
                    db.update_download_status(
                        url_id,
                        DownloadStatus.COMPLETED,
                        download_result['file_path'],
                        os.path.getsize(download_result['file_path']) if download_result['file_path'] else None
                    )
                else:
                    from src.database import DownloadStatus
                    db.update_download_status(
                        url_id,
                        DownloadStatus.FAILED,
                        error_message=download_result.get('error')
                    )

        # Final progress
        final_progress = db.get_download_progress()
        logger.info("\n" + "=" * 70)
        logger.info("Final Database Status")
        logger.info("=" * 70)
        logger.info(f"Total URLs: {final_progress['total_urls']}")
        logger.info(f"Downloaded: {final_progress['pdfs_downloaded']}")
        logger.info(f"Uploaded to Drive: {final_progress['uploaded_to_drive']}")
        logger.info(f"Completion: {final_progress['completion_rate']:.2f}%")
        logger.info("=" * 70)

    finally:
        db.close()


def mode_status(config: Dict, args):
    """
    Mode 3: Show current progress and statistics.

    Args:
        config: Configuration dictionary
        args: Command-line arguments
    """
    logger.info("\n" + "=" * 70)
    logger.info("MODE: STATUS")
    logger.info("=" * 70)

    # Initialize database
    db_path = config.get('database', {}).get('url', 'sqlite:///data/indiankanoon_production.db')
    db = CaseDatabase(db_path)

    try:
        progress = db.get_download_progress()

        logger.info("\n" + "─" * 70)
        logger.info("📊 OVERALL PROGRESS")
        logger.info("─" * 70)
        logger.info(f"Total URLs collected: {progress['total_urls']:,}")
        logger.info(f"PDFs downloaded: {progress['pdfs_downloaded']:,}")
        logger.info(f"Uploaded to Drive: {progress['uploaded_to_drive']:,}")
        logger.info(f"Download completion: {progress['completion_rate']:.2f}%")
        logger.info(f"Upload completion: {progress['upload_rate']:.2f}%")

        logger.info("\n" + "─" * 70)
        logger.info("📋 STATUS BREAKDOWN")
        logger.info("─" * 70)
        for status, count in progress['status_breakdown'].items():
            logger.info(f"{status:15s}: {count:,}")

        # Estimate remaining time
        if progress['pdfs_downloaded'] > 0:
            rate = 500  # Estimated docs/hour
            remaining = progress['total_urls'] - progress['pdfs_downloaded']
            hours_remaining = remaining / rate
            days_remaining = hours_remaining / 24

            logger.info("\n" + "─" * 70)
            logger.info("⏱️  ESTIMATED COMPLETION")
            logger.info("─" * 70)
            logger.info(f"Remaining documents: {remaining:,}")
            logger.info(f"Estimated time (@ 500 docs/hr): {hours_remaining:.1f} hours ({days_remaining:.1f} days)")

        logger.info("=" * 70)

    finally:
        db.close()


def mode_resume(config: Dict, args):
    """
    Mode 4: Resume interrupted downloads.

    Args:
        config: Configuration dictionary
        args: Command-line arguments
    """
    logger.info("\n" + "=" * 70)
    logger.info("MODE: RESUME DOWNLOADS")
    logger.info("=" * 70)

    # Initialize database
    db_path = config.get('database', {}).get('url', 'sqlite:///data/indiankanoon_production.db')
    db = CaseDatabase(db_path)

    try:
        # Get failed URLs that can be retried
        failed_urls = db.get_failed_urls(max_attempts=3, limit=args.batch_size or 1000)

        if not failed_urls:
            logger.info("✓ No failed URLs to retry. Checking for pending URLs...")

            # Try pending URLs instead
            pending_urls = db.get_pending_urls(limit=args.batch_size or 1000)

            if not pending_urls:
                logger.info("✓ No pending URLs. All downloads complete!")
                return

            logger.info(f"Found {len(pending_urls)} pending URLs. Resuming...")

        else:
            logger.info(f"Found {len(failed_urls)} failed URLs to retry.")

        # Convert to download format
        urls_to_download = db.get_urls_to_download(args.batch_size or 1000)

        if urls_to_download:
            # Reuse scrape mode logic
            args.mode = 'scrape'
            mode_scrape(config, args)
        else:
            logger.info("Nothing to resume.")

    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='IndianKanoon Production Scraper - Download 1.4M+ legal documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect all URLs
  python main_scraper.py --mode collect

  # Download PDFs (first 1000)
  python main_scraper.py --mode scrape --batch-size 1000

  # Check status
  python main_scraper.py --mode status

  # Resume interrupted downloads
  python main_scraper.py --mode resume

  # Test with limited pages
  python main_scraper.py --mode collect --max-pages 10
        """
    )

    parser.add_argument(
        '--mode',
        choices=['collect', 'scrape', 'status', 'resume'],
        required=True,
        help='Operation mode'
    )

    parser.add_argument(
        '--config',
        default='./config/config_production.yaml',
        help='Path to configuration file (default: ./config/config_production.yaml)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        help='Number of documents to process in this run (overrides config)'
    )

    parser.add_argument(
        '--start-page',
        type=int,
        default=0,
        help='Start from specific page (for collect mode)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum pages to collect (for testing, overrides config)'
    )

    args = parser.parse_args()

    # Create logs directory if not exists
    Path('./logs').mkdir(exist_ok=True)

    # Load configuration
    config = load_config(args.config)

    # Override config with command-line arguments
    if args.max_pages:
        config.setdefault('url_collection', {})['max_pages'] = args.max_pages

    # Route to appropriate mode
    try:
        if args.mode == 'collect':
            mode_collect(config, args)
        elif args.mode == 'scrape':
            mode_scrape(config, args)
        elif args.mode == 'status':
            mode_status(config, args)
        elif args.mode == 'resume':
            mode_resume(config, args)
    except KeyboardInterrupt:
        logger.warning("\n⚠ Interrupted by user. Progress has been saved.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
