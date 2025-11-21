"""
Base Legal Scraper for Bangladesh Sources
Provides common functionality for all Bangladesh legal data scrapers
"""

import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    success: bool
    count: int
    message: str
    metadata: Optional[Dict[str, Any]] = None
    documents: Optional[List[Dict[str, Any]]] = None


@dataclass
class DocumentInfo:
    """Information about a scraped document"""
    title: str
    url: str
    doc_type: str
    source: str
    date: Optional[str] = None
    content: Optional[str] = None
    pdf_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLegalScraper(ABC):
    """
    Abstract base class for all Bangladesh legal scrapers
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_name = config.get('source_name', self.__class__.__name__)
        self.base_url = config.get('base_url', '')
        self.rate_limit = config.get('rate_limit', 1)  # seconds between requests
        self.session = self._create_session()
        self.headers = config.get('headers', self._get_default_headers())
        self.session.headers.update(self.headers)

        # Statistics tracking
        self.stats = {
            'requests_made': 0,
            'documents_found': 0,
            'documents_downloaded': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

        logger.info(f"Initialized {self.source_name} scraper")

    def _create_session(self) -> requests.Session:
        """Create a requests session with appropriate settings"""
        session = requests.Session()

        # Configure session
        session.timeout = 30
        session.max_redirects = 5

        # Proxy settings if configured
        if self.config.get('proxy'):
            session.proxies.update(self.config.get('proxy'))

        return session

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for requests"""
        return {
            'User-Agent': self.config.get('user_agent',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _rate_limit_delay(self):
        """Implement rate limiting between requests"""
        if self.rate_limit > 0:
            # Add random jitter to avoid detection
            jitter = random.uniform(0.1, 0.3)
            time.sleep(self.rate_limit + jitter)

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Make an HTTP request with error handling and rate limiting"""
        self._rate_limit_delay()

        try:
            self.stats['requests_made'] += 1
            logger.debug(f"Requesting {method} {url}")

            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            return response

        except requests.exceptions.RequestException as e:
            self.stats['errors'] += 1
            logger.error(f"Request failed for {url}: {e}")
            return None

    def _get_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute URL"""
        if url.startswith(('http://', 'https://')):
            return url
        return urljoin(self.base_url, url)

    def _download_pdf(self, pdf_url: str, save_path: str) -> bool:
        """Download a PDF file from the given URL"""
        try:
            response = self._make_request(pdf_url)
            if not response:
                return False

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(response.content)

            self.stats['documents_downloaded'] += 1
            logger.info(f"Downloaded PDF: {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download PDF from {pdf_url}: {e}")
            self.stats['errors'] += 1
            return False

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to standard format (YYYY-MM-DD)"""
        if not date_str:
            return None

        try:
            # Common date formats for Bangladesh legal documents
            date_formats = [
                '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y',
                '%Y %B %d', '%d %B %Y',
                '%d-%b-%Y', '%b %d, %Y'
            ]

            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue

            # If no format matches, return the original string
            return date_str.strip()

        except Exception:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        elapsed = datetime.now() - self.stats['start_time']
        return {
            **self.stats,
            'elapsed_time': str(elapsed),
            'requests_per_minute': (self.stats['requests_made'] / elapsed.total_seconds()) * 60 if elapsed.total_seconds() > 0 else 0
        }

    # Abstract methods that must be implemented by subclasses

    @abstractmethod
    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        """
        Get a list of available documents from the source

        Args:
            **kwargs: Source-specific parameters (e.g., page, limit, filters)

        Returns:
            List of DocumentInfo objects
        """
        pass

    @abstractmethod
    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific document and extract its content

        Args:
            doc_info: Information about the document to scrape

        Returns:
            Dictionary with document data or None if failed
        """
        pass

    @abstractmethod
    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        """
        Search for documents matching a query

        Args:
            query: Search query
            **filters: Additional search filters

        Returns:
            List of matching DocumentInfo objects
        """
        pass

    # Optional helper methods

    def scrape_all(self, **kwargs) -> ScrapingResult:
        """
        Scrape all available documents from the source

        Args:
            **kwargs: Scraping parameters

        Returns:
            ScrapingResult with summary of the operation
        """
        try:
            documents = []

            # Get document list
            doc_list = self.get_document_list(**kwargs)
            logger.info(f"Found {len(doc_list)} documents to scrape")

            # Scrape each document
            for doc_info in doc_list:
                try:
                    doc_data = self.scrape_document(doc_info)
                    if doc_data:
                        documents.append(doc_data)
                        self.stats['documents_found'] += 1
                except Exception as e:
                    logger.error(f"Failed to scrape document {doc_info.url}: {e}")
                    self.stats['errors'] += 1
                    continue

            return ScrapingResult(
                success=True,
                count=len(documents),
                message=f"Successfully scraped {len(documents)} documents from {self.source_name}",
                documents=documents,
                metadata={
                    'source': self.source_name,
                    'stats': self.get_stats()
                }
            )

        except Exception as e:
            logger.error(f"Scraping failed for {self.source_name}: {e}")
            return ScrapingResult(
                success=False,
                count=0,
                message=f"Scraping failed: {str(e)}",
                metadata={'source': self.source_name}
            )

    def test_connection(self) -> bool:
        """Test connection to the source website"""
        try:
            response = self._make_request(self.base_url)
            return response is not None and response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed for {self.source_name}: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.session.close()
        logger.info(f"Closed {self.source_name} scraper session")


class StubScraper(BaseLegalScraper):
    """
    Stub scraper for sources that require authentication or paid access
    """

    def get_document_list(self, **kwargs) -> List[DocumentInfo]:
        logger.warning(f"STUB: {self.source_name} requires authentication/paid access")
        return []

    def scrape_document(self, doc_info: DocumentInfo) -> Optional[Dict[str, Any]]:
        logger.warning(f"STUB: {self.source_name} requires authentication/paid access")
        return None

    def search_documents(self, query: str, **filters) -> List[DocumentInfo]:
        logger.warning(f"STUB: {self.source_name} requires authentication/paid access")
        return []


# Export the classes
__all__ = ['BaseLegalScraper', 'ScrapingResult', 'DocumentInfo', 'StubScraper']