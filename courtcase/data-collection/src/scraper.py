"""
IndianKanoon Scraper Module
Handles web scraping of legal cases from indiankanoon.org
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, quote
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .exceptions import (
    ScraperException,
    NetworkException,
    PDFDownloadException,
    WebDriverException as CustomWebDriverException,
    ParsingException,
    FileOperationException
)
from .constants import (
    DEFAULT_DELAY_SECONDS,
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY_MULTIPLIER,
    REQUEST_TIMEOUT_SECONDS,
    PDF_DOWNLOAD_TIMEOUT_SECONDS,
    MIN_PDF_SIZE_BYTES,
    PDF_HEADER_SIGNATURE,
    PDF_HEADER_READ_BYTES,
    DOWNLOAD_CHUNK_SIZE,
    DEFAULT_MAX_PAGES,
)

logger = logging.getLogger(__name__)


class IndianKanoonScraper:
    """Scraper for IndianKanoon.org legal database."""

    def __init__(self, base_url: str = "https://indiankanoon.org", headless: bool = True, delay: int = DEFAULT_DELAY_SECONDS, proxy: Optional[Dict[str, str]] = None):
        """
        Initialize the scraper.

        Args:
            base_url: Base URL of IndianKanoon
            headless: Run browser in headless mode
            delay: Delay between requests (seconds)
            proxy: Proxy dictionary {"http": "...", "https": "..."} for requests
        """
        self.base_url = base_url
        self.delay = delay
        self.proxy = proxy
        self.session = requests.Session()

        # Configure proxy for requests session
        if proxy:
            self.session.proxies.update(proxy)
            logger.debug(f"Proxy configured for requests session")

        # Comprehensive security headers to protect against tracking and fingerprinting
        self.session.headers.update({
            # User agent and browser identification
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',

            # Security headers
            'DNT': '1',  # Do Not Track
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"'
        })

        # Selenium setup
        self.headless = headless
        self.driver = None

    def init_driver(self) -> None:
        """Initialize Selenium WebDriver with security and privacy settings."""
        if self.driver is None:
            temp_driver = None
            try:
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument("--headless")

                # Security and stability options
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")

                # Privacy and security enhancements
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins-discovery")
                chrome_options.add_argument("--incognito")

                # Performance and resource management
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")
                chrome_options.add_argument("--disable-infobars")

                # Configure proxy for Selenium if provided
                if self.proxy and self.proxy.get("http"):
                    proxy_url = self.proxy.get("http", "").replace("http://", "")
                    chrome_options.add_argument(f"--proxy-server={proxy_url}")
                    logger.debug(f"Proxy configured for Selenium WebDriver")

                # Set preferences for additional security
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_experimental_option("prefs", {
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.default_content_setting_values.media_stream": 2,
                    "profile.default_content_setting_values.geolocation": 2
                })

                service = Service(ChromeDriverManager().install())
                temp_driver = webdriver.Chrome(service=service, options=chrome_options)

                # Remove webdriver property to avoid detection
                temp_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                # Only assign to self.driver after successful initialization
                self.driver = temp_driver
                logger.info("WebDriver initialized with security settings")

            except Exception as e:
                # Clean up temp driver if initialization failed partway through
                if temp_driver:
                    try:
                        temp_driver.quit()
                    except:
                        pass
                raise CustomWebDriverException(
                    "Failed to initialize Chrome WebDriver",
                    driver_type="Chrome",
                    original_exception=e
                )

    def close_driver(self) -> None:
        """Close Selenium WebDriver safely with error handling."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

    def search_cases(self, query: str, year: Optional[int] = None,
                    doc_type: str = "supremecourt", page: int = 0) -> List[Dict[str, Any]]:
        """
        Search for cases on IndianKanoon.

        Args:
            query: Search query
            year: Filter by year
            doc_type: Type of document (supremecourt, highcourt, etc.)
            page: Page number for pagination

        Returns:
            List of case dictionaries with links and metadata
        """
        # Build search URL
        search_params = f"doctypes:{doc_type}"
        if query:
            search_params += f" {query}"
        if year:
            search_params += f" fromdate:1-1-{year} todate:31-12-{year}"

        search_url = f"{self.base_url}/search/?formInput={quote(search_params)}&pagenum={page}"

        logger.info(f"Searching: {search_url}")

        try:
            response = self.session.get(search_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            cases = []

            # Extract case results
            result_divs = soup.find_all('div', class_='result')

            for result in result_divs:
                case = {}

                # Extract title and link
                title_div = result.find('div', class_='result_title')
                if title_div:
                    title_link = title_div.find('a')
                    if title_link:
                        case['title'] = title_link.get_text(strip=True)
                        case['url'] = urljoin(self.base_url, title_link['href'])

                # Extract snippet
                snippet = result.find('div', class_='result_snippet')
                if snippet:
                    case['snippet'] = snippet.get_text(strip=True)

                # Extract citation
                cite_tag = result.find('div', class_='cite')
                if cite_tag:
                    case['citation'] = cite_tag.get_text(strip=True)

                if case:
                    cases.append(case)

            time.sleep(self.delay)
            logger.info(f"Found {len(cases)} cases on page {page}")

            return cases

        except requests.exceptions.Timeout as e:
            raise NetworkException(
                "Search request timed out",
                url=search_url,
                original_exception=e
            )
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
            raise NetworkException(
                "Failed to fetch search results",
                url=search_url,
                status_code=status_code,
                original_exception=e
            )
        except Exception as e:
            raise ParsingException(
                "Failed to parse search results",
                url=search_url,
                original_exception=e
            )

    def get_case_details(self, case_url: str) -> Dict[str, Any]:
        """
        Extract detailed information from a case page.

        Args:
            case_url: URL of the case

        Returns:
            Dictionary with case details
        """
        try:
            response = self.session.get(case_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            case_details = {
                'url': case_url,
                'title': '',
                'citation': '',
                'court': '',
                'date': '',
                'bench': '',
                'author': '',
                'full_text': '',
                'judgement': '',
                'pdf_link': ''
            }

            # Extract title
            title_tag = soup.find('h1', class_='doc_title')
            if title_tag:
                case_details['title'] = title_tag.get_text(strip=True)

            # Extract citation
            pre_tag = soup.find('pre')
            if pre_tag:
                case_details['citation'] = pre_tag.get_text(strip=True)

            # Extract judgment text
            doc_div = soup.find('div', class_='judgments')
            if doc_div:
                case_details['full_text'] = doc_div.get_text(separator='\n', strip=True)

            # Extract PDF link - IndianKanoon uses form submission
            # Look for PDF form with type=pdf input
            pdf_forms = soup.find_all('form', method='POST')
            for form in pdf_forms:
                pdf_input = form.find('input', {'type': 'hidden', 'name': 'type', 'value': 'pdf'})
                if pdf_input:
                    # Found PDF form - store the case URL for later POST request
                    case_details['pdf_link'] = case_url
                    logger.debug(f"Found PDF form for case: {case_url}")
                    break

            # Also check for direct PDF link (some cases may have it)
            if not case_details['pdf_link']:
                pdf_link = soup.find('a', string='Download PDF')
                if pdf_link:
                    case_details['pdf_link'] = urljoin(self.base_url, pdf_link['href'])

            # Extract metadata
            tags = soup.find_all('a', href=True)
            for tag in tags:
                text = tag.get_text(strip=True)
                if 'Supreme Court' in text or 'High Court' in text:
                    case_details['court'] = text
                    break

            time.sleep(self.delay)
            logger.info(f"Extracted details for: {case_details['title'][:50]}...")

            return case_details

        except requests.exceptions.Timeout as e:
            raise NetworkException(
                "Request timed out while fetching case details",
                url=case_url,
                original_exception=e
            )
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
            raise NetworkException(
                "Failed to fetch case details",
                url=case_url,
                status_code=status_code,
                original_exception=e
            )
        except Exception as e:
            raise ParsingException(
                "Failed to parse case details",
                url=case_url,
                original_exception=e
            )

    def download_pdf(self, pdf_url: str, output_path: str) -> bool:
        """
        Download PDF document.

        Args:
            pdf_url: URL of the PDF
            output_path: Path to save the PDF

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(pdf_url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    f.write(chunk)

            logger.info(f"Downloaded PDF to: {output_path}")
            time.sleep(self.delay)
            return True

        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return False

    def download_indiankanoon_pdf(self, case_url: str, output_path: str, max_retries: int = MAX_RETRY_ATTEMPTS) -> bool:
        """
        Download PDF from IndianKanoon using form submission with retry logic.

        IndianKanoon generates PDFs via POST request with type=pdf parameter.

        Args:
            case_url: URL of the case page
            output_path: Path to save the PDF
            max_retries: Maximum number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        import os

        for attempt in range(max_retries):
            try:
                # Extract doc ID from URL
                # URL formats:
                # - https://indiankanoon.org/doc/195337301/
                # - https://indiankanoon.org/docfragment/195337301/?formInput=...

                # Clean URL to get base doc URL
                if '/docfragment/' in case_url:
                    # Extract doc ID and convert to /doc/ format
                    doc_id = case_url.split('/docfragment/')[1].split('/')[0].split('?')[0]
                    post_url = f"{self.base_url}/doc/{doc_id}/"
                elif '/doc/' in case_url:
                    # Already in correct format, remove query params
                    post_url = case_url.split('?')[0]
                else:
                    logger.error(f"Invalid IndianKanoon URL format: {case_url}")
                    return False

                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} for: {post_url}")
                else:
                    logger.info(f"Requesting PDF from: {post_url}")

                # Submit POST request with type=pdf to generate PDF
                response = self.session.post(
                    post_url,
                    data={'type': 'pdf'},
                    stream=True,
                    timeout=PDF_DOWNLOAD_TIMEOUT_SECONDS
                )
                response.raise_for_status()

                # Check if response is actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                    logger.warning(f"Response may not be a PDF. Content-Type: {content_type}")
                    # Continue anyway, sometimes servers send wrong content-type

                # Save PDF to file
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)

                # Verify file was written and has content
                file_size = os.path.getsize(output_path)
                if file_size == 0:
                    logger.error(f"Downloaded file is empty")
                    if os.path.exists(output_path):
                        os.remove(output_path)

                    # Retry if not last attempt
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying due to empty file...")
                        time.sleep(self.delay * 2)  # Double delay before retry
                        continue
                    return False

                # Verify it's a valid PDF by checking header
                with open(output_path, 'rb') as f:
                    header = f.read(PDF_HEADER_READ_BYTES)
                    if header != PDF_HEADER_SIGNATURE:
                        logger.warning(f"File may not be a valid PDF. Header: {header}")
                        if os.path.exists(output_path):
                            os.remove(output_path)

                        # Retry if not last attempt
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying due to invalid PDF header...")
                            time.sleep(self.delay * RETRY_DELAY_MULTIPLIER)
                            continue
                        return False

                logger.info(f"Downloaded IndianKanoon PDF to: {output_path} ({file_size} bytes)")
                time.sleep(self.delay)
                return True

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.delay * 2)
                    continue
                logger.error(f"Failed after {max_retries} timeout attempts")
                return False

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.delay * 2)
                    continue
                logger.error(f"Failed after {max_retries} request attempts")
                return False

            except Exception as e:
                logger.error(f"Unexpected error downloading PDF from {case_url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.delay * 2)
                    continue
                return False

        return False

    def scrape_by_year_range(self, start_year: int, end_year: int,
                            doc_type: str = "supremecourt",
                            max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape cases for a range of years.

        Args:
            start_year: Starting year
            end_year: Ending year
            doc_type: Document type to scrape
            max_pages: Maximum pages to scrape per year

        Returns:
            List of all cases found
        """
        all_cases = []

        for year in range(start_year, end_year + 1):
            logger.info(f"Scraping cases for year: {year}")

            for page in range(max_pages):
                cases = self.search_cases("", year=year, doc_type=doc_type, page=page)

                if not cases:
                    break

                all_cases.extend(cases)
                logger.info(f"Year {year}, Page {page}: Found {len(cases)} cases")

        logger.info(f"Total cases scraped: {len(all_cases)}")
        return all_cases

    def __enter__(self) -> 'IndianKanoonScraper':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> bool:
        """
        Context manager exit with comprehensive cleanup.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            False to propagate any exception that occurred
        """
        try:
            # Close driver resources
            self.close_driver()

            # Close HTTP session
            if hasattr(self, 'session') and self.session:
                try:
                    self.session.close()
                    logger.debug("HTTP session closed")
                except Exception as e:
                    logger.error(f"Error closing HTTP session: {e}")

        except Exception as e:
            logger.error(f"Error during cleanup in __exit__: {e}")

        # Don't suppress any exceptions from the with block
        return False

    def __del__(self) -> None:
        """Destructor to ensure resources are cleaned up."""
        try:
            self.close_driver()
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass  # Silently fail in destructor
