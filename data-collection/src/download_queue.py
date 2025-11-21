"""
Priority Download Queue Module
Manages concurrent PDF downloads with priority queuing and deduplication.
"""

import hashlib
import logging
import threading
from queue import PriorityQueue, Empty
from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Any
from datetime import datetime
from enum import IntEnum

logger = logging.getLogger(__name__)


class DownloadPriority(IntEnum):
    """Priority levels for downloads (lower number = higher priority)."""
    SUPREME_COURT = 1
    HIGH_COURT = 2
    TRIBUNAL = 3
    OTHER = 4


@dataclass(order=True)
class DownloadTask:
    """
    Represents a download task with priority ordering.

    Tasks are ordered by priority first, then by timestamp.
    """
    priority: int
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    case_data: Dict[str, Any] = field(default_factory=dict, compare=False)
    url_hash: str = field(default="", compare=False)

    def __post_init__(self):
        """Generate URL hash if not provided."""
        if not self.url_hash and self.case_data:
            url = self.case_data.get('case_url', '') or self.case_data.get('pdf_link', '')
            self.url_hash = self._generate_hash(url)

    @staticmethod
    def _generate_hash(url: str) -> str:
        """Generate SHA256 hash of URL for deduplication."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()


class PriorityDownloadQueue:
    """
    Thread-safe priority queue for managing concurrent downloads.

    Features:
    - Priority-based ordering (Supreme Court gets priority 1)
    - URL deduplication using hash-based tracking
    - Thread-safe operations
    - Statistics tracking
    """

    def __init__(self, max_size: int = 0):
        """
        Initialize priority download queue.

        Args:
            max_size: Maximum queue size (0 = unlimited)
        """
        self.queue = PriorityQueue(maxsize=max_size)
        self.seen_urls: Set[str] = set()
        self.lock = threading.RLock()

        # Statistics
        self.stats = {
            'total_added': 0,
            'duplicates_rejected': 0,
            'completed': 0,
            'failed': 0,
            'by_priority': {
                DownloadPriority.SUPREME_COURT: 0,
                DownloadPriority.HIGH_COURT: 0,
                DownloadPriority.TRIBUNAL: 0,
                DownloadPriority.OTHER: 0
            }
        }

    def add_task(self, case_data: Dict[str, Any], priority: Optional[int] = None) -> bool:
        """
        Add a download task to the queue.

        Args:
            case_data: Dictionary containing case information
            priority: Optional priority override (1-4)

        Returns:
            True if task was added, False if duplicate
        """
        with self.lock:
            # Determine priority if not provided
            if priority is None:
                priority = self._determine_priority(case_data)

            # Create task
            task = DownloadTask(
                priority=priority,
                case_data=case_data
            )

            # Check for duplicates
            if task.url_hash in self.seen_urls:
                self.stats['duplicates_rejected'] += 1
                logger.debug(f"Duplicate URL rejected: {case_data.get('case_url', 'N/A')[:50]}...")
                return False

            # Add to queue and tracking
            self.queue.put(task)
            self.seen_urls.add(task.url_hash)
            self.stats['total_added'] += 1
            self.stats['by_priority'][DownloadPriority(priority)] += 1

            logger.debug(f"Added task with priority {priority}: {case_data.get('title', 'N/A')[:50]}...")
            return True

    def get_task(self, timeout: Optional[float] = None) -> Optional[DownloadTask]:
        """
        Get next task from queue.

        Args:
            timeout: Maximum time to wait for a task (None = block indefinitely)

        Returns:
            DownloadTask or None if queue is empty/timeout
        """
        try:
            task = self.queue.get(timeout=timeout)
            return task
        except Empty:
            return None

    def mark_completed(self, task: DownloadTask):
        """Mark a task as completed."""
        with self.lock:
            self.stats['completed'] += 1
            self.queue.task_done()

    def mark_failed(self, task: DownloadTask):
        """Mark a task as failed."""
        with self.lock:
            self.stats['failed'] += 1
            # Remove from seen_urls to allow retry
            if task.url_hash in self.seen_urls:
                self.seen_urls.remove(task.url_hash)
            self.queue.task_done()

    def size(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self.queue.empty()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        with self.lock:
            return {
                'queue_size': self.size(),
                'total_added': self.stats['total_added'],
                'duplicates_rejected': self.stats['duplicates_rejected'],
                'completed': self.stats['completed'],
                'failed': self.stats['failed'],
                'in_progress': self.stats['total_added'] - self.stats['completed'] - self.stats['failed'],
                'by_priority': {
                    'supreme_court': self.stats['by_priority'][DownloadPriority.SUPREME_COURT],
                    'high_court': self.stats['by_priority'][DownloadPriority.HIGH_COURT],
                    'tribunal': self.stats['by_priority'][DownloadPriority.TRIBUNAL],
                    'other': self.stats['by_priority'][DownloadPriority.OTHER]
                },
                'deduplication_rate': (
                    self.stats['duplicates_rejected'] /
                    (self.stats['total_added'] + self.stats['duplicates_rejected']) * 100
                    if (self.stats['total_added'] + self.stats['duplicates_rejected']) > 0 else 0
                )
            }

    def _determine_priority(self, case_data: Dict[str, Any]) -> int:
        """
        Determine priority based on case data.

        Args:
            case_data: Case information dictionary

        Returns:
            Priority level (1-4)
        """
        court = (case_data.get('court', '') or '').upper()
        court_type = case_data.get('court_type', '')

        # Check court type first
        if court_type:
            court_type_str = str(court_type).upper()
            if 'SUPREME' in court_type_str:
                return DownloadPriority.SUPREME_COURT
            elif 'HIGH' in court_type_str:
                return DownloadPriority.HIGH_COURT
            elif 'TRIBUNAL' in court_type_str:
                return DownloadPriority.TRIBUNAL

        # Fallback to court name parsing
        if 'SUPREME' in court:
            return DownloadPriority.SUPREME_COURT
        elif 'HIGH' in court:
            return DownloadPriority.HIGH_COURT
        elif 'TRIBUNAL' in court:
            return DownloadPriority.TRIBUNAL

        return DownloadPriority.OTHER

    def clear(self):
        """Clear the queue and reset tracking."""
        with self.lock:
            # Drain the queue
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                except Empty:
                    break

            # Reset tracking
            self.seen_urls.clear()
            self.stats = {
                'total_added': 0,
                'duplicates_rejected': 0,
                'completed': 0,
                'failed': 0,
                'by_priority': {
                    DownloadPriority.SUPREME_COURT: 0,
                    DownloadPriority.HIGH_COURT: 0,
                    DownloadPriority.TRIBUNAL: 0,
                    DownloadPriority.OTHER: 0
                }
            }
            logger.info("Queue cleared and reset")

    def wait_completion(self, timeout: Optional[float] = None):
        """
        Wait for all tasks to complete.

        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
        """
        self.queue.join()


class RateLimiter:
    """
    Thread-safe rate limiter for controlling request frequency.

    Implements token bucket algorithm for smooth rate limiting.
    """

    def __init__(self, max_requests_per_second: float = 5.0):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_second: Maximum requests allowed per second
        """
        self.max_rate = max_requests_per_second
        self.tokens = max_requests_per_second
        self.last_update = datetime.now()
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens for making a request.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False if rate limit exceeded
        """
        import time

        with self.lock:
            now = datetime.now()
            time_passed = (now - self.last_update).total_seconds()

            # Refill tokens based on time passed
            self.tokens = min(
                self.max_rate,
                self.tokens + time_passed * self.max_rate
            )
            self.last_update = now

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                # Calculate wait time
                wait_time = (tokens - self.tokens) / self.max_rate
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
                self.tokens = 0
                self.last_update = datetime.now()
                return True

    def reset(self):
        """Reset the rate limiter."""
        with self.lock:
            self.tokens = self.max_rate
            self.last_update = datetime.now()


# Module-level convenience functions

def create_download_queue(max_size: int = 0) -> PriorityDownloadQueue:
    """
    Create a new priority download queue.

    Args:
        max_size: Maximum queue size (0 = unlimited)

    Returns:
        Initialized PriorityDownloadQueue
    """
    return PriorityDownloadQueue(max_size=max_size)


def create_rate_limiter(requests_per_second: float = 5.0) -> RateLimiter:
    """
    Create a new rate limiter.

    Args:
        requests_per_second: Maximum requests per second

    Returns:
        Initialized RateLimiter
    """
    return RateLimiter(max_requests_per_second=requests_per_second)
