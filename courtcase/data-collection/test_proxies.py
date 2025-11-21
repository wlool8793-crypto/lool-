#!/usr/bin/env python3
"""
Test Proxy Health and Performance
Tests all deployed proxies and generates a health report
"""

import json
import requests
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import Dict, List
import colorlog

# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel('INFO')


class ProxyTester:
    """Test proxy health and performance"""

    def __init__(self, proxy_list_file: str = "config/proxy_list.json"):
        self.proxy_list_file = Path(proxy_list_file)
        self.proxies = []
        self.results = []

    def load_proxies(self):
        """Load proxies from JSON file"""
        if not self.proxy_list_file.exists():
            logger.error(f"Proxy list not found: {self.proxy_list_file}")
            return False

        with open(self.proxy_list_file, 'r') as f:
            data = json.load(f)
            self.proxies = data.get('proxies', [])

        logger.info(f"Loaded {len(self.proxies)} proxies")
        return True

    def test_proxy(self, proxy: Dict) -> Dict:
        """Test a single proxy"""
        proxy_url = proxy['proxy_url']
        result = {
            'proxy': proxy_url,
            'ip': proxy['ip'],
            'provider': proxy['provider'],
            'region': proxy['region'],
            'status': 'failed',
            'response_time': None,
            'error': None
        }

        try:
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }

            # Test with a simple request
            start_time = time.time()
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                result['status'] = 'working'
                result['response_time'] = round(response_time, 2)

                # Check if IP matches
                returned_ip = response.json().get('origin', '').split(',')[0].strip()
                if returned_ip == proxy['ip']:
                    result['status'] = 'perfect'
                else:
                    result['returned_ip'] = returned_ip

                logger.info(f"✓ {proxy['ip']} - {response_time:.2f}s")
            else:
                result['error'] = f"HTTP {response.status_code}"
                logger.warning(f"✗ {proxy['ip']} - HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
            logger.error(f"✗ {proxy['ip']} - Timeout")
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection Error'
            logger.error(f"✗ {proxy['ip']} - Connection Error")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"✗ {proxy['ip']} - {e}")

        return result

    def test_all_proxies(self, max_workers: int = 20):
        """Test all proxies in parallel"""
        logger.info("=" * 70)
        logger.info("Testing Proxy Health")
        logger.info("=" * 70)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy
                for proxy in self.proxies
            }

            with tqdm(total=len(self.proxies), desc="Testing proxies") as pbar:
                for future in as_completed(future_to_proxy):
                    result = future.result()
                    self.results.append(result)
                    pbar.update(1)

    def generate_report(self):
        """Generate and print test report"""
        if not self.results:
            logger.warning("No test results available")
            return

        working = [r for r in self.results if r['status'] in ['working', 'perfect']]
        failed = [r for r in self.results if r['status'] == 'failed']

        perfect = [r for r in self.results if r['status'] == 'perfect']
        avg_response_time = (
            sum(r['response_time'] for r in working if r['response_time'])
            / len(working) if working else 0
        )

        # Group by provider
        by_provider = {}
        for result in self.results:
            provider = result['provider']
            if provider not in by_provider:
                by_provider[provider] = {'total': 0, 'working': 0}
            by_provider[provider]['total'] += 1
            if result['status'] in ['working', 'perfect']:
                by_provider[provider]['working'] += 1

        print("\n" + "=" * 70)
        print("PROXY TEST REPORT")
        print("=" * 70)

        print(f"\n📊 Overall Statistics:")
        print(f"  • Total Proxies: {len(self.results)}")
        print(f"  • Working: {len(working)} ({len(working)/len(self.results)*100:.1f}%)")
        print(f"  • Failed: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
        print(f"  • Perfect (IP match): {len(perfect)}")
        print(f"  • Average Response Time: {avg_response_time:.2f}s")

        print(f"\n📈 By Provider:")
        for provider, stats in by_provider.items():
            success_rate = stats['working'] / stats['total'] * 100
            print(f"  • {provider.capitalize()}:")
            print(f"    - Total: {stats['total']}")
            print(f"    - Working: {stats['working']} ({success_rate:.1f}%)")

        if failed:
            print(f"\n❌ Failed Proxies ({len(failed)}):")
            for result in failed[:10]:  # Show first 10
                print(f"  • {result['ip']} ({result['provider']}) - {result['error']}")
            if len(failed) > 10:
                print(f"  ... and {len(failed) - 10} more")

        # Find fastest proxies
        fastest = sorted(
            [r for r in working if r['response_time']],
            key=lambda x: x['response_time']
        )[:10]

        if fastest:
            print(f"\n⚡ Fastest Proxies:")
            for result in fastest:
                print(f"  • {result['ip']} - {result['response_time']:.2f}s ({result['region']})")

        # Save detailed report
        report_file = Path("config/proxy_test_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total': len(self.results),
                    'working': len(working),
                    'failed': len(failed),
                    'avg_response_time': round(avg_response_time, 2)
                },
                'by_provider': by_provider,
                'results': self.results
            }, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        # Update proxy_list.txt with only working proxies
        if working:
            proxy_txt_file = Path("config/proxy_list.txt")
            with open(proxy_txt_file, 'w') as f:
                for result in working:
                    f.write(f"{result['proxy']}\n")
            print(f"✓ Updated {proxy_txt_file} with {len(working)} working proxies")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   Proxy Health Test                          ║
    ║              Indian Kanoon Scraper Project                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    tester = ProxyTester()

    if not tester.load_proxies():
        print("\n❌ No proxies to test. Run deploy_vms.py first.")
        return

    tester.test_all_proxies()
    tester.generate_report()

    print("\n✅ Proxy testing complete!")


if __name__ == "__main__":
    main()
