#!/usr/bin/env python3
"""
Stage 1 Scaling Test
Tests performance with different worker counts: 1, 10, 20, 50, 100
Measures scaling efficiency and identifies bottlenecks
"""

import sys
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during tests
    format='%(asctime)s - %(levelname)s - %(message)s'
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

# Test URLs - using 20 URLs to better show scaling
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
    "https://indiankanoon.org/doc/1712542/",
    "https://indiankanoon.org/doc/1766147/",
    "https://indiankanoon.org/doc/237570/",
    "https://indiankanoon.org/doc/1096615/",
    "https://indiankanoon.org/doc/1933984/",
    "https://indiankanoon.org/doc/781781/",
    "https://indiankanoon.org/doc/1362771/",
    "https://indiankanoon.org/doc/367586/",
    "https://indiankanoon.org/doc/1199182/",
    "https://indiankanoon.org/doc/1712542/",
]

def download_document(url: str) -> Dict:
    """Download a single document"""
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
        return {
            'success': False,
            'size': 0,
            'time_ms': int((time.time() - start_time) * 1000),
            'error': str(e)
        }

def run_test(num_workers: int, urls: List[str]) -> TestResult:
    """Run test with specified number of workers"""
    print(f"\n{'='*80}")
    print(f"Testing with {num_workers} workers...")
    print(f"{'='*80}")

    start_time = time.time()
    results = []

    if num_workers == 1:
        # Sequential
        for i, url in enumerate(urls, 1):
            result = download_document(url)
            results.append(result)
            if i % 5 == 0:
                print(f"  Progress: {i}/{len(urls)} documents")
    else:
        # Parallel
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(download_document, url): url for url in urls}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                results.append(result)
                if i % 5 == 0:
                    print(f"  Progress: {i}/{len(urls)} documents")

    total_time = time.time() - start_time

    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_bytes = sum(r['size'] for r in successful)

    docs_per_hour = (len(successful) / total_time) * 3600 if total_time > 0 else 0

    print(f"\n  Completed in {total_time:.2f}s")
    print(f"  Successful: {len(successful)}/{len(urls)}")
    print(f"  Throughput: {docs_per_hour:.1f} docs/hour")
    print(f"  Total data: {total_bytes/(1024*1024):.2f} MB")

    return TestResult(
        workers=num_workers,
        total_time=total_time,
        successful=len(successful),
        failed=len(failed),
        total_bytes=total_bytes,
        docs_per_hour=docs_per_hour,
        speedup=0.0,  # Will calculate later
        efficiency=0.0  # Will calculate later
    )

def main():
    """Run scaling tests"""
    print("\n" + "="*80)
    print("STAGE 1 SCALING TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total URLs: {len(TEST_URLS)}")
    print(f"Worker counts to test: 1, 10, 20, 50, 100")

    # Run tests with different worker counts
    worker_counts = [1, 10, 20, 50, 100]
    results = []

    for workers in worker_counts:
        result = run_test(workers, TEST_URLS)
        results.append(result)
        time.sleep(2)  # Brief pause between tests

    # Calculate speedup and efficiency
    baseline = results[0]
    for result in results:
        if baseline.total_time > 0:
            result.speedup = baseline.total_time / result.total_time
            result.efficiency = (result.speedup / result.workers) * 100

    # Print comparison table
    print("\n" + "="*80)
    print("SCALING TEST RESULTS - COMPARISON")
    print("="*80)

    print(f"\n{'Workers':<10} {'Time (s)':<12} {'Throughput':<20} {'Speedup':<12} {'Efficiency':<12}")
    print("-" * 80)

    for result in results:
        print(f"{result.workers:<10} "
              f"{result.total_time:<12.2f} "
              f"{result.docs_per_hour:<20.1f} "
              f"{result.speedup:<12.2f}x "
              f"{result.efficiency:<12.1f}%")

    # Analyze scaling behavior
    print("\n" + "="*80)
    print("SCALING ANALYSIS")
    print("="*80)

    # Find best configuration
    best_throughput = max(results, key=lambda r: r.docs_per_hour)
    best_efficiency = max(results[1:], key=lambda r: r.efficiency)  # Skip baseline

    print(f"\nBest Throughput: {best_throughput.workers} workers")
    print(f"  {best_throughput.docs_per_hour:.1f} docs/hour")
    print(f"  {best_throughput.speedup:.2f}x speedup")

    print(f"\nBest Efficiency: {best_efficiency.workers} workers")
    print(f"  {best_efficiency.efficiency:.1f}% efficient")
    print(f"  {best_efficiency.speedup:.2f}x speedup")

    # Extrapolation to 1.4M documents
    print("\n" + "="*80)
    print("EXTRAPOLATION TO 1.4M DOCUMENTS")
    print("="*80)

    total_docs = 1_400_000

    print(f"\n{'Workers':<10} {'Time (hours)':<15} {'Time (days)':<15} {'Time Saved':<20}")
    print("-" * 80)

    baseline_hours = total_docs / baseline.docs_per_hour

    for result in results:
        if result.docs_per_hour > 0:
            hours = total_docs / result.docs_per_hour
            days = hours / 24
            time_saved_hours = baseline_hours - hours
            time_saved_days = time_saved_hours / 24

            print(f"{result.workers:<10} "
                  f"{hours:<15.1f} "
                  f"{days:<15.1f} "
                  f"{time_saved_days:<20.1f} days")

    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    # Find sweet spot (best efficiency above 10 workers)
    efficient_configs = [r for r in results if r.workers >= 10 and r.efficiency > 15]
    if efficient_configs:
        sweet_spot = max(efficient_configs, key=lambda r: r.docs_per_hour)

        print(f"\nRecommended Configuration: {sweet_spot.workers} workers")
        print(f"  Throughput: {sweet_spot.docs_per_hour:.1f} docs/hour")
        print(f"  Speedup: {sweet_spot.speedup:.2f}x")
        print(f"  Efficiency: {sweet_spot.efficiency:.1f}%")
        print(f"  Time for 1.4M docs: {total_docs/sweet_spot.docs_per_hour/24:.1f} days")

    print("\nScaling Observations:")

    # Check for linear scaling
    if results[-1].speedup < results[-1].workers * 0.3:
        print("  ⚠️  Diminishing returns observed at high worker counts")
        print("  ⚠️  Network I/O is the bottleneck (not CPU)")
        print("  ✓  Consider async I/O (Stage 2) for better scaling")
    else:
        print("  ✓  Good linear scaling observed")
        print("  ✓  Can continue scaling workers")

    # Check if throughput is still increasing
    if results[-1].docs_per_hour > results[-2].docs_per_hour * 1.1:
        print("  ✓  Throughput still increasing at 100 workers")
        print("  →  Could benefit from even more workers with proxy rotation")
    else:
        print("  ⚠️  Throughput plateau at high worker counts")
        print("  →  Async migration (Stage 2) recommended for further improvement")

    print("\n" + "="*80)

    # Save results to file
    import json
    from pathlib import Path

    Path('logs').mkdir(exist_ok=True)

    results_file = Path('logs') / f"scaling_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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

    print(f"Results saved to: {results_file}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
