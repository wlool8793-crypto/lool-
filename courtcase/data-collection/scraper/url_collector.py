"""
URL Collector Module
Collects all document URLs from IndianKanoon.org using Selenium pagination
"""

import json
import logging
import time
from typing import List, Dict, Set, Optional
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class URLCollector:
    """Collects document URLs from IndianKanoon.org with checkpoint support."""

    def __init__(self, config: Dict, checkpoint_file: str = "./data/document_urls.json"):
        """
        Initialize URL collector.

        Args:
            config: Configuration dictionary
            checkpoint_file: Path to save collected URLs
        """
        self.config = config
        self.checkpoint_file = Path(checkpoint_file)
        self.base_url = "https://indiankanoon.org"

        # URL collection settings
        self.search_url = config.get('url_collection', {}).get(
            'base_search_url',
            'https://indiankanoon.org/search/?formInput=doctype:%20judgments'
        )
        self.max_pages = config.get('url_collection', {}).get('max_pages', None)
        self.checkpoint_every = config.get('url_collection', {}).get('checkpoint_every', 10000)
        self.page_load_timeout = config.get('scraper', {}).get('timeout', 30)

        # Storage for collected URLs
        self.collected_urls: Set[str] = set()
        self.url_metadata: List[Dict] = []

        # Selenium driver
        self.driver: Optional[webdriver.Chrome] = None

        # Statistics
        self.stats = {
            'pages_processed': 0,
            'urls_collected': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }

    def init_driver(self):
        """Initialize Selenium WebDriver with optimized settings."""
        if self.driver is None:
            chrome_options = Options()

            # Headless mode
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            # Window size
            chrome_options.add_argument("--window-size=1920,1080")

            # User agent
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            # Remove automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Performance optimization
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-images")  # Don't load images
            chrome_options.page_load_strategy = 'eager'  # Don't wait for full load

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Remove webdriver property
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
            )

            self.driver.set_page_load_timeout(self.page_load_timeout)
            logger.info("✓ Selenium WebDriver initialized for URL collection")

    def close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("✓ WebDriver closed")

    def load_checkpoint(self) -> bool:
        """
        Load previously collected URLs from checkpoint file.

        Returns:
            True if checkpoint loaded, False otherwise
        """
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    self.collected_urls = set(data.get('urls', []))
                    self.url_metadata = data.get('metadata', [])
                    self.stats = data.get('stats', self.stats)
                    logger.info(f"✓ Loaded {len(self.collected_urls)} URLs from checkpoint")
                    return True
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
                return False
        return False

    def save_checkpoint(self):
        """Save collected URLs to checkpoint file."""
        try:
            data = {
                'urls': list(self.collected_urls),
                'metadata': self.url_metadata,
                'stats': self.stats,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # Save to temporary file first
            temp_file = self.checkpoint_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic rename
            temp_file.replace(self.checkpoint_file)

            logger.info(f"✓ Checkpoint saved: {len(self.collected_urls)} URLs")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def extract_urls_from_page(self, page_source: str) -> List[Dict]:
        """
        Extract document URLs from search results page.

        Args:
            page_source: HTML source of the page

        Returns:
            List of dictionaries with URL and metadata
        """
        soup = BeautifulSoup(page_source, 'html.parser')
        results = []

        # Find all result divs
        result_divs = soup.find_all('div', class_='result')

        for result_div in result_divs:
            try:
                # Extract title and URL
                title_div = result_div.find('div', class_='result_title')
                if not title_div:
                    continue

                title_link = title_div.find('a')
                if not title_link or 'href' not in title_link.attrs:
                    continue

                url = title_link['href']

                # Convert to absolute URL
                if url.startswith('/'):
                    url = self.base_url + url

                # Extract doc ID from URL
                # Format: /doc/123456/ or /doc/123456
                if '/doc/' not in url:
                    continue

                doc_id = url.split('/doc/')[1].strip('/').split('/')[0].split('?')[0]

                # Skip if already collected
                if url in self.collected_urls:
                    self.stats['duplicates_skipped'] += 1
                    continue

                # Extract metadata
                title = title_link.get_text(strip=True)

                # Extract citation
                citation = ""
                cite_div = result_div.find('div', class_='cite')
                if cite_div:
                    citation = cite_div.get_text(strip=True)

                # Extract court info from citation or title
                court = ""
                if "Supreme Court" in citation or "Supreme Court" in title:
                    court = "Supreme Court"
                elif "High Court" in citation or "High Court" in title:
                    court = "High Court"

                # Add to results
                result_data = {
                    'url': url,
                    'doc_id': doc_id,
                    'title': title,
                    'citation': citation,
                    'court': court
                }

                results.append(result_data)
                self.collected_urls.add(url)

            except Exception as e:
                logger.warning(f"Error extracting URL from result: {e}")
                continue

        return results

    def has_next_page(self) -> bool:
        """
        Check if there's a next page button.

        Returns:
            True if next page exists, False otherwise
        """
        try:
            # Look for "Next" link or pagination
            next_link = self.driver.find_element(By.LINK_TEXT, "Next")
            return next_link.is_displayed() and next_link.is_enabled()
        except NoSuchElementException:
            return False

    def click_next_page(self) -> bool:
        """
        Click the next page button.

        Returns:
            True if successful, False otherwise
        """
        try:
            next_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
            )
            next_link.click()

            # Wait for page to load
            time.sleep(2)

            # Wait for results to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Could not click next page: {e}")
            return False

    def collect_urls(self, start_page: int = 0) -> Dict:
        """
        Collect all document URLs from IndianKanoon.

        Args:
            start_page: Page number to start from (for resume)

        Returns:
            Dictionary with collection statistics
        """
        logger.info("=" * 70)
        logger.info("Starting URL Collection")
        logger.info("=" * 70)

        # Load checkpoint if exists
        self.load_checkpoint()

        # Initialize driver
        self.init_driver()

        try:
            # Navigate to search page
            if start_page == 0:
                logger.info(f"Loading search page: {self.search_url}")
                self.driver.get(self.search_url)
            else:
                # Construct URL with page number
                url_with_page = f"{self.search_url}&pagenum={start_page}"
                logger.info(f"Resuming from page {start_page}: {url_with_page}")
                self.driver.get(url_with_page)

            time.sleep(3)  # Initial load delay

            current_page = start_page
            consecutive_errors = 0
            max_consecutive_errors = 5

            while True:
                # Check page limit
                if self.max_pages is not None and current_page >= self.max_pages:
                    logger.info(f"Reached max pages limit: {self.max_pages}")
                    break

                try:
                    logger.info(f"\nProcessing page {current_page}...")

                    # Extract URLs from current page
                    page_source = self.driver.page_source
                    page_results = self.extract_urls_from_page(page_source)

                    # Update metadata
                    self.url_metadata.extend(page_results)

                    # Update statistics
                    self.stats['pages_processed'] = current_page + 1
                    self.stats['urls_collected'] = len(self.collected_urls)

                    logger.info(
                        f"  → Found {len(page_results)} new URLs "
                        f"(Total: {self.stats['urls_collected']}, "
                        f"Duplicates: {self.stats['duplicates_skipped']})"
                    )

                    # Save checkpoint periodically
                    if len(self.collected_urls) % self.checkpoint_every < len(page_results):
                        self.save_checkpoint()

                    # Check if there's a next page
                    if not self.has_next_page():
                        logger.info("No more pages found. Collection complete!")
                        break

                    # Click next page
                    if not self.click_next_page():
                        logger.warning("Failed to navigate to next page")
                        break

                    current_page += 1
                    consecutive_errors = 0

                    # Polite delay
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Error on page {current_page}: {e}")
                    self.stats['errors'] += 1
                    consecutive_errors += 1

                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                        break

                    time.sleep(5)  # Longer delay after error
                    continue

            # Final checkpoint
            self.save_checkpoint()

            # Print summary
            logger.info("\n" + "=" * 70)
            logger.info("URL Collection Complete")
            logger.info("=" * 70)
            logger.info(f"Pages processed: {self.stats['pages_processed']}")
            logger.info(f"URLs collected: {self.stats['urls_collected']}")
            logger.info(f"Duplicates skipped: {self.stats['duplicates_skipped']}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info(f"Checkpoint saved to: {self.checkpoint_file}")
            logger.info("=" * 70)

            return self.stats

        finally:
            self.close_driver()

    def get_collected_urls(self) -> List[str]:
        """
        Get list of collected URLs.

        Returns:
            List of URL strings
        """
        return list(self.collected_urls)

    def get_url_metadata(self) -> List[Dict]:
        """
        Get list of URL metadata.

        Returns:
            List of dictionaries with URL metadata
        """
        return self.url_metadata

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_driver()
