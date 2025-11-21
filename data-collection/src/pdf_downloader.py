"""
PDF Downloader Module
Centralized PDF download logic with retry and validation.
Single source of truth for PDF downloading across the application.
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Callable
import requests

logger = logging.getLogger(__name__)


class PDFDownloader:
    """
    Unified PDF downloader with validation and retry logic.
    Handles IndianKanoon-specific PDF downloads via POST requests.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        delay: float = 2.0,
        timeout: int = 90
    ):
        """
        Initialize PDF downloader.

        Args:
            session: Optional requests.Session instance (creates new if None)
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
        """
        self.session = session or self._create_session()
        self.delay = delay
        self.timeout = timeout

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with appropriate headers.

        Returns:
            Configured requests.Session instance
        """
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })
        return session

    def download_indiankanoon_pdf(
        self,
        case_url: str,
        output_path: str,
        max_retries: int = 3,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Download PDF from IndianKanoon using POST request with retry logic.

        IndianKanoon generates PDFs dynamically via POST with type=pdf parameter.

        Args:
            case_url: URL of the case page
            output_path: Path to save the PDF
            max_retries: Maximum number of retry attempts
            progress_callback: Optional callback(current_attempt, max_retries)

        Returns:
            True if successful, False otherwise
        """
        base_url = "https://indiankanoon.org"

        for attempt in range(max_retries):
            try:
                # Extract doc ID and construct POST URL
                post_url = self._construct_post_url(case_url, base_url)
                if not post_url:
                    return False

                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} for: {post_url}")
                else:
                    logger.debug(f"Requesting PDF from: {post_url}")

                # Progress callback
                if progress_callback:
                    progress_callback(attempt + 1, max_retries)

                # Submit POST request to generate PDF
                response = self.session.post(
                    post_url,
                    data={'type': 'pdf'},
                    stream=True,
                    timeout=self.timeout
                )
                response.raise_for_status()

                # Validate content type
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                    logger.warning(f"Response may not be PDF. Content-Type: {content_type}")

                # Save PDF to file
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Verify file was written
                file_size = os.path.getsize(output_path)
                if file_size == 0:
                    logger.error("Downloaded file is empty")
                    self._cleanup_file(output_path)
                    if attempt < max_retries - 1:
                        time.sleep(self.delay * 2)
                        continue
                    return False

                # Validate PDF header
                if not self._validate_pdf_header(output_path):
                    self._cleanup_file(output_path)
                    if attempt < max_retries - 1:
                        time.sleep(self.delay * 2)
                        continue
                    return False

                logger.debug(f"Downloaded PDF: {output_path} ({file_size} bytes)")
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
                logger.error(f"Unexpected error downloading PDF: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.delay * 2)
                    continue
                return False

        return False

    def download_generic_pdf(
        self,
        pdf_url: str,
        output_path: str,
        max_retries: int = 3
    ) -> bool:
        """
        Download PDF from a direct URL with retry logic.

        Args:
            pdf_url: Direct URL to the PDF
            output_path: Path to save the PDF
            max_retries: Maximum number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries}")

                response = self.session.get(pdf_url, stream=True, timeout=self.timeout)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Validate the downloaded file
                file_size = os.path.getsize(output_path)
                if file_size == 0:
                    logger.error("Downloaded file is empty")
                    self._cleanup_file(output_path)
                    if attempt < max_retries - 1:
                        time.sleep(self.delay * 2)
                        continue
                    return False

                if not self._validate_pdf_header(output_path):
                    self._cleanup_file(output_path)
                    if attempt < max_retries - 1:
                        time.sleep(self.delay * 2)
                        continue
                    return False

                logger.debug(f"Downloaded PDF: {output_path} ({file_size} bytes)")
                time.sleep(self.delay)
                return True

            except Exception as e:
                logger.warning(f"Download error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.delay * 2)
                    continue

        return False

    def _construct_post_url(self, case_url: str, base_url: str) -> Optional[str]:
        """
        Construct the POST URL from a case URL.

        Args:
            case_url: Original case URL
            base_url: Base URL of the site

        Returns:
            POST URL or None if invalid format
        """
        try:
            # Handle different URL formats:
            # - https://indiankanoon.org/doc/195337301/
            # - https://indiankanoon.org/docfragment/195337301/?formInput=...

            if '/docfragment/' in case_url:
                # Extract doc ID and convert to /doc/ format
                doc_id = case_url.split('/docfragment/')[1].split('/')[0].split('?')[0]
                return f"{base_url}/doc/{doc_id}/"
            elif '/doc/' in case_url:
                # Already in correct format, remove query params
                return case_url.split('?')[0]
            else:
                logger.error(f"Invalid IndianKanoon URL format: {case_url}")
                return None

        except Exception as e:
            logger.error(f"Error constructing POST URL from {case_url}: {e}")
            return None

    def _validate_pdf_header(self, file_path: str) -> bool:
        """
        Validate that a file is a valid PDF by checking its header.

        Args:
            file_path: Path to the file

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    logger.warning(f"Invalid PDF header: {header}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating PDF header: {e}")
            return False

    def _cleanup_file(self, file_path: str):
        """
        Remove a file if it exists.

        Args:
            file_path: Path to the file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")

    def validate_existing_pdf(self, file_path: str, min_size: int = 1024) -> bool:
        """
        Validate an existing PDF file.

        Args:
            file_path: Path to the PDF file
            min_size: Minimum file size in bytes (default: 1KB)

        Returns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size < min_size:
                logger.warning(f"PDF too small: {file_size} bytes < {min_size} bytes")
                return False

            # Check PDF header
            return self._validate_pdf_header(file_path)

        except Exception as e:
            logger.error(f"Error validating PDF {file_path}: {e}")
            return False

    def close(self):
        """Close the requests session."""
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
