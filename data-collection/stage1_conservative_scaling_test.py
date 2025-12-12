#!/usr/bin/env python3
"""
Stage 1 Conservative Scaling Test
Tests performance with rate limiting and delays to avoid server blocks
"""

import sys
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Result of a scaling test"""
    workers: int
    total_time: float
    successful: int
    failed: int
    total_bytes: int
    docs_per_hour: float
    speedup: float
    efficiency: float

# Smaller test set for conservative testing
TEST_URLS = [
    "https://indiankanoon.org/doc/1712542/",
    "https://indiankanoon.org/doc/1199182/",
    "https://indiankanoon.org/doc/1766147/",
    "https://indiankanoon.org/doc/237570/",
    "https://indiankanoon.org/doc/1096615/",
    "https://indiankanoon.org/doc/1933984/",
    "https://indiankanoon.org/doc/781781/",
    "https://indiankanoon.org/doc/1362771/",
    "https://indiankanoon.org/doc/367586/",
    "https://indiankanoon.org/doc/1199182/",
]

# Rate limiting
rate_limiter = threading.Semaphore(10)  # Max 10 concurrent requests
request_delay = 0.1  # 100ms between requests

def download_document(url: str, delay: float = 0.0) -> Dict:
    """Download a single document with rate limiting"""

    # Rate limiting
    with rate_limiter:
        if delay > 0:
            time.sleep(delay)

        start_time = time.time()

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find download link
            pdf_link = None
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text().lower()
                if 'pdf' in text or '.pdf' in href or ('/doc/' in href and href != url):
                    pdf_link = href
                    break

            if pdf_link:
                if not pdf_link.startswith('http'):
                    from urllib.parse import urljoin
                    pdf_link = urljoin('https://indiankanoon.org', pdf_link)

                pdf_response = session.get(pdf_link, timeout=60)
                pdf_response.raise_for_status()
                content = pdf_response.content
            else:
                content = response.content

            download_time_ms = int((time.time() - start_time) * 1000)

            return {
                'success': True,
                'size': len(content),
                'time_ms': download_time_ms
            }

        except Exception as e:
            logger.debug(f"Download failed: {e}")
            return {
                'success': False,
                'size': 0,
                'time_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }

def run_test(num_workers: int, urls: List[str], delay: float = 0.0) -> TestResult:
    """Run test with specified number of workers"""
    logger.info(f"{'='*80}")
    logger.info(f"Testing with {num_workers} workers (delay: {delay}s)...")
    logger.info(f"{'='*80}")

    start_time = time.time()
    results = []

    if num_workers == 1:
        # Sequential
        for i, url in enumerate(urls, 1):
            result = download_document(url, delay)
            results.append(result)
            if i % 5 == 0 or i == len(urls):
                logger.info(f"  Progress: {i}/{len(urls)} documents")
    else:
        # Parallel with rate limiting
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(download_document, url, delay): url for url in urls}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)
                if i % 5 == 0 or i == len(urls):
                    logger.info(f"  Progress: {i}/{len(urls)} documents")

    total_time = time.time() - start_time

    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_bytes = sum(r['size'] for r in successful)

    docs_per_hour = (len(successful) / total_time) * 3600 if total_time > 0 else 0

    logger.info(f"")
    logger.info(f"  Completed in {total_time:.2f}s")
    logger.info(f"  Successful: {len(successful)}/{len(urls)} ({len(successful)/len(urls)*100:.1f}%)")
    logger.info(f"  Failed: {len(failed)}")
    logger.info(f"  Throughput: {docs_per_hour:.1f} docs/hour")
    logger.info(f"  Total data: {total_bytes/(1024*1024):.2f} MB")

    return TestResult(
        workers=num_workers,
        total_time=total_time,
        successful=len(successful),
        failed=len(failed),
        total_bytes=total_bytes,
        docs_per_hour=docs_per_hour,
        speedup=0.0,
        efficiency=0.0
    )

def main():
    """Run conservative scaling tests"""
    print("\n" + "="*80)
    print("STAGE 1 CONSERVATIVE SCALING TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total URLs: {len(TEST_URLS)}")
    print(f"Worker counts to test: 1, 5, 10, 20, 50")
    print(f"Rate limiting: Max 10 concurrent, 100ms delay")
    print("="*80 + "\n")

    # Run tests with different worker counts
    worker_configs = [
        (1, 0.5),    # 1 worker, 500ms delay (baseline)
        (5, 0.2),    # 5 workers, 200ms delay
        (10, 0.1),   # 10 workers, 100ms delay
        (20, 0.05),  # 20 workers, 50ms delay
        (50, 0.02),  # 50 workers, 20ms delay
    ]

    results = []

    for workers, delay in worker_configs:
        result = run_test(workers, TEST_URLS, delay)
        results.append(result)
        time.sleep(3)  # Pause between tests to avoid rate limiting

    # Calculate speedup and efficiency
    baseline = results[0]
    for result in results:
        if baseline.total_time > 0 and result.total_time > 0:
            result.speedup = baseline.total_time / result.total_time
            result.efficiency = (result.speedup / result.workers) * 100 if result.workers > 0 else 0

    # Print comparison table
    print("\n" + "="*80)
    print("SCALING TEST RESULTS")
    print("="*80)

    print(f"\n{'Workers':<10} {'Success':<10} {'Time (s)':<12} {'Throughput':<20} {'Speedup':<12} {'Efficiency':<12}")
    print("-" * 95)

    for result in results:
        success_rate = (result.successful / (result.successful + result.failed) * 100) if (result.successful + result.failed) > 0 else 0
        print(f"{result.workers:<10} "
              f"{success_rate:<10.1f}% "
              f"{result.total_time:<12.2f} "
              f"{result.docs_per_hour:<20.1f} "
              f"{result.speedup:<12.2f}x "
              f"{result.efficiency:<12.1f}%")

    # Find best configuration
    valid_results = [r for r in results if r.successful > 0]

    if valid_results:
        best_throughput = max(valid_results, key=lambda r: r.docs_per_hour)
        best_efficiency = max(valid_results[1:], key=lambda r: r.efficiency) if len(valid_results) > 1 else valid_results[0]

        print("\n" + "="*80)
        print("ANALYSIS")
        print("="*80)

        print(f"\nBest Throughput: {best_throughput.workers} workers")
        print(f"  {best_throughput.docs_per_hour:.1f} docs/hour")
        print(f"  {best_throughput.speedup:.2f}x speedup")
        print(f"  {best_throughput.successful}/{best_throughput.successful + best_throughput.failed} success rate")

        print(f"\nBest Efficiency: {best_efficiency.workers} workers")
        print(f"  {best_efficiency.efficiency:.1f}% efficient")
        print(f"  {best_efficiency.speedup:.2f}x speedup")
        print(f"  {best_efficiency.docs_per_hour:.1f} docs/hour")

        # Extrapolation
        print("\n" + "="*80)
        print("EXTRAPOLATION TO 1.4M DOCUMENTS")
        print("="*80)

        total_docs = 1_400_000

        print(f"\n{'Workers':<10} {'Time (hours)':<15} {'Time (days)':<15} {'Time Saved (days)':<20}")
        print("-" * 80)

        if baseline.docs_per_hour > 0:
            baseline_hours = total_docs / baseline.docs_per_hour

            for result in valid_results:
                if result.docs_per_hour > 0:
                    hours = total_docs / result.docs_per_hour
                    days = hours / 24
                    time_saved_days = (baseline_hours - hours) / 24

                    print(f"{result.workers:<10} "
                          f"{hours:<15.1f} "
                          f"{days:<15.1f} "
                          f"{time_saved_days:<20.1f}")

        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)

        print(f"\nFor Production Deployment:")
        print(f"  Recommended: {best_throughput.workers} workers")
        print(f"  Expected throughput: {best_throughput.docs_per_hour:.1f} docs/hour")
        print(f"  Time for 1.4M docs: {total_docs/best_throughput.docs_per_hour/24:.1f} days")

        print(f"\nObservations:")

        # Check scaling pattern
        throughputs = [r.docs_per_hour for r in valid_results]
        if len(throughputs) >= 3:
            improvement_rate = (throughputs[-1] - throughputs[0]) / throughputs[0]

            if improvement_rate > 1.0:
                print(f"  ✓  Good scaling: {improvement_rate*100:.1f}% improvement")
                print(f"  →  Can scale to more workers for higher throughput")
            elif improvement_rate > 0.5:
                print(f"  ⚠️  Moderate scaling: {improvement_rate*100:.1f}% improvement")
                print(f"  →  Diminishing returns starting to appear")
            else:
                print(f"  ⚠️  Limited scaling: {improvement_rate*100:.1f}% improvement only")
                print(f"  →  Network/server bottleneck reached")

        # Success rate analysis
        avg_success_rate = sum(r.successful for r in valid_results) / sum(r.successful + r.failed for r in valid_results) * 100

        if avg_success_rate > 95:
            print(f"  ✓  Excellent reliability: {avg_success_rate:.1f}% success rate")
        elif avg_success_rate > 80:
            print(f"  ⚠️  Good reliability: {avg_success_rate:.1f}% success rate")
        else:
            print(f"  ⚠️  Rate limiting detected: {avg_success_rate:.1f}% success rate")
            print(f"  →  Consider using proxy rotation or reducing concurrency")

    print("\n" + "="*80)

    # Save results
    import json
    from pathlib import Path

    Path('logs').mkdir(exist_ok=True)

    results_file = Path('logs') / f"conservative_scaling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'test_urls': len(TEST_URLS),
            'results': [
                {
                    'workers': r.workers,
                    'total_time': r.total_time,
                    'successful': r.successful,
                    'failed': r.failed,
                    'total_bytes': r.total_bytes,
                    'docs_per_hour': r.docs_per_hour,
                    'speedup': r.speedup,
                    'efficiency': r.efficiency
                }
                for r in results
            ]
        }, f, indent=2)

    logger.info(f"Results saved to: {results_file}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
