#!/usr/bin/env python3
"""
Multi-Cloud VM Deployment Script for Indian Kanoon Scraper
Deploys VMs across multiple cloud providers and configures them as proxy servers
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import colorlog
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cloud_providers.base import VMInstance
from src.cloud_providers.digitalocean_provider import DigitalOceanProvider
from src.cloud_providers.vultr_provider import VultrProvider

# Load environment variables
load_dotenv()

# Setup colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
    datefmt=None,
    reset=True,
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
logger.setLevel(logging.INFO)


class CloudConfig:
    """Simple configuration for cloud providers"""
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

        if provider_name == "digitalocean":
            self.token = os.getenv('DIGITALOCEAN_TOKEN', '')
            self.vm_count = int(os.getenv('DIGITALOCEAN_VM_COUNT', 15))
            self.vm_size = os.getenv('DIGITALOCEAN_VM_SIZE', 's-1vcpu-1gb')
            self.regions = os.getenv('DIGITALOCEAN_REGIONS', 'nyc1,nyc3,sfo3,sgp1,lon1,fra1,tor1,blr1,ams3').split(',')

        elif provider_name == "vultr":
            self.api_key = os.getenv('VULTR_API_KEY', '')
            self.vm_count = int(os.getenv('VULTR_VM_COUNT', 10))
            self.vm_plan = os.getenv('VULTR_VM_PLAN', 'vc2-1c-1gb')
            self.regions = os.getenv('VULTR_REGIONS', 'ewr,ord,dfw,sea,lax,atl,ams,lhr,sgp,nrt').split(',')

        self.ssh_public_key_path = Path(os.getenv('SSH_PUBLIC_KEY_PATH', Path.home() / '.ssh' / 'id_rsa.pub'))
        self.ssh_private_key_path = Path(os.getenv('SSH_PRIVATE_KEY_PATH', Path.home() / '.ssh' / 'id_rsa'))


class MultiCloudDeployer:
    """Manages VM deployment across multiple cloud providers"""

    def __init__(self):
        self.providers = []
        self.deployed_vms: List[VMInstance] = []
        self.proxy_list_file = Path("config/proxy_list.json")
        self.proxy_txt_file = Path("config/proxy_list.txt")
        self.setup_script = Path("proxy_setup.sh")

        # Ensure config directory exists
        Path("config").mkdir(exist_ok=True)

        # Initialize providers
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize cloud provider instances"""
        logger.info("Initializing cloud providers...")

        # DigitalOcean
        do_config = CloudConfig("digitalocean")
        if do_config.token:
            try:
                do_provider = DigitalOceanProvider(do_config)
                if do_provider.authenticate():
                    self.providers.append(do_provider)
                    logger.info(f"✓ DigitalOcean: {do_config.vm_count} VMs planned")
            except Exception as e:
                logger.error(f"Failed to initialize DigitalOcean: {e}")

        # Vultr
        vultr_config = CloudConfig("vultr")
        if vultr_config.api_key:
            try:
                vultr_provider = VultrProvider(vultr_config)
                if vultr_provider.authenticate():
                    self.providers.append(vultr_provider)
                    logger.info(f"✓ Vultr: {vultr_config.vm_count} VMs planned")
            except Exception as e:
                logger.error(f"Failed to initialize Vultr: {e}")

        if not self.providers:
            logger.error("No cloud providers configured! Please check your .env file.")
            sys.exit(1)

        logger.info(f"Total providers initialized: {len(self.providers)}")

    def deploy_all_vms(self):
        """Deploy VMs across all providers"""
        logger.info("=" * 70)
        logger.info("Starting Multi-Cloud VM Deployment")
        logger.info("=" * 70)

        total_vms = sum(
            p.config.vm_count if hasattr(p.config, 'vm_count')
            else 0 for p in self.providers
        )
        logger.info(f"Total VMs to deploy: {total_vms}")

        all_deployments = []

        # Prepare deployment tasks
        for provider in self.providers:
            regions = provider.get_available_regions()
            vm_count = provider.config.vm_count if hasattr(provider.config, 'vm_count') else 0
            size = (provider.config.vm_size if hasattr(provider.config, 'vm_size')
                   else provider.config.vm_plan)

            # Distribute VMs across regions
            for i in range(vm_count):
                region = regions[i % len(regions)]
                vm_name = f"{provider.name}-proxy-{i+1}"

                all_deployments.append({
                    'provider': provider,
                    'name': vm_name,
                    'region': region,
                    'size': size
                })

        # Deploy VMs in parallel
        deployed_vms = []
        failed_vms = []

        logger.info(f"\nDeploying {len(all_deployments)} VMs in parallel...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_deployment = {
                executor.submit(
                    self._deploy_single_vm,
                    dep['provider'],
                    dep['name'],
                    dep['region'],
                    dep['size']
                ): dep for dep in all_deployments
            }

            with tqdm(total=len(all_deployments), desc="Deploying VMs") as pbar:
                for future in as_completed(future_to_deployment):
                    deployment = future_to_deployment[future]
                    try:
                        vm = future.result()
                        if vm:
                            deployed_vms.append(vm)
                            logger.info(f"✓ Deployed: {vm.name} ({vm.ip_address})")
                        else:
                            failed_vms.append(deployment['name'])
                            logger.error(f"✗ Failed: {deployment['name']}")
                    except Exception as e:
                        failed_vms.append(deployment['name'])
                        logger.error(f"✗ Exception deploying {deployment['name']}: {e}")
                    finally:
                        pbar.update(1)

        self.deployed_vms = deployed_vms

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("Deployment Summary")
        logger.info("=" * 70)
        logger.info(f"Successfully deployed: {len(deployed_vms)}/{total_vms}")
        logger.info(f"Failed: {len(failed_vms)}")

        if failed_vms:
            logger.warning(f"Failed VMs: {', '.join(failed_vms)}")

        return deployed_vms

    def _deploy_single_vm(self, provider, name, region, size):
        """Deploy a single VM"""
        try:
            ssh_key = str(provider.config.ssh_public_key_path)
            vm = provider.deploy_vm(name, region, size, ssh_key)
            return vm
        except Exception as e:
            logger.error(f"Failed to deploy {name}: {e}")
            return None

    def install_proxies(self):
        """Install Squid proxy on all deployed VMs"""
        if not self.deployed_vms:
            logger.error("No VMs deployed to install proxies on")
            return []

        logger.info("\n" + "=" * 70)
        logger.info("Installing Squid Proxies")
        logger.info("=" * 70)

        if not self.setup_script.exists():
            logger.error(f"Proxy setup script not found: {self.setup_script}")
            return []

        successful_proxies = []
        failed_proxies = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_vm = {
                executor.submit(
                    self._install_single_proxy,
                    vm,
                    provider
                ): (vm, provider) for provider in self.providers
                for vm in provider.deployed_vms
            }

            with tqdm(total=len(self.deployed_vms), desc="Installing proxies") as pbar:
                for future in as_completed(future_to_vm):
                    vm, provider = future_to_vm[future]
                    try:
                        success = future.result()
                        if success:
                            successful_proxies.append(vm)
                            logger.info(f"✓ Proxy installed: {vm.ip_address}")
                        else:
                            failed_proxies.append(vm)
                            logger.error(f"✗ Proxy failed: {vm.ip_address}")
                    except Exception as e:
                        failed_proxies.append(vm)
                        logger.error(f"✗ Exception installing proxy on {vm.ip_address}: {e}")
                    finally:
                        pbar.update(1)

        logger.info(f"\nProxies installed: {len(successful_proxies)}/{len(self.deployed_vms)}")

        return successful_proxies

    def _install_single_proxy(self, vm, provider):
        """Install proxy on a single VM"""
        try:
            return provider.install_proxy(vm, str(self.setup_script))
        except Exception as e:
            logger.error(f"Exception installing proxy: {e}")
            return False

    def save_proxy_list(self):
        """Save proxy list to JSON and text files"""
        if not self.deployed_vms:
            logger.warning("No VMs to save")
            return

        # Save to JSON
        proxy_data = {
            "total_proxies": len(self.deployed_vms),
            "providers": {},
            "proxies": []
        }

        for provider in self.providers:
            proxy_data["providers"][provider.name] = {
                "count": len(provider.deployed_vms),
                "cost_estimate": provider.get_total_cost_estimate()
            }

        for vm in self.deployed_vms:
            proxy_data["proxies"].append({
                "provider": vm.provider,
                "ip": vm.ip_address,
                "name": vm.name,
                "region": vm.region,
                "proxy_url": f"http://{vm.ip_address}:3128"
            })

        with open(self.proxy_list_file, 'w') as f:
            json.dump(proxy_data, f, indent=2)

        logger.info(f"✓ Saved proxy list to {self.proxy_list_file}")

        # Save to text file
        with open(self.proxy_txt_file, 'w') as f:
            for vm in self.deployed_vms:
                f.write(f"http://{vm.ip_address}:3128\n")

        logger.info(f"✓ Saved proxy URLs to {self.proxy_txt_file}")

    def print_summary(self):
        """Print deployment summary"""
        logger.info("\n" + "=" * 70)
        logger.info("DEPLOYMENT COMPLETE!")
        logger.info("=" * 70)

        total_cost = sum(p.get_total_cost_estimate() for p in self.providers)

        print(f"\n📊 Summary:")
        print(f"  • Total VMs deployed: {len(self.deployed_vms)}")
        print(f"  • Total proxies: {len(self.deployed_vms)}")
        print(f"  • Estimated monthly cost: ${total_cost:.2f}")
        print(f"\n📁 Files created:")
        print(f"  • {self.proxy_list_file} (detailed JSON)")
        print(f"  • {self.proxy_txt_file} (for scraper)")
        print(f"\n🎯 Next steps:")
        print(f"  1. Test proxies: python test_proxies.py")
        print(f"  2. Start scraping: python bulk_download.py --use-proxies")
        print(f"  3. Monitor progress: python dashboard.py")
        print(f"\n⚠️  Remember to cleanup when done: python cleanup_vms.py")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║       Multi-Cloud Proxy Infrastructure Deployment           ║
    ║              Indian Kanoon Scraper Project                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    deployer = MultiCloudDeployer()

    try:
        # Step 1: Deploy VMs
        deployed_vms = deployer.deploy_all_vms()

        if not deployed_vms:
            logger.error("No VMs deployed successfully. Exiting.")
            sys.exit(1)

        # Step 2: Install proxies
        deployer.install_proxies()

        # Step 3: Save proxy list
        deployer.save_proxy_list()

        # Step 4: Print summary
        deployer.print_summary()

    except KeyboardInterrupt:
        logger.warning("\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
