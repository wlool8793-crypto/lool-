#!/usr/bin/env python3
"""
Cleanup All Deployed VMs
Deletes all VMs across all cloud providers to prevent unexpected charges
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import colorlog

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cloud_providers.digitalocean_provider import DigitalOceanProvider
from src.cloud_providers.vultr_provider import VultrProvider

# Load environment
load_dotenv()

# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
    log_colors={
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
    }
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel('INFO')


class CloudConfig:
    """Simple configuration for cloud providers"""
    def __init__(self, provider_name: str):
        if provider_name == "digitalocean":
            self.token = os.getenv('DIGITALOCEAN_TOKEN', '')
        elif provider_name == "vultr":
            self.api_key = os.getenv('VULTR_API_KEY', '')


def load_deployed_vms():
    """Load list of deployed VMs from proxy_list.json"""
    proxy_list_file = Path("config/proxy_list.json")

    if not proxy_list_file.exists():
        logger.warning("No proxy_list.json found. No VMs to cleanup.")
        return {}

    with open(proxy_list_file, 'r') as f:
        data = json.load(f)

    # Group by provider
    by_provider = {}
    for proxy in data.get('proxies', []):
        provider = proxy['provider']
        if provider not in by_provider:
            by_provider[provider] = []
        by_provider[provider].append(proxy)

    return by_provider


def confirm_deletion(vm_count: int) -> bool:
    """Ask user to confirm deletion"""
    print("\n" + "=" * 70)
    print("⚠️  WARNING: VM DELETION")
    print("=" * 70)
    print(f"\nYou are about to DELETE {vm_count} VMs across all cloud providers.")
    print("This action CANNOT be undone!")
    print("\nDeleted VMs:")

    response = input("\nType 'DELETE' to confirm deletion: ")
    return response == 'DELETE'


def cleanup_digitalocean(vms):
    """Cleanup DigitalOcean droplets"""
    config = CloudConfig("digitalocean")
    if not config.token:
        logger.warning("No DigitalOcean token configured")
        return 0

    provider = DigitalOceanProvider(config)
    if not provider.authenticate():
        logger.error("Failed to authenticate with DigitalOcean")
        return 0

    logger.info(f"Cleaning up {len(vms)} DigitalOcean droplets...")

    deleted = 0
    # Get all droplets with our tag
    all_vms = provider.list_vms()

    for vm in all_vms:
        try:
            if provider.delete_vm(vm.id):
                logger.info(f"✓ Deleted: {vm.name} ({vm.ip_address})")
                deleted += 1
            else:
                logger.error(f"✗ Failed to delete: {vm.name}")
        except Exception as e:
            logger.error(f"✗ Error deleting {vm.name}: {e}")

    return deleted


def cleanup_vultr(vms):
    """Cleanup Vultr instances"""
    config = CloudConfig("vultr")
    if not config.api_key:
        logger.warning("No Vultr API key configured")
        return 0

    provider = VultrProvider(config)
    if not provider.authenticate():
        logger.error("Failed to authenticate with Vultr")
        return 0

    logger.info(f"Cleaning up {len(vms)} Vultr instances...")

    deleted = 0
    # Get all instances with our tag
    all_vms = provider.list_vms()

    for vm in all_vms:
        try:
            if provider.delete_vm(vm.id):
                logger.info(f"✓ Deleted: {vm.name} ({vm.ip_address})")
                deleted += 1
            else:
                logger.error(f"✗ Failed to delete: {vm.name}")
        except Exception as e:
            logger.error(f"✗ Error deleting {vm.name}: {e}")

    return deleted


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    VM Cleanup Utility                        ║
    ║              Indian Kanoon Scraper Project                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Load deployed VMs
    by_provider = load_deployed_vms()

    if not by_provider:
        print("\n✓ No VMs found to cleanup.")
        return

    total_vms = sum(len(vms) for vms in by_provider.values())

    print(f"\nFound {total_vms} deployed VMs:")
    for provider, vms in by_provider.items():
        print(f"  • {provider.capitalize()}: {len(vms)} VMs")

    # Confirm deletion
    if not confirm_deletion(total_vms):
        print("\n❌ Cleanup cancelled.")
        return

    print("\n🗑️  Starting cleanup...")
    print("=" * 70)

    total_deleted = 0

    # Cleanup each provider
    if 'digitalocean' in by_provider:
        deleted = cleanup_digitalocean(by_provider['digitalocean'])
        total_deleted += deleted

    if 'vultr' in by_provider:
        deleted = cleanup_vultr(by_provider['vultr'])
        total_deleted += deleted

    # TODO: Add Linode, Oracle Cloud, etc.

    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  • Total VMs deleted: {total_deleted}/{total_vms}")

    if total_deleted == total_vms:
        print("\n✅ All VMs deleted successfully!")

        # Clean up proxy files
        proxy_list = Path("config/proxy_list.json")
        proxy_txt = Path("config/proxy_list.txt")

        if proxy_list.exists():
            proxy_list.unlink()
            print(f"✓ Removed {proxy_list}")

        if proxy_txt.exists():
            proxy_txt.unlink()
            print(f"✓ Removed {proxy_txt}")

    else:
        print(f"\n⚠️  Some VMs may not have been deleted. Check your cloud provider dashboards.")

    print("\n💡 Tip: Check your cloud provider billing dashboards to confirm no charges.")


if __name__ == "__main__":
    main()
