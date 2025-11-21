"""
Proxy Manager for IndianKanoon Scraper
Handles WebShare.io proxy rotation, health tracking, and failover.
"""

import os
import time
import logging
import threading
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class ProxyInfo:
    """Information about a single proxy"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"

    # Health tracking
    total_requests: int = 0
    failed_requests: int = 0
    last_used: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    is_active: bool = True
    consecutive_failures: int = 0

    # Performance tracking
    avg_response_time: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=10))

    def get_proxy_url(self) -> str:
        """Get formatted proxy URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

    def get_proxy_dict(self) -> Dict[str, str]:
        """Get proxy dict for requests library"""
        proxy_url = self.get_proxy_url()
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def record_success(self, response_time: float):
        """Record successful request"""
        self.total_requests += 1
        self.last_used = datetime.now()
        self.consecutive_failures = 0
        self.response_times.append(response_time)

        # Update average response time
        if self.response_times:
            self.avg_response_time = sum(self.response_times) / len(self.response_times)

    def record_failure(self):
        """Record failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = datetime.now()
        self.consecutive_failures += 1

        # Disable proxy after 5 consecutive failures
        if self.consecutive_failures >= 5:
            self.is_active = False
            logger.warning(f"Proxy {self.host}:{self.port} disabled after 5 consecutive failures")

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 1.0
        return (self.total_requests - self.failed_requests) / self.total_requests

    def __str__(self) -> str:
        return f"{self.host}:{self.port} (success: {self.get_success_rate():.1%}, avg_time: {self.avg_response_time:.2f}s)"


class ProxyManager:
    """
    Manages proxy pool with round-robin rotation and health tracking.
    Supports WebShare.io API integration.
    """

    def __init__(
        self,
        proxies: Optional[List[ProxyInfo]] = None,
        webshare_api_key: Optional[str] = None,
        rotation_strategy: str = "round_robin",
        health_check_enabled: bool = True,
        health_check_interval: int = 300  # 5 minutes
    ):
        """
        Initialize ProxyManager

        Args:
            proxies: List of ProxyInfo objects
            webshare_api_key: WebShare.io API key for auto-fetching proxies
            rotation_strategy: 'round_robin', 'least_used', or 'best_performing'
            health_check_enabled: Enable periodic health checks
            health_check_interval: Seconds between health checks
        """
        self.proxies: List[ProxyInfo] = proxies or []
        self.webshare_api_key = webshare_api_key
        self.rotation_strategy = rotation_strategy
        self.health_check_enabled = health_check_enabled
        self.health_check_interval = health_check_interval

        # Thread safety
        self._lock = threading.Lock()
        self._current_index = 0

        # Statistics
        self.total_requests = 0
        self.total_failures = 0

        # Load proxies from WebShare.io if API key provided
        if webshare_api_key and not proxies:
            self.load_proxies_from_webshare()

        logger.info(f"ProxyManager initialized with {len(self.proxies)} proxies, strategy: {rotation_strategy}")

    def load_proxies_from_webshare(self) -> int:
        """
        Load proxies from WebShare.io API

        Returns:
            Number of proxies loaded
        """
        if not self.webshare_api_key:
            logger.error("WebShare.io API key not provided")
            return 0

        try:
            logger.info("Fetching proxies from WebShare.io API...")

            url = "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
            headers = {"Authorization": f"Token {self.webshare_api_key}"}

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            proxies_data = data.get("results", [])

            # Parse proxies
            loaded_count = 0
            for proxy_data in proxies_data:
                proxy = ProxyInfo(
                    host=proxy_data.get("proxy_address"),
                    port=proxy_data.get("port"),
                    username=proxy_data.get("username"),
                    password=proxy_data.get("password"),
                    protocol="http"
                )
                self.proxies.append(proxy)
                loaded_count += 1

            logger.info(f"Successfully loaded {loaded_count} proxies from WebShare.io")

            # Fetch additional pages if needed
            total_count = data.get("count", 0)
            if total_count > 100:
                logger.info(f"Total proxies available: {total_count}, fetching additional pages...")
                # Implement pagination if needed

            return loaded_count

        except Exception as e:
            logger.error(f"Failed to load proxies from WebShare.io: {e}")
            return 0

    def load_proxies_from_file(self, file_path: str, format: str = "host:port:user:pass") -> int:
        """
        Load proxies from a text file

        Args:
            file_path: Path to proxy file
            format: Format of each line (default: "host:port:user:pass")

        Returns:
            Number of proxies loaded
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            loaded_count = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split(':')

                if len(parts) >= 2:
                    proxy = ProxyInfo(
                        host=parts[0],
                        port=int(parts[1]),
                        username=parts[2] if len(parts) > 2 else None,
                        password=parts[3] if len(parts) > 3 else None
                    )
                    self.proxies.append(proxy)
                    loaded_count += 1

            logger.info(f"Loaded {loaded_count} proxies from {file_path}")
            return loaded_count

        except Exception as e:
            logger.error(f"Failed to load proxies from file: {e}")
            return 0

    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """
        Get next proxy based on rotation strategy

        Returns:
            ProxyInfo object or None if no proxies available
        """
        with self._lock:
            active_proxies = [p for p in self.proxies if p.is_active]

            if not active_proxies:
                logger.error("No active proxies available!")
                return None

            if self.rotation_strategy == "round_robin":
                proxy = self._get_round_robin(active_proxies)
            elif self.rotation_strategy == "least_used":
                proxy = self._get_least_used(active_proxies)
            elif self.rotation_strategy == "best_performing":
                proxy = self._get_best_performing(active_proxies)
            else:
                proxy = active_proxies[0]

            return proxy

    def _get_round_robin(self, active_proxies: List[ProxyInfo]) -> ProxyInfo:
        """Round-robin selection"""
        proxy = active_proxies[self._current_index % len(active_proxies)]
        self._current_index += 1
        return proxy

    def _get_least_used(self, active_proxies: List[ProxyInfo]) -> ProxyInfo:
        """Select least used proxy"""
        return min(active_proxies, key=lambda p: p.total_requests)

    def _get_best_performing(self, active_proxies: List[ProxyInfo]) -> ProxyInfo:
        """Select best performing proxy based on success rate and response time"""
        # Weight: 70% success rate, 30% response time
        def score(p: ProxyInfo) -> float:
            success_rate = p.get_success_rate()
            # Invert response time (lower is better), normalize to 0-1 range
            time_score = 1.0 / (1.0 + p.avg_response_time) if p.avg_response_time > 0 else 1.0
            return (success_rate * 0.7) + (time_score * 0.3)

        return max(active_proxies, key=score)

    def get_statistics(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        with self._lock:
            active_count = sum(1 for p in self.proxies if p.is_active)
            inactive_count = len(self.proxies) - active_count

            if self.proxies:
                avg_success_rate = sum(p.get_success_rate() for p in self.proxies) / len(self.proxies)
                avg_response_time = sum(p.avg_response_time for p in self.proxies if p.avg_response_time > 0) / max(1, sum(1 for p in self.proxies if p.avg_response_time > 0))
            else:
                avg_success_rate = 0.0
                avg_response_time = 0.0

            return {
                "total_proxies": len(self.proxies),
                "active_proxies": active_count,
                "inactive_proxies": inactive_count,
                "avg_success_rate": avg_success_rate,
                "avg_response_time": avg_response_time,
                "total_requests": sum(p.total_requests for p in self.proxies),
                "total_failures": sum(p.failed_requests for p in self.proxies)
            }

    def print_statistics(self):
        """Print detailed proxy statistics"""
        stats = self.get_statistics()

        print("\n" + "="*80)
        print("PROXY POOL STATISTICS")
        print("="*80)
        print(f"Total Proxies: {stats['total_proxies']}")
        print(f"Active: {stats['active_proxies']} | Inactive: {stats['inactive_proxies']}")
        print(f"Average Success Rate: {stats['avg_success_rate']:.1%}")
        print(f"Average Response Time: {stats['avg_response_time']:.2f}s")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Failures: {stats['total_failures']}")
        print("="*80)

        # Top 5 performing proxies
        if self.proxies:
            print("\nTop 5 Performing Proxies:")
            sorted_proxies = sorted(
                self.proxies,
                key=lambda p: p.get_success_rate(),
                reverse=True
            )[:5]

            for i, proxy in enumerate(sorted_proxies, 1):
                print(f"  {i}. {proxy}")

        print()

    def health_check_proxy(self, proxy: ProxyInfo, test_url: str = "https://httpbin.org/ip") -> bool:
        """
        Perform health check on a single proxy

        Args:
            proxy: ProxyInfo to test
            test_url: URL to test against

        Returns:
            True if proxy is healthy
        """
        try:
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxy.get_proxy_dict(),
                timeout=10
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                proxy.record_success(response_time)
                logger.debug(f"Health check passed for {proxy.host}:{proxy.port} ({response_time:.2f}s)")
                return True
            else:
                proxy.record_failure()
                logger.warning(f"Health check failed for {proxy.host}:{proxy.port} - Status: {response.status_code}")
                return False

        except Exception as e:
            proxy.record_failure()
            logger.warning(f"Health check failed for {proxy.host}:{proxy.port} - Error: {e}")
            return False

    def reactivate_proxy(self, proxy: ProxyInfo):
        """Manually reactivate a disabled proxy"""
        with self._lock:
            proxy.is_active = True
            proxy.consecutive_failures = 0
            logger.info(f"Reactivated proxy {proxy.host}:{proxy.port}")

    def disable_proxy(self, proxy: ProxyInfo):
        """Manually disable a proxy"""
        with self._lock:
            proxy.is_active = False
            logger.info(f"Disabled proxy {proxy.host}:{proxy.port}")


def create_proxy_manager_from_env() -> Optional[ProxyManager]:
    """
    Create ProxyManager from environment variables

    Environment variables:
        WEBSHARE_API_KEY: WebShare.io API key
        PROXY_FILE: Path to proxy file
        PROXY_ROTATION_STRATEGY: round_robin, least_used, or best_performing

    Returns:
        ProxyManager instance or None
    """
    api_key = os.getenv("WEBSHARE_API_KEY")
    proxy_file = os.getenv("PROXY_FILE")
    strategy = os.getenv("PROXY_ROTATION_STRATEGY", "round_robin")

    if not api_key and not proxy_file:
        logger.warning("No proxy configuration found in environment")
        return None

    manager = ProxyManager(
        webshare_api_key=api_key,
        rotation_strategy=strategy
    )

    # Load from file if provided
    if proxy_file and os.path.exists(proxy_file):
        manager.load_proxies_from_file(proxy_file)

    return manager


# Example usage
if __name__ == "__main__":
    # Test with environment variables
    logging.basicConfig(level=logging.INFO)

    manager = create_proxy_manager_from_env()

    if manager:
        manager.print_statistics()

        # Test a few proxies
        print("\nTesting first 3 proxies...")
        for i in range(min(3, len(manager.proxies))):
            proxy = manager.get_next_proxy()
            if proxy:
                print(f"\nTesting proxy: {proxy.host}:{proxy.port}")
                success = manager.health_check_proxy(proxy)
                print(f"Result: {'✓ PASS' if success else '✗ FAIL'}")

        manager.print_statistics()
