"""
Vultr Cloud Provider Implementation
"""

import time
import requests
from typing import List, Optional
from datetime import datetime
from .base import CloudProvider, VMInstance
import logging
import paramiko

logger = logging.getLogger(__name__)


class VultrProvider(CloudProvider):
    """Vultr implementation"""

    def __init__(self, config):
        super().__init__("vultr", config)
        self.api_url = "https://api.vultr.com/v2"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        self.ssh_key_id = None

    def authenticate(self) -> bool:
        """Authenticate with Vultr API"""
        try:
            response = requests.get(
                f"{self.api_url}/account",
                headers=self.headers
            )
            if response.status_code == 200:
                logger.info("Vultr authentication successful")
                return True
            else:
                logger.error(f"Vultr authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Vultr authentication failed: {e}")
            return False

    def _upload_ssh_key(self, public_key_path: str) -> bool:
        """Upload SSH key to Vultr"""
        try:
            with open(public_key_path, 'r') as f:
                key_content = f.read().strip()

            key_name = f"scraper-key-{int(time.time())}"
            payload = {
                "name": key_name,
                "ssh_key": key_content
            }

            response = requests.post(
                f"{self.api_url}/ssh-keys",
                headers=self.headers,
                json=payload
            )

            if response.status_code == 201:
                self.ssh_key_id = response.json()['ssh_key']['id']
                logger.info(f"SSH key uploaded to Vultr: {key_name}")
                return True
            else:
                logger.error(f"Failed to upload SSH key: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Failed to upload SSH key: {e}")
            return False

    def deploy_vm(self, name: str, region: str, size: str, ssh_key: str) -> Optional[VMInstance]:
        """Deploy a Vultr instance"""
        try:
            # Upload SSH key if not already done
            if not self.ssh_key_id:
                if not self._upload_ssh_key(ssh_key):
                    return None

            # Get plan and region info
            plan_id = self._get_plan_id(size)
            region_id = region

            if not plan_id:
                logger.error(f"Invalid plan: {size}")
                return None

            # Create instance payload
            payload = {
                "region": region_id,
                "plan": plan_id,
                "label": name,
                "os_id": 387,  # Ubuntu 20.04 LTS x64
                "sshkey_id": [self.ssh_key_id],
                "backups": "disabled",
                "enable_ipv6": False,
                "tags": ["multi-cloud-scraper", "proxy-server"]
            }

            response = requests.post(
                f"{self.api_url}/instances",
                headers=self.headers,
                json=payload
            )

            if response.status_code != 202:
                logger.error(f"Failed to create instance: {response.text}")
                return None

            instance_data = response.json()['instance']
            instance_id = instance_data['id']
            logger.info(f"Created Vultr instance: {name} in {region}")

            # Wait for instance to be active
            if not self.wait_for_vm_ready(instance_id):
                logger.error(f"Instance {name} failed to become active")
                return None

            # Get instance details to retrieve IP
            instance_info = self._get_instance_info(instance_id)
            if not instance_info:
                return None

            vm = VMInstance(
                id=instance_id,
                name=name,
                ip_address=instance_info['main_ip'],
                provider="vultr",
                region=region,
                status=instance_info['status'],
                created_at=datetime.now(),
                size=size,
                tags={"purpose": "proxy"}
            )

            self.deployed_vms.append(vm)
            return vm

        except Exception as e:
            logger.error(f"Failed to deploy Vultr VM: {e}")
            return None

    def _get_plan_id(self, size: str) -> Optional[str]:
        """Get Vultr plan ID"""
        # Map common plan names to IDs
        plan_map = {
            "vc2-1c-1gb": "vc2-1c-1gb",
            "vc2-1c-2gb": "vc2-1c-2gb",
            "vc2-2c-4gb": "vc2-2c-4gb"
        }
        return plan_map.get(size, size)

    def _get_instance_info(self, instance_id: str) -> Optional[dict]:
        """Get instance information"""
        try:
            response = requests.get(
                f"{self.api_url}/instances/{instance_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()['instance']
            return None
        except Exception as e:
            logger.error(f"Failed to get instance info: {e}")
            return None

    def delete_vm(self, vm_id: str) -> bool:
        """Delete a Vultr instance"""
        try:
            response = requests.delete(
                f"{self.api_url}/instances/{vm_id}",
                headers=self.headers
            )
            if response.status_code == 204:
                logger.info(f"Deleted Vultr instance: {vm_id}")
                return True
            else:
                logger.error(f"Failed to delete instance: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete instance {vm_id}: {e}")
            return False

    def list_vms(self) -> List[VMInstance]:
        """List all Vultr instances"""
        try:
            response = requests.get(
                f"{self.api_url}/instances",
                headers=self.headers
            )

            if response.status_code != 200:
                return []

            instances = response.json().get('instances', [])
            vms = []

            for instance in instances:
                if 'multi-cloud-scraper' in instance.get('tags', []):
                    vm = VMInstance(
                        id=instance['id'],
                        name=instance['label'],
                        ip_address=instance['main_ip'],
                        provider="vultr",
                        region=instance['region'],
                        status=instance['status'],
                        created_at=datetime.fromisoformat(instance['date_created']),
                        size=instance['plan']
                    )
                    vms.append(vm)

            return vms
        except Exception as e:
            logger.error(f"Failed to list Vultr instances: {e}")
            return []

    def get_vm_status(self, vm_id: str) -> Optional[str]:
        """Get instance status"""
        instance_info = self._get_instance_info(vm_id)
        return instance_info['status'] if instance_info else None

    def wait_for_vm_ready(self, vm_id: str, timeout: int = 300) -> bool:
        """Wait for instance to be active"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_vm_status(vm_id)
            if status == 'active':
                logger.info(f"Vultr instance {vm_id} is now active")
                # Wait additional time for SSH to be ready
                time.sleep(30)
                return True
            time.sleep(10)
        logger.error(f"Timeout waiting for instance {vm_id}")
        return False

    def install_proxy(self, vm: VMInstance, setup_script: str) -> bool:
        """Install Squid proxy on the instance"""
        try:
            # Wait for SSH to be ready
            time.sleep(30)

            # Read setup script
            with open(setup_script, 'r') as f:
                script_content = f.read()

            # Connect via SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Try connecting with retries
            for attempt in range(5):
                try:
                    ssh.connect(
                        vm.ip_address,
                        username='root',
                        key_filename=str(self.config.ssh_private_key_path),
                        timeout=30
                    )
                    break
                except Exception as e:
                    if attempt < 4:
                        logger.warning(f"SSH connection attempt {attempt + 1} failed, retrying...")
                        time.sleep(10)
                    else:
                        raise e

            # Upload and execute setup script
            sftp = ssh.open_sftp()
            sftp.put(setup_script, '/root/proxy_setup.sh')
            sftp.close()

            stdin, stdout, stderr = ssh.exec_command('bash /root/proxy_setup.sh')
            exit_status = stdout.channel.recv_exit_status()

            ssh.close()

            if exit_status == 0:
                logger.info(f"Proxy installed successfully on {vm.ip_address}")
                return True
            else:
                logger.error(f"Proxy installation failed on {vm.ip_address}")
                return False

        except Exception as e:
            logger.error(f"Failed to install proxy on {vm.ip_address}: {e}")
            return False

    def get_available_regions(self) -> List[str]:
        """Get available Vultr regions"""
        return self.config.regions

    def get_total_cost_estimate(self) -> float:
        """Estimate monthly cost (assuming $5-6/month per instance)"""
        return len(self.deployed_vms) * 6.0
