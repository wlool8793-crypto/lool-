"""
Bangladesh Plugin Manager
Orchestrates multiple Bangladesh legal data scrapers with dynamic loading
"""

import logging
import importlib
import traceback
from typing import Dict, List, Optional, Any, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import time
import os
import sys

from .base_scraper import BaseLegalScraper, ScrapingResult, StubScraper
from .source_registry import BangladeshSourceRegistry, SourceInfo

logger = logging.getLogger(__name__)


@dataclass
class ScraperStatus:
    """Status of a scraper instance"""
    name: str
    loaded: bool
    available: bool
    last_run: Optional[datetime] = None
    last_result: Optional[ScrapingResult] = None
    error_count: int = 0
    total_documents: int = 0
    run_time: float = 0.0


class PluginManager:
    """
    Manages and orchestrates Bangladesh legal data scrapers
    Handles dynamic loading, execution, and monitoring of all scrapers
    """

    def __init__(self, registry: Optional[BangladeshSourceRegistry] = None, max_workers: int = 5):
        """
        Initialize the plugin manager

        Args:
            registry: Source registry instance (creates default if None)
            max_workers: Maximum number of concurrent scrapers
        """
        self.registry = registry or BangladeshSourceRegistry()
        self.max_workers = max_workers
        self.scrapers: Dict[str, BaseLegalScraper] = {}
        self.scraper_classes: Dict[str, Type[BaseLegalScraper]] = {}
        self.status: Dict[str, ScraperStatus] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load all available scrapers
        self._load_all_scrapers()

        logger.info(f"Plugin Manager initialized with {len(self.scrapers)} scrapers")

    def _load_all_scrapers(self):
        """Dynamically load all available scraper classes"""
        self.logger.info("Loading Bangladesh scraper plugins...")

        # Get the directory containing this file
        current_dir = os.path.dirname(__file__)

        # Import all scrapers from tier directories
        tier_dirs = ['tier1', 'tier2', 'tier3', 'other']

        for tier_dir in tier_dirs:
            tier_path = os.path.join(current_dir, tier_dir)
            if not os.path.exists(tier_path):
                continue

            # Add tier directory to Python path
            if tier_path not in sys.path:
                sys.path.insert(0, tier_path)

            # Try to import all Python files in the tier directory
            for filename in os.listdir(tier_path):
                if filename.endswith('_scraper.py') and not filename.startswith('__'):
                    module_name = filename[:-3]  # Remove .py extension
                    source_name = module_name.replace('_scraper', '')

                    try:
                        # Import the module
                        module = importlib.import_module(module_name)

                        # Find scraper class in the module
                        scraper_class = self._find_scraper_class(module, source_name)
                        if scraper_class:
                            self.scraper_classes[source_name] = scraper_class
                            self.logger.info(f"Loaded scraper class: {source_name}")

                            # Initialize status
                            self.status[source_name] = ScraperStatus(
                                name=source_name,
                                loaded=True,
                                available=True
                            )

                    except Exception as e:
                        self.logger.error(f"Failed to load scraper {source_name}: {e}")
                        self.status[source_name] = ScraperStatus(
                            name=source_name,
                            loaded=False,
                            available=False
                        )

        # Create stub scrapers for sources without implementations
        self._create_stub_scrapers()

    def _find_scraper_class(self, module, source_name: str) -> Optional[Type[BaseLegalScraper]]:
        """Find the scraper class in a module"""
        class_name = f"{source_name.replace('_', ' ').title().replace(' ', '')}Scraper"
        alternatives = [
            class_name,
            f"{source_name}Scraper",
            f"{source_name.title()}Scraper"
        ]

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, BaseLegalScraper) and
                attr != BaseLegalScraper and
                attr != StubScraper):
                return attr

        return None

    def _create_stub_scrapers(self):
        """Create stub scrapers for sources that don't have implementations"""
        all_sources = set(self.registry.sources.keys())
        implemented_sources = set(self.scraper_classes.keys())

        for source_name in all_sources - implemented_sources:
            source_info = self.registry.get_source(source_name)
            if source_info:
                # Create a stub scraper
                stub_class = type(
                    f"{source_name.title()}StubScraper",
                    (StubScraper,),
                    {}
                )
                self.scraper_classes[source_name] = stub_class
                self.logger.info(f"Created stub scraper for: {source_name}")

                self.status[source_name] = ScraperStatus(
                    name=source_name,
                    loaded=True,
                    available=False  # Mark as not available for actual scraping
                )

    def get_scraper(self, source_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseLegalScraper]:
        """
        Get or create a scraper instance for a specific source

        Args:
            source_name: Name of the source
            config: Optional configuration overrides

        Returns:
            Scraper instance or None if not available
        """
        if source_name not in self.scraper_classes:
            self.logger.error(f"No scraper class found for {source_name}")
            return None

        try:
            # Get source configuration
            source_info = self.registry.get_source(source_name)
            if not source_info:
                self.logger.error(f"No source configuration found for {source_name}")
                return None

            # Merge configurations
            scraper_config = source_info.config.copy()
            if config:
                scraper_config.update(config)

            # Add source name to config
            scraper_config['source_name'] = source_name
            scraper_config['base_url'] = source_info.url

            # Create scraper instance
            scraper_class = self.scraper_classes[source_name]
            scraper = scraper_class(scraper_config)

            # Cache the scraper
            self.scrapers[source_name] = scraper

            return scraper

        except Exception as e:
            self.logger.error(f"Failed to create scraper for {source_name}: {e}")
            return None

    def scrape_source(self, source_name: str, **kwargs) -> ScrapingResult:
        """
        Scrape documents from a specific source

        Args:
            source_name: Name of the source to scrape
            **kwargs: Scraping parameters

        Returns:
            ScrapingResult with documents and metadata
        """
        start_time = time.time()

        try:
            scraper = self.get_scraper(source_name)
            if not scraper:
                return ScrapingResult(
                    success=False,
                    count=0,
                    message=f"Failed to create scraper for {source_name}",
                    metadata={'source': source_name}
                )

            # Test connection first
            if not scraper.test_connection():
                return ScrapingResult(
                    success=False,
                    count=0,
                    message=f"Connection test failed for {source_name}",
                    metadata={'source': source_name}
                )

            # Perform scraping
            result = scraper.scrape_all(**kwargs)

            # Update status
            run_time = time.time() - start_time
            if source_name in self.status:
                self.status[source_name].last_run = datetime.now()
                self.status[source_name].last_result = result
                self.status[source_name].total_documents += result.count
                self.status[source_name].run_time += run_time
                if not result.success:
                    self.status[source_name].error_count += 1

            return result

        except Exception as e:
            error_msg = f"Scraping failed for {source_name}: {str(e)}"
            self.logger.error(error_msg)

            # Update status
            if source_name in self.status:
                self.status[source_name].error_count += 1

            return ScrapingResult(
                success=False,
                count=0,
                message=error_msg,
                metadata={'source': source_name, 'error': str(e)}
            )

    def scrape_multiple(self, source_names: List[str], concurrent: bool = False, **kwargs) -> Dict[str, ScrapingResult]:
        """
        Scrape multiple sources

        Args:
            source_names: List of source names to scrape
            concurrent: Whether to run scrapers concurrently
            **kwargs: Scraping parameters

        Returns:
            Dictionary mapping source names to ScrapingResults
        """
        results = {}

        if concurrent and len(source_names) > 1:
            # Run scrapers concurrently
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(source_names))) as executor:
                future_to_source = {
                    executor.submit(self.scrape_source, source_name, **kwargs): source_name
                    for source_name in source_names
                }

                for future in as_completed(future_to_source):
                    source_name = future_to_source[future]
                    try:
                        result = future.result()
                        results[source_name] = result
                    except Exception as e:
                        self.logger.error(f"Concurrent scraping failed for {source_name}: {e}")
                        results[source_name] = ScrapingResult(
                            success=False,
                            count=0,
                            message=f"Concurrent scraping error: {str(e)}",
                            metadata={'source': source_name}
                        )
        else:
            # Run scrapers sequentially
            for source_name in source_names:
                result = self.scrape_source(source_name, **kwargs)
                results[source_name] = result

        return results

    def scrape_tier(self, tier: int, **kwargs) -> Dict[str, ScrapingResult]:
        """
        Scrape all sources in a specific tier

        Args:
            tier: Tier number (1-4)
            **kwargs: Scraping parameters

        Returns:
            Dictionary mapping source names to ScrapingResults
        """
        tier_sources = self.registry.get_sources_by_tier(tier)
        source_names = [source.name for source in tier_sources]

        self.logger.info(f"Scraping {len(source_names)} sources from tier {tier}")

        return self.scrape_multiple(source_names, concurrent=True, **kwargs)

    def scrape_all(self, only_free: bool = True, **kwargs) -> Dict[str, ScrapingResult]:
        """
        Scrape all available sources

        Args:
            only_free: Only scrape sources that don't require authentication
            **kwargs: Scraping parameters

        Returns:
            Dictionary mapping source names to ScrapingResults
        """
        if only_free:
            sources = self.registry.get_no_auth_sources()
        else:
            sources = self.registry.get_all_sources()

        source_names = [source.name for source in sources]

        self.logger.info(f"Scraping {len(source_names)} sources (only_free={only_free})")

        # Run in priority order (tier 1 first)
        priority_order = self.registry.get_priority_order()
        filtered_names = [name for name in priority_order if name in source_names]

        return self.scrape_multiple(filtered_names, concurrent=True, **kwargs)

    def get_status(self) -> Dict[str, ScraperStatus]:
        """Get status of all scrapers"""
        return self.status.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about scraping operations"""
        stats = {
            'total_sources': len(self.status),
            'loaded_scrapers': len([s for s in self.status.values() if s.loaded]),
            'available_scrapers': len([s for s in self.status.values() if s.available]),
            'total_documents_scraped': sum(s.total_documents for s in self.status.values()),
            'total_errors': sum(s.error_count for s in self.status.values()),
            'total_run_time': sum(s.run_time for s in self.status.values()),
            'sources_by_tier': {},
            'recent_activity': []
        }

        # Count by tier
        for source_name, status in self.status.items():
            source_info = self.registry.get_source(source_name)
            if source_info:
                tier_key = f'tier_{source_info.tier}'
                stats['sources_by_tier'][tier_key] = stats['sources_by_tier'].get(tier_key, 0) + 1

        # Recent activity (last 24 hours)
        now = datetime.now()
        for source_name, status in self.status.items():
            if status.last_run and (now - status.last_run).days < 1:
                stats['recent_activity'].append({
                    'source': source_name,
                    'last_run': status.last_run.isoformat(),
                    'documents': status.total_documents,
                    'success': status.last_result.success if status.last_result else False
                })

        return stats

    def test_all_connections(self) -> Dict[str, bool]:
        """Test connections to all available sources"""
        results = {}

        for source_name in self.status.keys():
            if not self.status[source_name].available:
                continue

            try:
                scraper = self.get_scraper(source_name)
                if scraper:
                    results[source_name] = scraper.test_connection()
                else:
                    results[source_name] = False
            except Exception as e:
                self.logger.error(f"Connection test failed for {source_name}: {e}")
                results[source_name] = False

        return results

    def cleanup(self):
        """Clean up all scraper instances"""
        for scraper in self.scrapers.values():
            try:
                scraper.__exit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error during scraper cleanup: {e}")

        self.scrapers.clear()
        self.logger.info("Plugin manager cleanup completed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Export the class
__all__ = ['PluginManager']