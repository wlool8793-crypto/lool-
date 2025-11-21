#!/usr/bin/env python3
"""
Test script for concurrent download system.
Tests the priority queue, rate limiter, and worker functionality.
"""

import sys
import logging
from pathlib import Path
from src.download_queue import (
    PriorityDownloadQueue,
    RateLimiter,
    DownloadTask,
    DownloadPriority,
    create_download_queue,
    create_rate_limiter
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_priority_queue():
    """Test priority queue functionality."""
    print("\n" + "="*80)
    print("TEST 1: Priority Queue")
    print("="*80)

    queue = create_download_queue()

    # Add test cases with different priorities
    test_cases = [
        {'case_url': 'https://indiankanoon.org/doc/1/', 'title': 'Test Case 1', 'court': 'High Court'},
        {'case_url': 'https://indiankanoon.org/doc/2/', 'title': 'Test Case 2', 'court': 'Supreme Court'},
        {'case_url': 'https://indiankanoon.org/doc/3/', 'title': 'Test Case 3', 'court': 'Tribunal'},
        {'case_url': 'https://indiankanoon.org/doc/4/', 'title': 'Test Case 4', 'court': 'District Court'},
        {'case_url': 'https://indiankanoon.org/doc/2/', 'title': 'Duplicate', 'court': 'Supreme Court'},  # Duplicate
    ]

    print("\nAdding test cases to queue...")
    for case in test_cases:
        added = queue.add_task(case)
        status = "✓ Added" if added else "✗ Rejected (duplicate)"
        print(f"  {status}: {case['title']} - {case['court']}")

    # Get statistics
    stats = queue.get_statistics()
    print(f"\nQueue Statistics:")
    print(f"  Total added: {stats['total_added']}")
    print(f"  Duplicates rejected: {stats['duplicates_rejected']}")
    print(f"  Queue size: {stats['queue_size']}")
    print(f"  Deduplication rate: {stats['deduplication_rate']:.1f}%")
    print(f"\nBy Priority:")
    print(f"  Supreme Court: {stats['by_priority']['supreme_court']}")
    print(f"  High Court: {stats['by_priority']['high_court']}")
    print(f"  Tribunal: {stats['by_priority']['tribunal']}")
    print(f"  Other: {stats['by_priority']['other']}")

    # Retrieve tasks in priority order
    print("\nRetrieving tasks (should be in priority order):")
    while not queue.is_empty():
        task = queue.get_task(timeout=0.1)
        if task:
            court = task.case_data.get('court', 'Unknown')
            title = task.case_data.get('title', 'Unknown')
            print(f"  Priority {task.priority}: {title} - {court}")
            queue.mark_completed(task)

    final_stats = queue.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Completed: {final_stats['completed']}")
    print(f"  Failed: {final_stats['failed']}")

    assert stats['total_added'] == 4, "Should add 4 unique tasks"
    assert stats['duplicates_rejected'] == 1, "Should reject 1 duplicate"
    assert final_stats['completed'] == 4, "Should complete all 4 tasks"

    print("\n✓ Priority Queue Test PASSED")
    return True


def test_rate_limiter():
    """Test rate limiter functionality."""
    print("\n" + "="*80)
    print("TEST 2: Rate Limiter")
    print("="*80)

    import time

    # Create rate limiter: 5 requests per second
    rate_limiter = create_rate_limiter(requests_per_second=5.0)

    print("\nTesting rate limiting (5 requests/second)...")
    start_time = time.time()

    # Try to make 10 requests
    for i in range(10):
        request_start = time.time()
        rate_limiter.acquire()
        elapsed = time.time() - request_start

        print(f"  Request {i+1}: Waited {elapsed:.3f}s")

    total_time = time.time() - start_time
    expected_time = 10 / 5.0  # 10 requests at 5 req/sec = 2 seconds

    print(f"\nTotal time: {total_time:.2f}s (expected ~{expected_time:.2f}s)")

    # Allow some tolerance (±20%)
    assert abs(total_time - expected_time) < expected_time * 0.3, \
        f"Rate limiting failed: took {total_time:.2f}s, expected ~{expected_time:.2f}s"

    print("\n✓ Rate Limiter Test PASSED")
    return True


def test_download_task():
    """Test DownloadTask creation and hashing."""
    print("\n" + "="*80)
    print("TEST 3: Download Task & Hashing")
    print("="*80)

    # Create tasks
    task1 = DownloadTask(
        priority=DownloadPriority.SUPREME_COURT,
        case_data={'case_url': 'https://indiankanoon.org/doc/12345/'}
    )

    task2 = DownloadTask(
        priority=DownloadPriority.HIGH_COURT,
        case_data={'case_url': 'https://indiankanoon.org/doc/67890/'}
    )

    task3 = DownloadTask(
        priority=DownloadPriority.SUPREME_COURT,
        case_data={'case_url': 'https://indiankanoon.org/doc/12345/'}  # Same URL as task1
    )

    print(f"\nTask 1:")
    print(f"  URL: {task1.case_data['case_url']}")
    print(f"  Hash: {task1.url_hash[:16]}...")
    print(f"  Priority: {task1.priority}")

    print(f"\nTask 2:")
    print(f"  URL: {task2.case_data['case_url']}")
    print(f"  Hash: {task2.url_hash[:16]}...")
    print(f"  Priority: {task2.priority}")

    print(f"\nTask 3 (duplicate URL):")
    print(f"  URL: {task3.case_data['case_url']}")
    print(f"  Hash: {task3.url_hash[:16]}...")
    print(f"  Priority: {task3.priority}")

    # Verify hashing
    assert task1.url_hash == task3.url_hash, "Same URLs should have same hash"
    assert task1.url_hash != task2.url_hash, "Different URLs should have different hashes"

    # Verify priority ordering
    assert task1 < task2, "Supreme Court should have higher priority than High Court"

    print("\n✓ Download Task Test PASSED")
    return True


def test_integration():
    """Integration test simulating concurrent download workflow."""
    print("\n" + "="*80)
    print("TEST 4: Integration Test")
    print("="*80)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    import threading

    # Create queue and rate limiter
    queue = create_download_queue()
    rate_limiter = create_rate_limiter(requests_per_second=10.0)
    stats_lock = threading.Lock()

    overall_stats = {
        'processed': 0,
        'success': 0,
        'failed': 0
    }

    # Mock worker function
    def mock_worker(task, rate_limiter, stats_lock, overall_stats):
        """Simulate a download worker."""
        rate_limiter.acquire()

        # Simulate work
        time.sleep(0.1)

        result = {
            'success': True,
            'case_id': task.case_data.get('case_url', ''),
            'title': task.case_data.get('title', 'Unknown')
        }

        with stats_lock:
            overall_stats['processed'] += 1
            if result['success']:
                overall_stats['success'] += 1
            else:
                overall_stats['failed'] += 1

        return result

    # Add test cases
    print("\nAdding 20 test cases to queue...")
    for i in range(20):
        case = {
            'case_url': f'https://indiankanoon.org/doc/{i}/',
            'title': f'Test Case {i}',
            'court': 'Supreme Court' if i % 3 == 0 else 'High Court'
        }
        queue.add_task(case)

    queue_stats = queue.get_statistics()
    print(f"Queue populated: {queue_stats['total_added']} tasks")

    # Process with thread pool
    print("\nProcessing with 5 workers...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=5, thread_name_prefix='TestWorker') as executor:
        futures = []

        # Submit all tasks
        while not queue.is_empty():
            task = queue.get_task(timeout=0.1)
            if task:
                future = executor.submit(
                    mock_worker,
                    task,
                    rate_limiter,
                    stats_lock,
                    overall_stats
                )
                futures.append((future, task))

        # Wait for completion
        for future, task in as_completed([f for f, _ in futures]):
            try:
                result = future.result(timeout=5)
                queue.mark_completed(task)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                queue.mark_failed(task)

    elapsed_time = time.time() - start_time
    final_stats = queue.get_statistics()

    print(f"\nIntegration Test Results:")
    print(f"  Total processed: {overall_stats['processed']}")
    print(f"  Successful: {overall_stats['success']}")
    print(f"  Failed: {overall_stats['failed']}")
    print(f"  Time elapsed: {elapsed_time:.2f}s")
    print(f"  Processing rate: {overall_stats['processed']/elapsed_time:.1f} tasks/sec")

    assert overall_stats['processed'] == 20, "Should process all 20 tasks"
    assert final_stats['completed'] == 20, "Should complete all 20 tasks"

    print("\n✓ Integration Test PASSED")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("CONCURRENT DOWNLOAD SYSTEM TEST SUITE")
    print("="*80)

    tests = [
        ("Priority Queue", test_priority_queue),
        ("Rate Limiter", test_rate_limiter),
        ("Download Task", test_download_task),
        ("Integration", test_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with error: {e}")
            results.append((test_name, False, str(e)))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, error in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
        if error:
            print(f"    Error: {error}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total - passed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
