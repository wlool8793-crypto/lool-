"""
DigitalOcean Cloud Provider Implementation
"""

import time
import digitalocean
from typing import List, Optional
from datetime import datetime
from .base import CloudProvider, VMInstance
import logging
import paramiko

logger = logging.getLogger(__name__)


class DigitalOceanProvider(CloudProvider):
    """DigitalOcean implementation"""

    def __init__(self, config):
        super().__init__("digitalocean", config)
        self.client = None
        self.ssh_key_id = None

    def authenticate(self) -> bool:
        """Authenticate with DigitalOcean API"""
        try:
            self.client = digitalocean.Manager(token=self.config.token)
            # Test authentication by listing SSH keys
            self.client.get_all_sshkeys()
            logger.info("DigitalOcean authentication successful")
            return True
        except Exception as e:
            logger.error(f"DigitalOcean authentication failed: {e}")
            return False

    def _upload_ssh_key(self, public_key_path: str) -> bool:
        """Upload SSH key to DigitalOcean"""
        try:
            with open(public_key_path, 'r') as f:
                key_content = f.read().strip()

            key_name = f"scraper-key-{int(time.time())}"
            key = digitalocean.SSHKey(
                token=self.config.token,
                name=key_name,
                public_key=key_content
            )
            key.create()
            self.ssh_key_id = key.id
            logger.info(f"SSH key uploaded: {key_name} (ID: {key.id})")
            return True
        except Exception as e:
            logger.error(f"Failed to upload SSH key: {e}")
            return False

    def deploy_vm(self, name: str, region: str, size: str, ssh_key: str) -> Optional[VMInstance]:
        """Deploy a DigitalOcean droplet"""
        try:
            # Upload SSH key if not already done
            if not self.ssh_key_id:
                if not self._upload_ssh_key(ssh_key):
                    return None

            # Create droplet
            droplet = digitalocean.Droplet(
                token=self.config.token,
                name=name,
                region=region,
                image='ubuntu-20-04-x64',
                size_slug=size,
                ssh_keys=[self.ssh_key_id],
                backups=False,
                tags=['multi-cloud-scraper', 'proxy-server']
            )

            droplet.create()
            logger.info(f"Created droplet: {name} in {region}")

            # Wait for droplet to be active
            if not self.wait_for_vm_ready(droplet.id):
                logger.error(f"Droplet {name} failed to become active")
                return None

            # Refresh to get IP address
            droplet.load()

            vm = VMInstance(
                id=str(droplet.id),
                name=droplet.name,
                ip_address=droplet.ip_address,
                provider="digitalocean",
                region=region,
                status=droplet.status,
                created_at=datetime.now(),
                size=size,
                tags={"purpose": "proxy"}
            )

            self.deployed_vms.append(vm)
            return vm

        except Exception as e:
            logger.error(f"Failed to deploy DigitalOcean VM: {e}")
            return None

    def delete_vm(self, vm_id: str) -> bool:
        """Delete a DigitalOcean droplet"""
        try:
            droplet = digitalocean.Droplet(token=self.config.token, id=int(vm_id))
            droplet.destroy()
            logger.info(f"Deleted droplet: {vm_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete droplet {vm_id}: {e}")
            return False

    def list_vms(self) -> List[VMInstance]:
        """List all droplets"""
        try:
            droplets = self.client.get_all_droplets(tag_name='multi-cloud-scraper')
            vms = []
            for droplet in droplets:
                vm = VMInstance(
                    id=str(droplet.id),
                    name=droplet.name,
                    ip_address=droplet.ip_address,
                    provider="digitalocean",
                    region=droplet.region['slug'],
                    status=droplet.status,
                    created_at=datetime.fromisoformat(droplet.created_at.replace('Z', '+00:00')),
                    size=droplet.size_slug
                )
                vms.append(vm)
            return vms
        except Exception as e:
            logger.error(f"Failed to list droplets: {e}")
            return []

    def get_vm_status(self, vm_id: str) -> Optional[str]:
        """Get droplet status"""
        try:
            droplet = digitalocean.Droplet(token=self.config.token, id=int(vm_id))
            droplet.load()
            return droplet.status
        except Exception as e:
            logger.error(f"Failed to get droplet status: {e}")
            return None

    def wait_for_vm_ready(self, vm_id: str, timeout: int = 300) -> bool:
        """Wait for droplet to be active"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_vm_status(vm_id)
            if status == 'active':
                logger.info(f"Droplet {vm_id} is now active")
                return True
            time.sleep(10)
        logger.error(f"Timeout waiting for droplet {vm_id}")
        return False

    def install_proxy(self, vm: VMInstance, setup_script: str) -> bool:
        """Install Squid proxy on the droplet"""
        try:
            # Wait a bit for SSH to be ready
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
        """Get available DigitalOcean regions"""
        return self.config.regions

    def get_total_cost_estimate(self) -> float:
        """Estimate monthly cost (assuming $5/month per droplet)"""
        return len(self.deployed_vms) * 5.0
