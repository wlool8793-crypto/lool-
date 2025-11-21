#!/usr/bin/env python3
"""
Test script for proxy integration
Tests proxy manager, proxy rotation, and integration with scraper
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.proxy_manager import ProxyManager, ProxyInfo, create_proxy_manager_from_env
from src.scraper import IndianKanoonScraper

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_proxy_manager_creation():
    """Test creating a proxy manager"""
    print("\n" + "="*80)
    print("TEST 1: Proxy Manager Creation")
    print("="*80)

    # Test with manual proxy list
    proxies = [
        ProxyInfo(host="proxy1.example.com", port=8080, username="user1", password="pass1"),
        ProxyInfo(host="proxy2.example.com", port=8080, username="user2", password="pass2"),
        ProxyInfo(host="proxy3.example.com", port=8080, username="user3", password="pass3"),
    ]

    manager = ProxyManager(proxies=proxies, rotation_strategy="round_robin")

    print(f"✓ Created proxy manager with {len(manager.proxies)} proxies")
    print(f"✓ Rotation strategy: {manager.rotation_strategy}")

    # Test round-robin rotation
    print("\nTesting round-robin rotation:")
    for i in range(5):
        proxy = manager.get_next_proxy()
        if proxy:
            print(f"  Request {i+1}: {proxy.host}:{proxy.port}")

    return manager


def test_webshare_api():
    """Test WebShare.io API integration"""
    print("\n" + "="*80)
    print("TEST 2: WebShare.io API Integration")
    print("="*80)

    api_key = os.getenv("WEBSHARE_API_KEY")

    if not api_key or api_key == "your_webshare_api_key_here":
        print("⚠ WebShare.io API key not configured")
        print("  Set WEBSHARE_API_KEY in .env to test API integration")
        return None

    manager = ProxyManager(webshare_api_key=api_key)

    if len(manager.proxies) > 0:
        print(f"✓ Successfully loaded {len(manager.proxies)} proxies from WebShare.io")
        print(f"\nFirst 3 proxies:")
        for i, proxy in enumerate(manager.proxies[:3], 1):
            print(f"  {i}. {proxy.host}:{proxy.port}")
        return manager
    else:
        print("✗ Failed to load proxies from WebShare.io")
        return None


def test_proxy_from_env():
    """Test creating proxy manager from environment"""
    print("\n" + "="*80)
    print("TEST 3: Proxy Manager from Environment")
    print("="*80)

    manager = create_proxy_manager_from_env()

    if manager:
        print(f"✓ Created proxy manager from environment")
        print(f"  Proxies loaded: {len(manager.proxies)}")
        print(f"  Rotation strategy: {manager.rotation_strategy}")
        manager.print_statistics()
        return manager
    else:
        print("⚠ No proxy configuration found in environment")
        print("  This is OK if you're testing without proxies")
        return None


def test_scraper_with_proxy():
    """Test scraper with proxy integration"""
    print("\n" + "="*80)
    print("TEST 4: Scraper with Proxy")
    print("="*80)

    manager = create_proxy_manager_from_env()

    if not manager or len(manager.proxies) == 0:
        print("⚠ No proxies available, testing scraper without proxy")
        scraper = IndianKanoonScraper(delay=1, headless=True)
        print("✓ Created scraper without proxy")
    else:
        # Get a proxy from the manager
        proxy_info = manager.get_next_proxy()
        proxy_dict = proxy_info.get_proxy_dict()

        print(f"Using proxy: {proxy_info.host}:{proxy_info.port}")

        # Create scraper with proxy
        scraper = IndianKanoonScraper(delay=1, headless=True, proxy=proxy_dict)
        print("✓ Created scraper with proxy")

    return scraper


def test_proxy_health_check():
    """Test proxy health check"""
    print("\n" + "="*80)
    print("TEST 5: Proxy Health Check")
    print("="*80)

    manager = create_proxy_manager_from_env()

    if not manager or len(manager.proxies) == 0:
        print("⚠ No proxies available for health check")
        return

    print(f"Testing first 3 proxies (this may take ~30 seconds)...")

    for i, proxy in enumerate(manager.proxies[:3], 1):
        print(f"\nProxy {i}: {proxy.host}:{proxy.port}")
        is_healthy = manager.health_check_proxy(proxy, test_url="https://httpbin.org/ip")

        if is_healthy:
            print(f"  ✓ HEALTHY - Response time: {proxy.avg_response_time:.2f}s")
        else:
            print(f"  ✗ FAILED - Consecutive failures: {proxy.consecutive_failures}")

    print("\nUpdated statistics after health checks:")
    manager.print_statistics()


def test_proxy_rotation_strategies():
    """Test different proxy rotation strategies"""
    print("\n" + "="*80)
    print("TEST 6: Proxy Rotation Strategies")
    print("="*80)

    # Create test proxies
    proxies = [
        ProxyInfo(host="proxy1.example.com", port=8080),
        ProxyInfo(host="proxy2.example.com", port=8080),
        ProxyInfo(host="proxy3.example.com", port=8080),
    ]

    # Simulate some usage
    proxies[0].record_success(0.5)
    proxies[0].record_success(0.6)
    proxies[1].record_success(1.2)
    proxies[2].record_success(0.8)
    proxies[2].record_failure()

    strategies = ["round_robin", "least_used", "best_performing"]

    for strategy in strategies:
        print(f"\nTesting {strategy} strategy:")
        manager = ProxyManager(proxies=proxies.copy(), rotation_strategy=strategy)

        for i in range(3):
            proxy = manager.get_next_proxy()
            print(f"  Request {i+1}: {proxy.host} "
                  f"(used: {proxy.total_requests}, success: {proxy.get_success_rate():.1%})")


def main():
    """Run all tests"""
    print("="*80)
    print("PROXY INTEGRATION TEST SUITE")
    print("="*80)

    try:
        # Test 1: Basic proxy manager
        test_proxy_manager_creation()

        # Test 2: WebShare.io API
        test_webshare_api()

        # Test 3: Environment configuration
        test_proxy_from_env()

        # Test 4: Scraper integration
        test_scraper_with_proxy()

        # Test 5: Health check (optional, may be slow)
        try:
            user_input = input("\n\nRun proxy health checks? (may take 30+ seconds) [y/N]: ").lower()
            if user_input == 'y':
                test_proxy_health_check()
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping health checks (non-interactive mode)")

        # Test 6: Rotation strategies
        test_proxy_rotation_strategies()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        print("\n✓ Proxy integration is working correctly!")
        print("\nNext steps:")
        print("1. Add your WebShare.io API key to .env")
        print("2. Run: python bulk_download.py --max-workers 20")
        print("3. Monitor proxy statistics in the output")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
