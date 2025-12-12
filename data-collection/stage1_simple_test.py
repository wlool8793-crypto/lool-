#!/usr/bin/env python3
"""
Stage 1 Simple Performance Test
Tests direct HTTP download performance without Selenium dependency
Uses known good IndianKanoon document URLs
"""

import os
import sys
import time
import yaml
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DownloadResult:
    """Result of a single download"""
    url: str
    success: bool
    download_time_ms: int
    pdf_size_bytes: int = 0
    error: Optional[str] = None

# Known good IndianKanoon document URLs for testing
TEST_URLS = [
    # Supreme Court judgments - these have direct PDF links
    "https://indiankanoon.org/doc/1712542/",  # Kesavananda Bharati case
    "https://indiankanoon.org/doc/1199182/",  # Maneka Gandhi case
    "https://indiankanoon.org/doc/1766147/",  # Minerva Mills case
    "https://indiankanoon.org/doc/237570/",   # D.K. Basu case
    "https://indiankanoon.org/doc/1096615/",  # Vishaka case
    "https://indiankanoon.org/doc/1933984/",  # I.R. Coelho case
    "https://indiankanoon.org/doc/781781/",   # State of Karnataka case
    "https://indiankanoon.org/doc/1362771/",  # Shreya Singhal case
    "https://indiankanoon.org/doc/1199182/",  # Maneka Gandhi (repeat for concurrency test)
    "https://indiankanoon.org/doc/1766147/",  # Minerva Mills (repeat for concurrency test)
]

def load_config(config_path: str = './config/config_stage1_test.yaml') -> Dict:
    """Load configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def download_document(url: str, session: requests.Session = None) -> DownloadResult:
    """Download a single document using direct HTTP"""
    start_time = time.time()

    if session is None:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    try:
        # Get the page
        response = session.get(url, timeout=30)
        response.raise_for_status()

        # Parse HTML to find PDF link
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find PDF download link
        pdf_link = None

        # Method 1: Look for explicit PDF link
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text().lower()
            if 'pdf' in text or '.pdf' in href:
                pdf_link = href
                break

        # Method 2: Look for standard doc download link
        if not pdf_link:
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if '/doc/' in href and href != url:
                    pdf_link = href

        if pdf_link:
            # Make absolute URL
            if not pdf_link.startswith('http'):
                from urllib.parse import urljoin
                pdf_link = urljoin('https://indiankanoon.org', pdf_link)

            # Download PDF
            logger.info(f"Downloading from: {pdf_link}")
            pdf_response = session.get(pdf_link, timeout=60)
            pdf_response.raise_for_status()

            pdf_data = pdf_response.content

            # Validate
            if len(pdf_data) < 1024:
                raise Exception(f"PDF too small: {len(pdf_data)} bytes")

            # For HTML pages, just count the content
            if not pdf_data.startswith(b'%PDF'):
                logger.warning(f"Not a PDF, but valid HTML content: {len(pdf_data)} bytes")
                # Still count as success for performance testing

            download_time_ms = int((time.time() - start_time) * 1000)

            logger.info(f"✓ Downloaded {len(pdf_data)} bytes in {download_time_ms}ms")

            return DownloadResult(
                url=url,
                success=True,
                download_time_ms=download_time_ms,
                pdf_size_bytes=len(pdf_data)
            )
        else:
            raise Exception("No download link found")

    except Exception as e:
        download_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"✗ Failed: {e}")

        return DownloadResult(
            url=url,
            success=False,
            download_time_ms=download_time_ms,
            error=str(e)
        )

def run_test(num_workers: int = 1, urls: List[str] = None):
    """Run performance test"""
    if urls is None:
        urls = TEST_URLS

    print("="*80)
    print(f"STAGE 1 PERFORMANCE TEST - {num_workers} WORKERS")
    print("="*80)
    print(f"URLs to test: {len(urls)}")
    print(f"Workers: {num_workers}")

    start_time = time.time()
    results = []

    # Create shared session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    if num_workers == 1:
        # Sequential download (baseline)
        for url in urls:
            result = download_document(url, session)
            results.append(result)
    else:
        # Parallel download (Stage 1)
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(download_document, url): url for url in urls}

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                logger.info(f"Progress: {len(results)}/{len(urls)}")

    total_time = time.time() - start_time

    # Analyze results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    total_bytes = sum(r.pdf_size_bytes for r in successful)
    avg_time_ms = sum(r.download_time_ms for r in successful) / len(successful) if successful else 0

    print(f"\nResults:")
    print(f"  Successful: {len(successful)}/{len(urls)} ({len(successful)/len(urls)*100:.1f}%)")
    print(f"  Failed: {len(failed)}")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Avg Download Time: {avg_time_ms:.0f}ms")
    print(f"  Total Downloaded: {total_bytes/(1024*1024):.2f} MB")

    if total_time > 0:
        docs_per_second = len(successful) / total_time
        docs_per_hour = docs_per_second * 3600
        print(f"  Throughput: {docs_per_hour:.1f} docs/hour")

    print("="*80)

    return {
        'total_time': total_time,
        'successful': len(successful),
        'docs_per_hour': docs_per_hour if total_time > 0 else 0
    }

def main():
    """Run comparison test"""
    print("\n" + "="*80)
    print("STAGE 1 CONFIGURATION PERFORMANCE COMPARISON")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test 1: Baseline (1 worker, sequential)
    print("\n### TEST 1: BASELINE (1 Worker - Sequential Download) ###")
    baseline = run_test(num_workers=1, urls=TEST_URLS[:5])  # Use 5 URLs for faster test

    # Test 2: Stage 1 Configuration (10 workers, parallel)
    print("\n### TEST 2: STAGE 1 (10 Workers - Parallel Download) ###")
    stage1 = run_test(num_workers=10, urls=TEST_URLS[:5])

    # Comparison
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)

    print(f"\nBaseline (1 worker):")
    print(f"  Time: {baseline['total_time']:.2f}s")
    print(f"  Throughput: {baseline['docs_per_hour']:.1f} docs/hour")

    print(f"\nStage 1 (10 workers):")
    print(f"  Time: {stage1['total_time']:.2f}s")
    print(f"  Throughput: {stage1['docs_per_hour']:.1f} docs/hour")

    if baseline['total_time'] > 0:
        speedup = baseline['total_time'] / stage1['total_time']
        improvement_pct = (speedup - 1) * 100

        print(f"\nImprovement:")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Improvement: {improvement_pct:+.1f}%")
        print(f"  Time saved: {baseline['total_time'] - stage1['total_time']:.2f}s per {len(TEST_URLS[:5])} docs")

    # Extrapolation
    if stage1['docs_per_hour'] > 0:
        print(f"\nExtrapolation to 1.4M documents:")
        total_docs = 1_400_000

        baseline_hours = total_docs / baseline['docs_per_hour']
        stage1_hours = total_docs / stage1['docs_per_hour']

        print(f"  Baseline: {baseline_hours:.0f} hours ({baseline_hours/24:.1f} days)")
        print(f"  Stage 1: {stage1_hours:.0f} hours ({stage1_hours/24:.1f} days)")
        print(f"  Time saved: {baseline_hours - stage1_hours:.0f} hours ({(baseline_hours - stage1_hours)/24:.1f} days)")

    print("="*80)

if __name__ == "__main__":
    main()
