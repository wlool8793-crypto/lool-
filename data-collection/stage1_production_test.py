#!/usr/bin/env python3
"""
Stage 1 Production Test - Real Document Download
Tests Stage 1 configuration with actual IndianKanoon downloads
Measures performance vs baseline and validates quality gates
"""

import os
import sys
import time
import yaml
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import threading

# Import existing scraper
from src.scraper import IndianKanoonScraper
from src.url_classifier import URLClassifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/stage1_production_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DownloadResult:
    """Result of a single document download"""
    url: str
    success: bool
    download_time_ms: int
    method: str  # 'direct_http' or 'selenium'
    pdf_size_bytes: int = 0
    error: Optional[str] = None
    pdf_path: Optional[str] = None

@dataclass
class TestMetrics:
    """Aggregate test metrics"""
    total_documents: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    total_time_seconds: float = 0.0
    total_bytes_downloaded: int = 0
    direct_http_count: int = 0
    selenium_count: int = 0
    avg_download_time_ms: float = 0.0
    docs_per_hour: float = 0.0

    def calculate_derived_metrics(self):
        """Calculate derived metrics"""
        if self.successful_downloads > 0:
            self.avg_download_time_ms = (self.total_time_seconds * 1000) / self.successful_downloads
        if self.total_time_seconds > 0:
            self.docs_per_hour = (self.successful_downloads / self.total_time_seconds) * 3600

class ProductionTestRunner:
    """Runs production test with Stage 1 configuration"""

    def __init__(self, config_path: str = './config/config_stage1_test.yaml'):
        """Initialize test runner"""
        self.config = self._load_config(config_path)
        self.classifier = URLClassifier()
        self.db_path = self._get_db_path()
        self.results: List[DownloadResult] = []
        self.lock = threading.Lock()

        # Thread-local storage for scrapers
        self.thread_local = threading.local()

        # Create output directory
        self.output_dir = Path('data/stage1_test_downloads')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _get_db_path(self) -> str:
        """Extract database path from config"""
        db_url = self.config['database']['url']
        if 'sqlite:///' in db_url:
            return db_url.split('sqlite:///')[-1]
        raise ValueError("Only SQLite databases supported for Stage 1 testing")

    def get_thread_scraper(self) -> IndianKanoonScraper:
        """Get or create thread-local scraper instance"""
        if not hasattr(self.thread_local, 'scraper'):
            delay = self.config['scraper']['delay_between_requests']
            self.thread_local.scraper = IndianKanoonScraper(
                delay=delay,
                headless=True,
                proxy=None  # No proxies for small test
            )
            logger.debug(f"Created scraper for thread {threading.current_thread().name}")
        return self.thread_local.scraper

    def get_test_urls(self, limit: int = 20) -> List[Tuple[int, str]]:
        """
        Get test URLs from database
        Returns: List of (doc_id, url) tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get documents without PDFs
        query = """
            SELECT id, source_url
            FROM universal_legal_documents
            WHERE pdf_downloaded = 0
            AND source_url IS NOT NULL
            AND source_url LIKE '%indiankanoon.org%'
            LIMIT ?
        """

        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()

        logger.info(f"Found {len(results)} test URLs from database")
        return results

    def download_document(self, doc_id: int, url: str) -> DownloadResult:
        """
        Download a single document with URL classification
        """
        start_time = time.time()

        try:
            # Classify URL
            classification, confidence, reason = self.classifier.classify_url(url)

            logger.info(f"[{doc_id}] URL: {url}")
            logger.info(f"[{doc_id}] Classification: {classification} (confidence: {confidence:.2f})")

            scraper = self.get_thread_scraper()

            # Attempt download based on classification
            if classification == 'direct_http':
                # Try direct HTTP download first
                try:
                    pdf_data = self._download_direct_http(scraper, url, doc_id)
                    method = 'direct_http'
                except Exception as e:
                    logger.warning(f"[{doc_id}] Direct HTTP failed: {e}, falling back to Selenium")
                    pdf_data = self._download_with_selenium(scraper, url, doc_id)
                    method = 'selenium_fallback'
            else:
                # Use Selenium for dynamic pages
                pdf_data = self._download_with_selenium(scraper, url, doc_id)
                method = 'selenium'

            # Save PDF
            if pdf_data:
                pdf_path = self.output_dir / f"doc_{doc_id}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_data)

                download_time_ms = int((time.time() - start_time) * 1000)

                logger.info(f"[{doc_id}] ✓ Downloaded {len(pdf_data)} bytes in {download_time_ms}ms via {method}")

                return DownloadResult(
                    url=url,
                    success=True,
                    download_time_ms=download_time_ms,
                    method=method,
                    pdf_size_bytes=len(pdf_data),
                    pdf_path=str(pdf_path)
                )
            else:
                raise Exception("No PDF data returned")

        except Exception as e:
            download_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{doc_id}] ✗ Failed: {e}")

            return DownloadResult(
                url=url,
                success=False,
                download_time_ms=download_time_ms,
                method='failed',
                error=str(e)
            )

    def _download_direct_http(self, scraper: IndianKanoonScraper, url: str, doc_id: int) -> bytes:
        """Download PDF using direct HTTP request"""
        # Look for PDF link on the page
        response = scraper.session.get(url, timeout=30)
        response.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find PDF link
        pdf_link = soup.find('a', href=lambda x: x and '.pdf' in x.lower())
        if not pdf_link:
            # Try to find "Download PDF" button/link
            pdf_link = soup.find('a', string=lambda x: x and 'pdf' in x.lower())

        if pdf_link:
            pdf_url = pdf_link.get('href')
            if not pdf_url.startswith('http'):
                pdf_url = scraper.base_url + pdf_url

            logger.debug(f"[{doc_id}] Downloading PDF from: {pdf_url}")

            pdf_response = scraper.session.get(pdf_url, timeout=60)
            pdf_response.raise_for_status()

            pdf_data = pdf_response.content

            # Validate PDF
            if len(pdf_data) < 1024:
                raise Exception(f"PDF too small: {len(pdf_data)} bytes")

            if not pdf_data.startswith(b'%PDF'):
                raise Exception("Invalid PDF header")

            return pdf_data
        else:
            raise Exception("No PDF link found on page")

    def _download_with_selenium(self, scraper: IndianKanoonScraper, url: str, doc_id: int) -> bytes:
        """Download PDF using Selenium (for JavaScript-heavy pages)"""
        scraper.init_driver()

        # Navigate to page
        scraper.driver.get(url)
        time.sleep(2)  # Wait for JavaScript to load

        # Find and click PDF download button
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        try:
            # Wait for PDF link to be present
            pdf_link = WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "PDF"))
            )

            pdf_url = pdf_link.get_attribute('href')

            # Download PDF using requests (faster than Selenium download)
            pdf_response = scraper.session.get(pdf_url, timeout=60)
            pdf_response.raise_for_status()

            pdf_data = pdf_response.content

            # Validate PDF
            if len(pdf_data) < 1024:
                raise Exception(f"PDF too small: {len(pdf_data)} bytes")

            if not pdf_data.startswith(b'%PDF'):
                raise Exception("Invalid PDF header")

            return pdf_data

        except Exception as e:
            raise Exception(f"Selenium download failed: {e}")

    def run_test(self, num_documents: int = 20, max_workers: int = 10):
        """
        Run production test

        Args:
            num_documents: Number of documents to download
            max_workers: Number of concurrent workers
        """
        logger.info("="*80)
        logger.info("STAGE 1 PRODUCTION TEST - STARTING")
        logger.info("="*80)
        logger.info(f"Configuration: {self.config['database']['url']}")
        logger.info(f"Documents: {num_documents}")
        logger.info(f"Workers: {max_workers}")
        logger.info(f"Output: {self.output_dir}")

        # Get test URLs
        test_urls = self.get_test_urls(num_documents)

        if not test_urls:
            logger.error("No test URLs found in database!")
            return

        logger.info(f"Retrieved {len(test_urls)} URLs for testing")

        # Run downloads
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.download_document, doc_id, url): (doc_id, url)
                for doc_id, url in test_urls
            }

            for future in as_completed(futures):
                result = future.result()
                with self.lock:
                    self.results.append(result)

                # Print progress
                completed = len(self.results)
                logger.info(f"Progress: {completed}/{len(test_urls)} completed")

        total_time = time.time() - start_time

        # Analyze results
        self.analyze_results(total_time)

        # Cleanup
        self.cleanup_scrapers()

    def analyze_results(self, total_time: float):
        """Analyze and print test results"""
        metrics = TestMetrics()
        metrics.total_documents = len(self.results)
        metrics.total_time_seconds = total_time

        for result in self.results:
            if result.success:
                metrics.successful_downloads += 1
                metrics.total_bytes_downloaded += result.pdf_size_bytes

                if 'direct' in result.method:
                    metrics.direct_http_count += 1
                elif 'selenium' in result.method:
                    metrics.selenium_count += 1
            else:
                metrics.failed_downloads += 1

        metrics.calculate_derived_metrics()

        # Print results
        print("\n" + "="*80)
        print("STAGE 1 PRODUCTION TEST - RESULTS")
        print("="*80)

        print(f"\nOverall Performance:")
        print(f"  Total Documents: {metrics.total_documents}")
        print(f"  Successful: {metrics.successful_downloads} ✓")
        print(f"  Failed: {metrics.failed_downloads} ✗")
        print(f"  Success Rate: {(metrics.successful_downloads/metrics.total_documents)*100:.1f}%")

        print(f"\nTiming:")
        print(f"  Total Time: {metrics.total_time_seconds:.2f} seconds")
        print(f"  Avg Time per Doc: {metrics.avg_download_time_ms:.0f} ms")
        print(f"  Throughput: {metrics.docs_per_hour:.1f} docs/hour")

        print(f"\nDownload Methods:")
        print(f"  Direct HTTP: {metrics.direct_http_count} ({(metrics.direct_http_count/metrics.successful_downloads)*100:.1f}%)")
        print(f"  Selenium: {metrics.selenium_count} ({(metrics.selenium_count/metrics.successful_downloads)*100:.1f}%)")

        print(f"\nData Volume:")
        print(f"  Total Downloaded: {metrics.total_bytes_downloaded / (1024*1024):.2f} MB")
        print(f"  Avg PDF Size: {metrics.total_bytes_downloaded / metrics.successful_downloads / 1024:.1f} KB")

        # Baseline comparison
        print(f"\nBaseline Comparison:")
        baseline_docs_per_hour = 500
        improvement = (metrics.docs_per_hour / baseline_docs_per_hour - 1) * 100
        print(f"  Baseline: {baseline_docs_per_hour} docs/hour")
        print(f"  Stage 1: {metrics.docs_per_hour:.1f} docs/hour")
        print(f"  Improvement: {improvement:+.1f}%")

        # Extrapolation
        if metrics.docs_per_hour > 0:
            print(f"\nExtrapolation to 1.4M documents:")
            total_docs = 1_400_000
            hours_needed = total_docs / metrics.docs_per_hour
            days_needed = hours_needed / 24
            print(f"  Time needed: {hours_needed:.0f} hours ({days_needed:.1f} days)")

            baseline_hours = total_docs / baseline_docs_per_hour
            baseline_days = baseline_hours / 24
            time_saved_hours = baseline_hours - hours_needed
            time_saved_days = time_saved_hours / 24
            print(f"  Baseline time: {baseline_hours:.0f} hours ({baseline_days:.1f} days)")
            print(f"  Time saved: {time_saved_hours:.0f} hours ({time_saved_days:.1f} days)")

        print("="*80)

        # Save metrics to file
        self.save_metrics(metrics)

    def save_metrics(self, metrics: TestMetrics):
        """Save metrics to JSON file"""
        import json

        metrics_file = Path('logs') / f"stage1_test_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            'timestamp': datetime.now().isoformat(),
            'configuration': 'stage1_test',
            'metrics': {
                'total_documents': metrics.total_documents,
                'successful_downloads': metrics.successful_downloads,
                'failed_downloads': metrics.failed_downloads,
                'total_time_seconds': metrics.total_time_seconds,
                'total_bytes_downloaded': metrics.total_bytes_downloaded,
                'direct_http_count': metrics.direct_http_count,
                'selenium_count': metrics.selenium_count,
                'avg_download_time_ms': metrics.avg_download_time_ms,
                'docs_per_hour': metrics.docs_per_hour,
            },
            'results': [
                {
                    'url': r.url,
                    'success': r.success,
                    'method': r.method,
                    'download_time_ms': r.download_time_ms,
                    'pdf_size_bytes': r.pdf_size_bytes,
                    'error': r.error
                }
                for r in self.results
            ]
        }

        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Metrics saved to: {metrics_file}")

    def cleanup_scrapers(self):
        """Cleanup all thread-local scrapers"""
        if hasattr(self.thread_local, 'scraper'):
            if self.thread_local.scraper.driver:
                self.thread_local.scraper.close_driver()

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Run Stage 1 production test')
    parser.add_argument('--documents', type=int, default=20,
                       help='Number of documents to download (default: 20)')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of concurrent workers (default: 10)')
    parser.add_argument('--config', type=str, default='./config/config_stage1_test.yaml',
                       help='Configuration file path')

    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    # Run test
    runner = ProductionTestRunner(config_path=args.config)
    runner.run_test(num_documents=args.documents, max_workers=args.workers)

if __name__ == "__main__":
    main()
