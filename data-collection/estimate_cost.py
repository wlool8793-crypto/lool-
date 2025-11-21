#!/usr/bin/env python3
"""
Cost Estimation Tool
Estimates monthly costs and scraping completion time
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import colorlog

# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
    log_colors={'INFO': 'green', 'WARNING': 'yellow'}
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel('INFO')


# Pricing per provider (monthly)
PRICING = {
    'digitalocean': {
        's-1vcpu-1gb': 5.00,
        's-1vcpu-2gb': 10.00,
        's-2vcpu-2gb': 15.00
    },
    'vultr': {
        'vc2-1c-1gb': 6.00,
        'vc2-1c-2gb': 12.00,
        'vc2-2c-4gb': 18.00
    },
    'linode': {
        'g6-nanode-1': 5.00,
        'g6-standard-1': 10.00,
        'g6-standard-2': 20.00
    },
    'oracle': {
        'VM.Standard.E2.1.Micro': 0.00  # Always Free
    }
}


def load_proxy_data():
    """Load proxy deployment data"""
    proxy_file = Path("config/proxy_list.json")

    if not proxy_file.exists():
        logger.error("No proxy deployment found. Run deploy_vms.py first.")
        return None

    with open(proxy_file, 'r') as f:
        return json.load(f)


def calculate_vm_costs(proxy_data):
    """Calculate VM infrastructure costs"""
    total_cost = 0
    cost_breakdown = {}

    for provider, stats in proxy_data.get('providers', {}).items():
        count = stats['count']

        # Default pricing
        monthly_per_vm = 5.00
        if provider == 'vultr':
            monthly_per_vm = 6.00

        monthly_cost = count * monthly_per_vm
        total_cost += monthly_cost

        cost_breakdown[provider] = {
            'count': count,
            'per_vm': monthly_per_vm,
            'monthly': monthly_cost
        }

    return total_cost, cost_breakdown


def estimate_scraping_time(total_documents: int, proxies_count: int, delay: float = 2.0):
    """
    Estimate scraping completion time

    Args:
        total_documents: Total documents to scrape
        proxies_count: Number of proxy servers
        delay: Delay between requests (seconds)
    """
    # Assume each proxy can handle 1 request every delay seconds
    requests_per_hour = proxies_count * (3600 / delay)
    requests_per_day = requests_per_hour * 24

    # Assume 2 requests per document (1 for page, 1 for PDF)
    total_requests = total_documents * 2

    days_needed = total_requests / requests_per_day
    hours_needed = (total_requests / requests_per_hour)

    return {
        'requests_per_hour': int(requests_per_hour),
        'requests_per_day': int(requests_per_day),
        'total_requests': total_requests,
        'days': days_needed,
        'hours': hours_needed,
        'completion_date': datetime.now() + timedelta(days=days_needed)
    }


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              Cost Estimation & Planning Tool                 ║
    ║              Indian Kanoon Scraper Project                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Load deployment data
    proxy_data = load_proxy_data()

    if not proxy_data:
        print("\n❌ No deployment data found. Deploy VMs first with: python deploy_vms.py")
        return

    proxies_count = proxy_data.get('total_proxies', 0)
    total_cost, cost_breakdown = calculate_vm_costs(proxy_data)

    print("\n" + "=" * 70)
    print("INFRASTRUCTURE COSTS")
    print("=" * 70)

    print(f"\n💰 Cost Breakdown by Provider:")
    for provider, costs in cost_breakdown.items():
        print(f"\n  {provider.capitalize()}:")
        print(f"    • VMs: {costs['count']}")
        print(f"    • Cost per VM: ${costs['per_vm']:.2f}/month")
        print(f"    • Total: ${costs['monthly']:.2f}/month")

    print(f"\n📊 Total Infrastructure Cost:")
    print(f"  • Monthly: ${total_cost:.2f}")
    print(f"  • Daily: ${total_cost/30:.2f}")
    print(f"  • Hourly: ${total_cost/30/24:.3f}")

    # Scraping estimates
    print("\n" + "=" * 70)
    print("SCRAPING TIME ESTIMATES")
    print("=" * 70)

    scenarios = [
        (100000, "100K documents"),
        (500000, "500K documents"),
        (1000000, "1M documents"),
        (1400000, "1.4M documents (full dataset)")
    ]

    for doc_count, label in scenarios:
        estimate = estimate_scraping_time(doc_count, proxies_count, delay=2.0)

        print(f"\n📈 {label}:")
        print(f"  • Requests per hour: {estimate['requests_per_hour']:,}")
        print(f"  • Requests per day: {estimate['requests_per_day']:,}")
        print(f"  • Total requests: {estimate['total_requests']:,}")
        print(f"  • Estimated time: {estimate['days']:.1f} days ({estimate['hours']:.1f} hours)")
        print(f"  • Completion date: {estimate['completion_date'].strftime('%Y-%m-%d')}")
        print(f"  • Estimated cost: ${total_cost * (estimate['days']/30):.2f}")

    # Optimization suggestions
    print("\n" + "=" * 70)
    print("OPTIMIZATION TIPS")
    print("=" * 70)

    print("\n💡 To reduce costs:")
    print("  • Deploy fewer VMs (reduces monthly cost)")
    print("  • Use Oracle Cloud Always Free tier (4 free VMs)")
    print("  • Delete VMs immediately after scraping")
    print("  • Use spot/preemptible instances if available")

    print("\n⚡ To speed up scraping:")
    print("  • Deploy more VMs (increases cost)")
    print(f"  • Reduce delay between requests (currently 2s)")
    print("  • Use concurrent requests per proxy")
    print("  • Optimize parsing and storage pipeline")

    # Credit usage estimates
    print("\n" + "=" * 70)
    print("FREE CREDIT USAGE")
    print("=" * 70)

    free_credits = {
        'digitalocean': 200,
        'vultr': 100,
        'linode': 100,
        'oracle': 0  # Always free
    }

    print("\n💳 Available Free Credits:")
    total_credits = sum(free_credits.values())
    print(f"  • Total: ${total_credits}")

    for provider, credit in free_credits.items():
        if provider in cost_breakdown:
            monthly_cost = cost_breakdown[provider]['monthly']
            months = credit / monthly_cost if monthly_cost > 0 else float('inf')
            print(f"  • {provider.capitalize()}: ${credit} (covers {months:.1f} months)")

    months_covered = total_credits / total_cost if total_cost > 0 else 0
    print(f"\n⏱️  Credits will cover: {months_covered:.1f} months of scraping")
    print(f"📅  Estimated expiry: {(datetime.now() + timedelta(days=months_covered*30)).strftime('%Y-%m-%d')}")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    if months_covered >= 1:
        print("\n✅ You have sufficient credits to complete the project!")
        print(f"  • Complete scraping within {months_covered:.1f} months to stay within free credits")
    else:
        print("\n⚠️  Free credits may not cover the full project duration")
        print(f"  • Consider reducing VMs or optimizing scraping speed")

    print(f"\n🎯 Optimal Strategy:")
    print(f"  1. Start with {proxies_count} proxies")
    print(f"  2. Monitor daily progress and costs")
    print(f"  3. Adjust VM count based on progress/budget")
    print(f"  4. Delete VMs immediately when done")

    print(f"\n📊 Expected Outcome:")
    estimate_1_4m = estimate_scraping_time(1400000, proxies_count)
    print(f"  • Scrape 1.4M documents in ~{estimate_1_4m['days']:.0f} days")
    print(f"  • Cost: ${total_cost * (estimate_1_4m['days']/30):.2f}")
    print(f"  • Remaining credits: ${total_credits - (total_cost * (estimate_1_4m['days']/30)):.2f}")


if __name__ == "__main__":
    main()
