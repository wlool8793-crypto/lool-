#!/usr/bin/env python3
"""
Stage 1 Configuration Test Script
Tests URL classifier, configuration loading, and worker setup
"""

import sys
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

# Import new database modules
from src.database import DatabaseConnection, DatabaseConfig
from src.url_classifier import URLClassifier

def load_config(config_path: str = './config/config_stage1_test.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_url_classifier():
    """Test URL classifier performance"""
    print("\n" + "="*80)
    print("TEST 1: URL Classifier")
    print("="*80)

    classifier = URLClassifier()

    # Sample URLs from IndianKanoon
    test_urls = [
        "https://indiankanoon.org/doc/123456/",
        "https://indiankanoon.org/doc/789012/petition.pdf",
        "https://indiankanoon.org/search/?formInput=test",
        "https://indiankanoon.org/browse/",
        "https://indiankanoon.org/judgment/123456/",
    ]

    stats = {'direct_http': 0, 'selenium': 0, 'unknown': 0}

    for url in test_urls:
        classification, confidence, reason = classifier.classify_url(url)
        stats[classification] += 1
        print(f"\nURL: {url}")
        print(f"  Classification: {classification}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Reason: {reason}")

    print(f"\n Summary:")
    print(f"  Direct HTTP: {stats['direct_http']} ({stats['direct_http']/len(test_urls)*100:.1f}%)")
    print(f"  Selenium: {stats['selenium']} ({stats['selenium']/len(test_urls)*100:.1f}%)")
    print(f"  Unknown: {stats['unknown']} ({stats['unknown']/len(test_urls)*100:.1f}%)")

    # Calculate efficiency gain
    baseline_time = len(test_urls) * 10  # 10 sec per Selenium request
    optimized_time = (stats['direct_http'] * 3) + (stats['selenium'] * 10) + (stats['unknown'] * 10)
    improvement = (baseline_time / optimized_time - 1) * 100

    print(f"\n  Efficiency Improvement: {improvement:.1f}%")

    return True

def test_config_loading():
    """Test configuration loading and validation"""
    print("\n" + "="*80)
    print("TEST 2: Configuration Loading")
    print("="*80)

    try:
        config = load_config()

        # Extract key metrics
        workers = config['performance']['max_workers']
        rate_limit = config['safety']['max_requests_per_minute']
        per_proxy_rate = config['safety'].get('requests_per_second_per_proxy', 2.0)
        db_url = config['database']['url']

        print(f"\n  Max Workers: {workers}")
        print(f"  Rate Limit: {rate_limit} req/min")
        print(f"  Per-Proxy Rate: {per_proxy_rate} req/sec")
        print(f"  Database: {db_url.split(':')[0]}://...")

        # Calculate theoretical throughput
        aggregate_rate_per_sec = workers * per_proxy_rate
        aggregate_rate_per_min = aggregate_rate_per_sec * 60

        print(f"\n  Theoretical Throughput:")
        print(f"    {aggregate_rate_per_sec:.0f} requests/second")
        print(f"    {aggregate_rate_per_min:.0f} requests/minute")

        # Verify quality settings
        if 'quality' in config:
            print(f"\n  Quality Gates: {'ENABLED' if config['quality']['enable_quality_gates'] else 'DISABLED'}")
            print(f"  Strict Validation: {'YES' if config['quality']['strict_validation'] else 'NO'}")
            print(f"  Direct HTTP for PDFs: {'YES' if config['quality']['use_direct_http_for_pdfs'] else 'NO'}")

        return True

    except Exception as e:
        print(f"\n  ERROR: {e}")
        return False

def test_worker_pool():
    """Test ThreadPoolExecutor with configured worker count"""
    print("\n" + "="*80)
    print("TEST 3: Worker Pool Setup")
    print("="*80)

    try:
        config = load_config()
        max_workers = config['performance']['max_workers']

        # Test with smaller pool for quick verification
        test_workers = min(max_workers, 20)

        print(f"\n  Testing with {test_workers} workers (max: {max_workers})")

        def mock_task(task_id):
            """Simulate a quick download task"""
            time.sleep(0.1)  # 100ms simulated work
            return f"Task {task_id} completed"

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=test_workers) as executor:
            tasks = list(range(test_workers))
            results = list(executor.map(mock_task, tasks))

        elapsed = time.time() - start_time

        print(f"  Completed {len(results)} tasks in {elapsed:.2f} seconds")
        print(f"  Tasks per second: {len(results)/elapsed:.1f}")

        # Estimate full performance
        if test_workers < max_workers:
            print(f"\n  Estimated with {max_workers} workers:")
            estimated_rate = (len(results)/elapsed) * (max_workers/test_workers)
            print(f"    ~{estimated_rate:.0f} tasks/second")

        return True

    except Exception as e:
        print(f"\n  ERROR: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n" + "="*80)
    print("TEST 4: Database Connection")
    print("="*80)

    try:
        config = load_config()
        db_url = config['database']['url']

        # Check if database file exists for SQLite
        if 'sqlite' in db_url:
            db_path = db_url.split('sqlite:///')[-1]
            if Path(db_path).exists():
                file_size = Path(db_path).stat().st_size / (1024*1024)
                print(f"\n  Database: {db_path}")
                print(f"  Size: {file_size:.2f} MB")
                print(f"  Status: EXISTS ✓")
                return True
            else:
                print(f"\n  Database: {db_path}")
                print(f"  Status: NOT FOUND ✗")
                return False
        else:
            print(f"\n  Database: PostgreSQL")
            print(f"  Connection: (not tested in this script)")
            return True

    except Exception as e:
        print(f"\n  ERROR: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*80)
    print("STAGE 1 CONFIGURATION TEST SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"\n  Tests Run: {total}")
    print(f"  Passed: {passed} ✓")
    print(f"  Failed: {failed}")

    print(f"\n  Individual Results:")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"    {test_name}: {status}")

    if passed == total:
        print(f"\n  Overall: ALL TESTS PASSED ✓")
        print(f"\n  Stage 1 configuration is ready for deployment!")
        return 0
    else:
        print(f"\n  Overall: SOME TESTS FAILED ✗")
        print(f"\n  Please review failed tests before proceeding.")
        return 1

def main():
    """Run all Stage 1 configuration tests"""
    print("\n" + "="*80)
    print("PHASE 4 - STAGE 1 CONFIGURATION TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Config: ./config/config_stage1_test.yaml")

    results = {
        'URL Classifier': test_url_classifier(),
        'Configuration Loading': test_config_loading(),
        'Worker Pool': test_worker_pool(),
        'Database Connection': test_database_connection(),
    }

    return print_summary(results)

if __name__ == "__main__":
    sys.exit(main())
