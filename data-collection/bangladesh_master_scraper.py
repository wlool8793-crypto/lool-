#!/usr/bin/env python3
"""
Bangladesh Master Scraper - CLI Orchestrator
Comprehensive CLI for managing and orchestrating Bangladesh legal data scraping
"""

import argparse
import logging
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.scrapers.bangladesh.source_registry import BangladeshSourceRegistry
from src.scrapers.bangladesh.plugin_manager import PluginManager

# Try to import DriveManager, make it optional if not available
try:
    from scraper.drive_manager import DriveManager
    DRIVE_MANAGER_AVAILABLE = True
except ImportError:
    DRIVE_MANAGER_AVAILABLE = False
    DriveManager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bangladesh_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BangladeshMasterScraper:
    """Master CLI orchestrator for Bangladesh legal data scraping"""

    def __init__(self):
        self.registry = BangladeshSourceRegistry()
        self.plugin_manager = PluginManager(self.registry)
        self.drive_manager = None

    def setup_drive(self, config_path: Optional[str] = None):
        """Setup Google Drive integration"""
        if not DRIVE_MANAGER_AVAILABLE:
            logger.warning("Google Drive integration not available (missing dependencies)")
            self.drive_manager = None
            return

        try:
            if config_path:
                self.drive_manager = DriveManager(config_path)
            else:
                # Try default config
                self.drive_manager = DriveManager()
            logger.info("Google Drive integration initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Google Drive: {e}")
            self.drive_manager = None

    def list_sources(self, tier: Optional[int] = None, type_filter: Optional[str] = None) -> Dict[str, Any]:
        """List available sources"""
        sources = []

        if tier:
            sources = self.registry.get_sources_by_tier(tier)
        elif type_filter:
            sources = self.registry.get_sources_by_type(type_filter)
        else:
            sources = self.registry.get_all_sources()

        return {
            'total_count': len(sources),
            'sources': [
                {
                    'name': source.name,
                    'url': source.url,
                    'tier': source.tier,
                    'type': source.source_type,
                    'description': source.description,
                    'auth_required': source.auth_required,
                    'has_pdfs': source.has_pdfs
                }
                for source in sources
            ]
        }

    def test_connections(self, source_names: Optional[List[str]] = None) -> Dict[str, bool]:
        """Test connections to sources"""
        if source_names:
            results = {}
            for name in source_names:
                scraper = self.plugin_manager.get_scraper(name)
                if scraper:
                    results[name] = scraper.test_connection()
                else:
                    results[name] = False
            return results
        else:
            return self.plugin_manager.test_all_connections()

    def scrape_sources(self, source_names: List[str], concurrent: bool = True,
                      upload_drive: bool = False, **scraping_kwargs) -> Dict[str, Any]:
        """Scrape specific sources"""
        logger.info(f"Starting scraping of {len(source_names)} sources")

        start_time = datetime.now()

        # Perform scraping
        results = self.plugin_manager.scrape_multiple(
            source_names,
            concurrent=concurrent,
            **scraping_kwargs
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Calculate statistics
        successful_sources = [name for name, result in results.items() if result.success]
        failed_sources = [name for name, result in results.items() if not result.success]
        total_documents = sum(result.count for result in results.values())

        summary = {
            'duration_seconds': duration,
            'total_sources': len(source_names),
            'successful_sources': len(successful_sources),
            'failed_sources': len(failed_sources),
            'total_documents_scraped': total_documents,
            'success_rate': (len(successful_sources) / len(source_names)) * 100,
            'results': {
                name: {
                    'success': result.success,
                    'count': result.count,
                    'message': result.message,
                    'metadata': result.metadata
                }
                for name, result in results.items()
            }
        }

        # Upload to Google Drive if requested
        if upload_drive and self.drive_manager:
            try:
                self._upload_results_to_drive(results, summary)
                summary['drive_upload'] = 'success'
            except Exception as e:
                logger.error(f"Failed to upload to Google Drive: {e}")
                summary['drive_upload'] = f'failed: {e}'

        return summary

    def scrape_tier(self, tier: int, concurrent: bool = True, upload_drive: bool = False) -> Dict[str, Any]:
        """Scrape all sources in a specific tier"""
        tier_sources = self.registry.get_sources_by_tier(tier)
        source_names = [source.name for source in tier_sources]

        if not source_names:
            return {
                'error': f'No sources found in tier {tier}',
                'tier': tier
            }

        logger.info(f"Scraping tier {tier} ({len(source_names)} sources)")
        return self.scrape_sources(source_names, concurrent=concurrent, upload_drive=upload_drive)

    def scrape_all(self, only_free: bool = True, concurrent: bool = True, upload_drive: bool = False) -> Dict[str, Any]:
        """Scrape all available sources"""
        if only_free:
            sources = self.registry.get_no_auth_sources()
            logger.info("Scraping all free sources (no authentication required)")
        else:
            sources = self.registry.get_all_sources()
            logger.info("Scraping all sources (including those requiring authentication)")

        source_names = [source.name for source in sources]
        return self.scrape_sources(source_names, concurrent=concurrent, upload_drive=upload_drive)

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        # Registry statistics
        registry_stats = self.registry.get_source_stats()

        # Plugin manager statistics
        plugin_stats = self.plugin_manager.get_statistics()

        # Combine statistics
        return {
            'registry': registry_stats,
            'plugin_manager': plugin_stats,
            'summary': {
                'total_sources': registry_stats['total_sources'],
                'available_scrapers': plugin_stats['available_scrapers'],
                'total_estimated_documents': sum(
                    source.config.get('estimated_docs', 0)
                    for source in self.registry.get_all_sources()
                )
            }
        }

    def search_sources(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for sources by name or description"""
        matching_sources = self.registry.search_sources(query)

        # Limit results
        if len(matching_sources) > max_results:
            matching_sources = matching_sources[:max_results]

        return {
            'query': query,
            'total_matches': len(matching_sources),
            'sources': [
                {
                    'name': source.name,
                    'url': source.url,
                    'tier': source.tier,
                    'type': source.source_type,
                    'description': source.description
                }
                for source in matching_sources
            ]
        }

    def _upload_results_to_drive(self, results: Dict[str, Any], summary: Dict[str, Any]):
        """Upload scraping results to Google Drive"""
        if not self.drive_manager:
            return

        # Create timestamped folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_path = f"BD/Scraping_Results/{timestamp}"

        # Upload summary
        summary_json = json.dumps(summary, indent=2, default=str)
        self.drive_manager.upload_file(
            content=summary_json,
            filename=f"{folder_path}/scraping_summary.json",
            content_type='application/json'
        )

        # Upload individual results
        for source_name, result in results.items():
            if result.success and result.documents:
                documents_json = json.dumps(
                    [doc.__dict__ if hasattr(doc, '__dict__') else str(doc) for doc in result.documents],
                    indent=2,
                    default=str
                )
                self.drive_manager.upload_file(
                    content=documents_json,
                    filename=f"{folder_path}/{source_name}_documents.json",
                    content_type='application/json'
                )

        logger.info(f"Uploaded scraping results to Google Drive: {folder_path}")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Bangladesh Master Scraper - Comprehensive legal data scraping system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all Tier 1 government sources
  python bangladesh_master_scraper.py list --tier 1

  # Test connections to all sources
  python bangladesh_master_scraper.py test

  # Scrape Tier 1 sources concurrently
  python bangladesh_master_scraper.py scrape-tier 1 --concurrent

  # Scrape specific sources
  python bangladesh_master_scraper.py scrape-sources bdlaws supreme_court

  # Get statistics
  python bangladesh_master_scraper.py stats

  # Search for sources
  python bangladesh_master_scraper.py search "cyber tribunal"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List sources command
    list_parser = subparsers.add_parser('list', help='List available sources')
    list_parser.add_argument('--tier', type=int, choices=[1, 2, 3, 4],
                            help='Filter by tier (1=gov, 2=commercial, 3=tribunals, 4=international)')
    list_parser.add_argument('--type', help='Filter by source type')

    # Test connections command
    test_parser = subparsers.add_parser('test', help='Test connections to sources')
    test_parser.add_argument('sources', nargs='*', help='Specific sources to test (optional)')

    # Scrape sources command
    scrape_sources_parser = subparsers.add_parser('scrape-sources', help='Scrape specific sources')
    scrape_sources_parser.add_argument('sources', nargs='+', help='Source names to scrape')
    scrape_sources_parser.add_argument('--no-concurrent', action='store_true',
                                      help='Run sequentially instead of concurrently')
    scrape_sources_parser.add_argument('--upload-drive', action='store_true',
                                      help='Upload results to Google Drive')
    scrape_sources_parser.add_argument('--limit', type=int, help='Limit number of documents per source')
    scrape_sources_parser.add_argument('--resume', action='store_true',
                                      help='Resume from previous scraping session')

    # Scrape tier command
    scrape_tier_parser = subparsers.add_parser('scrape-tier', help='Scrape all sources in a tier')
    scrape_tier_parser.add_argument('tier', type=int, choices=[1, 2, 3, 4],
                                   help='Tier to scrape (1=gov, 2=commercial, 3=tribunals, 4=international)')
    scrape_tier_parser.add_argument('--no-concurrent', action='store_true',
                                   help='Run sequentially instead of concurrently')
    scrape_tier_parser.add_argument('--upload-drive', action='store_true',
                                   help='Upload results to Google Drive')

    # Scrape all command
    scrape_all_parser = subparsers.add_parser('scrape-all', help='Scrape all available sources')
    scrape_all_parser.add_argument('--include-auth', action='store_true',
                                 help='Include sources requiring authentication')
    scrape_all_parser.add_argument('--no-concurrent', action='store_true',
                                 help='Run sequentially instead of concurrently')
    scrape_all_parser.add_argument('--upload-drive', action='store_true',
                                 help='Upload results to Google Drive')

    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show comprehensive statistics')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for sources')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--max-results', type=int, default=10,
                              help='Maximum number of results (default: 10)')

    # Global options
    parser.add_argument('--drive-config', help='Path to Google Drive configuration file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Set logging level')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')

    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    if args.quiet:
        logging.getLogger().handlers[1].setLevel(logging.WARNING)  # Console handler

    log_level = getattr(logging, args.log_level)
    logging.getLogger().setLevel(log_level)

    if not args.command:
        parser.print_help()
        return 1

    # Initialize master scraper
    try:
        master = BangladeshMasterScraper()

        # Setup Google Drive if requested
        if hasattr(args, 'upload_drive') and args.upload_drive:
            master.setup_drive(args.drive_config)

        # Execute command
        if args.command == 'list':
            result = master.list_sources(args.tier, args.type)
            print(json.dumps(result, indent=2))

        elif args.command == 'test':
            result = master.test_connections(args.sources if args.sources else None)
            print(json.dumps(result, indent=2))

        elif args.command == 'scrape-sources':
            scraping_kwargs = {}
            if args.limit:
                scraping_kwargs['limit'] = args.limit
            if args.resume:
                scraping_kwargs['resume'] = True

            result = master.scrape_sources(
                args.sources,
                concurrent=not args.no_concurrent,
                upload_drive=args.upload_drive,
                **scraping_kwargs
            )
            print(json.dumps(result, indent=2, default=str))

        elif args.command == 'scrape-tier':
            result = master.scrape_tier(
                args.tier,
                concurrent=not args.no_concurrent,
                upload_drive=args.upload_drive
            )
            print(json.dumps(result, indent=2, default=str))

        elif args.command == 'scrape-all':
            result = master.scrape_all(
                only_free=not args.include_auth,
                concurrent=not args.no_concurrent,
                upload_drive=args.upload_drive
            )
            print(json.dumps(result, indent=2, default=str))

        elif args.command == 'stats':
            result = master.get_statistics()
            print(json.dumps(result, indent=2, default=str))

        elif args.command == 'search':
            result = master.search_sources(args.query, args.max_results)
            print(json.dumps(result, indent=2))

        return 0

    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())