"""
Base Legal Scraper - Abstract Base Class
Foundation for all country-specific legal document scrapers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import time
import logging
import requests
from pathlib import Path
from datetime import datetime
import hashlib
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from bs4 import BeautifulSoup


class BaseLegalScraper(ABC):
    """
    Abstract base class for legal document scrapers.

    All country-specific scrapers should inherit from this class
    and implement the abstract methods.
    """

    def __init__(self, config: Dict[str, Any], database):
        """
        Initialize the scraper.

        Args:
            config: Dictionary containing scraper configuration
            database: Database instance for storing documents
        """
        self.config = config
        self.db = database
        self.country = config.get('country')
        self.base_url = config.get('base_url')
        self.logger = self._setup_logger()

        # Scraping settings
        self.request_delay = config.get('request_delay', 2)
        self.use_selenium = config.get('use_selenium', True)
        self.headless = config.get('headless', True)
        self.download_pdfs = config.get('download_pdfs', True)

        # Output directories
        self.pdf_dir = Path(config.get('pdf_dir', f'./data/pdfs/{self.country}'))
        self.html_dir = Path(config.get('html_dir', f'./data/html/{self.country}'))
        self._create_output_dirs()

        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'pdfs_downloaded': 0,
            'start_time': None
        }

        # Selenium driver (lazy initialization)
        self._driver = None

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the scraper"""
        logger = logging.getLogger(f'{self.__class__.__name__}')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _create_output_dirs(self):
        """Create output directories if they don't exist"""
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.html_dir.mkdir(parents=True, exist_ok=True)

    @property
    def driver(self) -> webdriver.Chrome:
        """Lazy initialization of Selenium WebDriver"""
        if self._driver is None and self.use_selenium:
            self._driver = self._init_selenium_driver()
        return self._driver

    def _init_selenium_driver(self) -> webdriver.Chrome:
        """Initialize Selenium WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver

    # ========================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ========================================================================

    @abstractmethod
    def get_document_list(self) -> List[str]:
        """
        Get list of all document URLs to scrape.

        Returns:
            List of URLs to scrape
        """
        pass

    @abstractmethod
    def parse_document(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single document page and extract all relevant information.

        Args:
            url: URL of the document to parse

        Returns:
            Dictionary containing document data, or None if parsing failed
        """
        pass

    @abstractmethod
    def extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract country-specific metadata from HTML.

        Args:
            html: HTML content of the page
            url: URL of the page

        Returns:
            Dictionary of metadata key-value pairs
        """
        pass

    # ========================================================================
    # SHARED UTILITY METHODS - Available to all subclasses
    # ========================================================================

    def fetch_page(self, url: str, use_selenium: bool = None) -> Optional[str]:
        """
        Fetch HTML content of a page.

        Args:
            url: URL to fetch
            use_selenium: Override default selenium usage

        Returns:
            HTML content or None if failed
        """
        if use_selenium is None:
            use_selenium = self.use_selenium

        try:
            if use_selenium:
                return self._fetch_with_selenium(url)
            else:
                return self._fetch_with_requests(url)
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _fetch_with_selenium(self, url: str) -> str:
        """Fetch page using Selenium"""
        self.driver.get(url)
        time.sleep(2)  # Wait for JavaScript to load
        return self.driver.page_source

    def _fetch_with_requests(self, url: str) -> str:
        """Fetch page using requests library"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text

    def extract_pdf_url(self, html: str, base_url: str) -> Optional[str]:
        """
        Extract PDF download URL from HTML.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            Absolute PDF URL or None
        """
        soup = BeautifulSoup(html, 'lxml')

        # Look for common PDF link patterns
        pdf_patterns = [
            {'name': 'a', 'href': lambda x: x and x.endswith('.pdf')},
            {'name': 'a', 'text': lambda x: x and 'pdf' in x.lower()},
            {'class': lambda x: x and 'pdf' in str(x).lower()}
        ]

        for pattern in pdf_patterns:
            link = soup.find(**pattern)
            if link and link.get('href'):
                pdf_url = urljoin(base_url, link['href'])
                return pdf_url

        return None

    def download_pdf(self, pdf_url: str, doc_id: int) -> Optional[str]:
        """
        Download a PDF file.

        Args:
            pdf_url: URL of PDF to download
            doc_id: Document ID for filename

        Returns:
            Local file path or None if failed
        """
        if not self.download_pdfs:
            return None

        try:
            # Generate filename
            pdf_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:8]
            filename = f"{self.country}_{doc_id}_{pdf_hash}.pdf"
            filepath = self.pdf_dir / filename

            # Skip if already exists
            if filepath.exists():
                self.logger.info(f"PDF already exists: {filename}")
                return str(filepath)

            # Download
            self.logger.info(f"Downloading PDF: {pdf_url}")
            response = requests.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()

            # Save to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.stats['pdfs_downloaded'] += 1
            self.logger.info(f"PDF downloaded: {filename}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Failed to download PDF from {pdf_url}: {e}")
            return None

    def save_html(self, html: str, doc_id: int) -> Optional[str]:
        """
        Save HTML content to file.

        Args:
            html: HTML content
            doc_id: Document ID for filename

        Returns:
            Local file path or None if failed
        """
        try:
            filename = f"{self.country}_{doc_id}.html"
            filepath = self.html_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            return str(filepath)
        except Exception as e:
            self.logger.error(f"Failed to save HTML for doc {doc_id}: {e}")
            return None

    def save_document(self, doc_data: Dict[str, Any]) -> Optional[int]:
        """
        Save document to database.

        Args:
            doc_data: Dictionary containing document information

        Returns:
            Document ID if successful, None otherwise
        """
        try:
            doc_data['country'] = self.country
            doc_data['scraped_at'] = datetime.now().isoformat()

            doc_id = self.db.save_legal_document(doc_data)
            self.stats['successful'] += 1
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to save document: {e}")
            self.stats['failed'] += 1
            return None

    def rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(self.request_delay)

    # ========================================================================
    # MAIN SCRAPING WORKFLOW
    # ========================================================================

    def scrape_all(self, resume: bool = False):
        """
        Main scraping workflow - scrapes all documents.

        Args:
            resume: Whether to resume from previous scraping session
        """
        self.logger.info(f"Starting {self.country} legal document scraper")
        self.logger.info(f"Configuration: {self.config}")

        self.stats['start_time'] = datetime.now()

        try:
            # Get list of URLs to scrape
            self.logger.info("Getting document list...")
            urls = self.get_document_list()
            self.logger.info(f"Found {len(urls)} documents to scrape")

            # Filter out already scraped URLs if resuming
            if resume:
                urls = self._filter_scraped_urls(urls)
                self.logger.info(f"Resuming: {len(urls)} documents remaining")

            # Scrape each document
            for i, url in enumerate(urls, 1):
                self.logger.info(f"Processing {i}/{len(urls)}: {url}")

                try:
                    # Parse document
                    doc_data = self.parse_document(url)

                    if doc_data:
                        # Save to database and get document ID
                        doc_id = self.save_document(doc_data)

                        # Download PDF if available
                        if doc_id and doc_data.get('pdf_url') and self.download_pdfs:
                            pdf_path = self.download_pdf(
                                doc_data['pdf_url'],
                                doc_id
                            )
                            if pdf_path:
                                self.db.update_pdf_path(doc_id, pdf_path)

                    self.stats['total_processed'] += 1

                except Exception as e:
                    self.logger.error(f"Error processing {url}: {e}")
                    self.stats['failed'] += 1

                # Rate limiting
                self.rate_limit()

                # Progress update every 10 documents
                if i % 10 == 0:
                    self._print_progress()

            self._print_final_stats()

        except KeyboardInterrupt:
            self.logger.warning("Scraping interrupted by user")
            self._print_final_stats()
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
        finally:
            self.cleanup()

    def _filter_scraped_urls(self, urls: List[str]) -> List[str]:
        """Filter out URLs that have already been scraped"""
        scraped_urls = self.db.get_scraped_urls(self.country)
        return [url for url in urls if url not in scraped_urls]

    def _print_progress(self):
        """Print current progress statistics"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        rate = self.stats['total_processed'] / elapsed if elapsed > 0 else 0

        self.logger.info(
            f"Progress: {self.stats['successful']} successful, "
            f"{self.stats['failed']} failed, "
            f"{self.stats['pdfs_downloaded']} PDFs, "
            f"Rate: {rate:.2f} docs/sec"
        )

    def _print_final_stats(self):
        """Print final scraping statistics"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()

        self.logger.info("=" * 70)
        self.logger.info("SCRAPING COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info(f"Total processed: {self.stats['total_processed']}")
        self.logger.info(f"Successful: {self.stats['successful']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"PDFs downloaded: {self.stats['pdfs_downloaded']}")
        self.logger.info(f"Time elapsed: {elapsed/60:.1f} minutes")
        self.logger.info("=" * 70)

    def cleanup(self):
        """Cleanup resources"""
        if self._driver:
            try:
                self._driver.quit()
                self._driver = None
                self.logger.info("Selenium driver closed")
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
