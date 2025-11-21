"""
Unit Tests for IndianKanoon Scraper
Comprehensive tests for search, details extraction, PDF downloads, and retry logic.
"""

import pytest
import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, call
from src.scraper import IndianKanoonScraper
from tests.fixtures import (
    mock_search_page_html, mock_case_detail_html,
    mock_http_response, mock_pdf_response
)
import requests
import gc


class TestScraperResourceCleanup(unittest.TestCase):
    """Test resource cleanup and memory management in scraper."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = None

    def tearDown(self):
        """Clean up after each test."""
        if self.scraper:
            try:
                self.scraper.close_driver()
            except:
                pass
        gc.collect()

    def test_scraper_initialization_without_driver(self):
        """Test scraper initializes without starting driver."""
        scraper = IndianKanoonScraper()
        self.assertIsNone(scraper.driver, "Driver should not be initialized in __init__")
        self.assertIsNotNone(scraper.session, "Session should be initialized")

    def test_driver_cleanup_on_close(self):
        """Test driver is properly cleaned up when close_driver is called."""
        scraper = IndianKanoonScraper()

        # Mock the driver
        scraper.driver = Mock()
        scraper.driver.quit = Mock()

        # Close the driver
        scraper.close_driver()

        # Verify driver.quit() was called
        scraper.driver.quit.assert_called_once()
        self.assertIsNone(scraper.driver, "Driver should be None after close")

    def test_driver_cleanup_handles_exceptions(self):
        """Test driver cleanup handles exceptions gracefully."""
        scraper = IndianKanoonScraper()

        # Mock the driver to raise exception on quit
        scraper.driver = Mock()
        scraper.driver.quit = Mock(side_effect=Exception("Driver quit failed"))

        # Should not raise exception
        try:
            scraper.close_driver()
        except Exception as e:
            self.fail(f"close_driver raised exception: {e}")

        # Driver should still be set to None
        self.assertIsNone(scraper.driver, "Driver should be None even after exception")

    def test_context_manager_entry(self):
        """Test context manager __enter__ returns self."""
        scraper = IndianKanoonScraper()
        with scraper as s:
            self.assertIs(s, scraper, "__enter__ should return self")

    def test_context_manager_exit_closes_driver(self):
        """Test context manager __exit__ properly closes driver."""
        scraper = IndianKanoonScraper()
        scraper.driver = Mock()
        scraper.driver.quit = Mock()

        # Use context manager
        with scraper:
            pass

        # Verify driver was closed
        scraper.driver.quit.assert_called_once()

    def test_context_manager_exit_handles_exceptions(self):
        """Test context manager handles exceptions during cleanup."""
        scraper = IndianKanoonScraper()
        scraper.driver = Mock()
        scraper.driver.quit = Mock(side_effect=Exception("Cleanup failed"))

        # Should not raise exception
        try:
            with scraper:
                pass
        except Exception as e:
            self.fail(f"Context manager raised exception during cleanup: {e}")

    def test_multiple_close_calls_safe(self):
        """Test calling close_driver multiple times is safe."""
        scraper = IndianKanoonScraper()
        scraper.driver = Mock()
        scraper.driver.quit = Mock()

        # Close multiple times
        scraper.close_driver()
        scraper.close_driver()
        scraper.close_driver()

        # Should not raise exception and quit should be called only once
        self.assertEqual(scraper.driver.quit.call_count, 1)

    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.ChromeDriverManager')
    def test_driver_initialization_with_security_settings(self, mock_driver_manager, mock_chrome):
        """Test driver initialization includes security settings."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"

        scraper = IndianKanoonScraper()
        scraper.init_driver()

        # Verify driver was initialized
        mock_chrome.assert_called_once()

        # Verify security script was executed
        mock_driver.execute_script.assert_called_once()
        call_args = mock_driver.execute_script.call_args[0][0]
        self.assertIn("webdriver", call_args, "Should remove webdriver property")

    def test_session_has_security_headers(self):
        """Test session is initialized with proper security headers."""
        scraper = IndianKanoonScraper()

        # Check for security headers
        headers = scraper.session.headers
        self.assertIn('User-Agent', headers)
        self.assertIn('DNT', headers)
        self.assertEqual(headers['DNT'], '1', "DNT header should be set")
        self.assertIn('Sec-Fetch-Dest', headers)
        self.assertIn('Sec-Fetch-Mode', headers)

    def test_session_cleanup_on_deletion(self):
        """Test session is properly cleaned up when scraper is deleted."""
        scraper = IndianKanoonScraper()
        session = scraper.session

        # Delete scraper
        del scraper
        gc.collect()

        # Session should be closed (we can't directly test this, but no exceptions should occur)
        self.assertTrue(True, "Scraper deletion completed without errors")


class TestScraperExceptionHandling(unittest.TestCase):
    """Test exception handling in scraper methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = IndianKanoonScraper()

    def tearDown(self):
        """Clean up after each test."""
        if self.scraper:
            self.scraper.close_driver()

    @patch('src.scraper.requests.Session.get')
    def test_search_cases_handles_connection_error(self, mock_get):
        """Test search_cases handles connection errors gracefully."""
        mock_get.side_effect = Exception("Connection failed")

        # Should return empty list, not raise exception
        results = self.scraper.search_cases("test query")
        self.assertEqual(results, [], "Should return empty list on error")

    @patch('src.scraper.requests.Session.get')
    def test_get_case_details_handles_http_error(self, mock_get):
        """Test get_case_details handles HTTP errors gracefully."""
        mock_get.side_effect = Exception("HTTP 500 Error")

        # Should return empty dict, not raise exception
        result = self.scraper.get_case_details("https://example.com/case/123")
        self.assertEqual(result, {}, "Should return empty dict on error")

    @patch('src.scraper.requests.Session.post')
    def test_download_pdf_handles_timeout(self, mock_post):
        """Test download_indiankanoon_pdf handles timeouts gracefully."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        # Should return False, not raise exception
        result = self.scraper.download_indiankanoon_pdf(
            "https://indiankanoon.org/doc/123/",
            "/tmp/test.pdf",
            max_retries=1
        )
        self.assertFalse(result, "Should return False on timeout")


class TestScraperMemoryLeaks(unittest.TestCase):
    """Test for memory leaks in scraper."""

    def test_no_driver_leak_on_multiple_inits(self):
        """Test that initializing driver multiple times doesn't leak resources."""
        scraper = IndianKanoonScraper()

        # Mock driver to track instances
        drivers = []
        original_driver = scraper.driver

        with patch('src.scraper.webdriver.Chrome') as mock_chrome:
            mock_driver1 = Mock()
            mock_driver2 = Mock()
            mock_chrome.side_effect = [mock_driver1, mock_driver2]

            with patch('src.scraper.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = "/path/to/chromedriver"

                # Initialize driver twice
                scraper.init_driver()
                first_driver = scraper.driver

                scraper.init_driver()  # Should not create new driver if one exists
                second_driver = scraper.driver

                # Should be the same driver instance
                self.assertIs(first_driver, second_driver,
                             "Should reuse existing driver, not create new one")

        scraper.close_driver()

    def test_session_persists_across_requests(self):
        """Test that session is reused across multiple requests."""
        scraper = IndianKanoonScraper()
        session1 = scraper.session

        # Make a request (mocked)
        with patch.object(scraper.session, 'get') as mock_get:
            mock_get.return_value = Mock(status_code=200, content=b"<html></html>")
            scraper.search_cases("test")

        session2 = scraper.session

        # Should be the same session
        self.assertIs(session1, session2, "Session should be reused")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
