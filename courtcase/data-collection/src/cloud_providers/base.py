"""
Base Cloud Provider Interface
Defines the common interface for all cloud providers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class VMInstance:
    """Represents a deployed VM instance"""
    id: str
    name: str
    ip_address: str
    provider: str
    region: str
    status: str
    created_at: datetime
    size: str
    tags: Dict[str, str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "ip_address": self.ip_address,
            "provider": self.provider,
            "region": self.region,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "size": self.size,
            "tags": self.tags or {}
        }

    def to_proxy_format(self, port: int = 3128) -> str:
        """Convert to proxy URL format"""
        return f"http://{self.ip_address}:{port}"


class CloudProvider(ABC):
    """Abstract base class for cloud providers"""

    def __init__(self, name: str, config: object):
        self.name = name
        self.config = config
        self.deployed_vms: List[VMInstance] = []

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the cloud provider
        Returns: True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def deploy_vm(self, name: str, region: str, size: str, ssh_key: str) -> Optional[VMInstance]:
        """
        Deploy a single VM instance
        Args:
            name: Name for the VM
            region: Region to deploy in
            size: VM size/type
            ssh_key: SSH public key for access
        Returns:
            VMInstance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_vm(self, vm_id: str) -> bool:
        """
        Delete a VM instance
        Args:
            vm_id: ID of the VM to delete
        Returns:
            True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    def list_vms(self) -> List[VMInstance]:
        """
        List all VMs for this provider
        Returns:
            List of VMInstance objects
        """
        pass

    @abstractmethod
    def get_vm_status(self, vm_id: str) -> Optional[str]:
        """
        Get current status of a VM
        Args:
            vm_id: ID of the VM
        Returns:
            Status string or None if not found
        """
        pass

    @abstractmethod
    def wait_for_vm_ready(self, vm_id: str, timeout: int = 300) -> bool:
        """
        Wait for VM to be in running state
        Args:
            vm_id: ID of the VM
            timeout: Maximum seconds to wait
        Returns:
            True if VM is ready, False if timeout
        """
        pass

    @abstractmethod
    def install_proxy(self, vm: VMInstance, setup_script: str) -> bool:
        """
        Install and configure Squid proxy on the VM
        Args:
            vm: VMInstance object
            setup_script: Path to proxy setup script
        Returns:
            True if installation successful, False otherwise
        """
        pass

    def get_available_regions(self) -> List[str]:
        """
        Get list of available regions for this provider
        Returns:
            List of region codes
        """
        return []

    def get_deployed_count(self) -> int:
        """
        Get number of deployed VMs
        Returns:
            Number of VMs deployed
        """
        return len(self.deployed_vms)

    def get_total_cost_estimate(self) -> float:
        """
        Estimate total monthly cost for deployed VMs
        Returns:
            Estimated cost in USD
        """
        # Override in subclass with provider-specific pricing
        return 0.0

    def cleanup_all(self) -> int:
        """
        Delete all VMs deployed by this provider
        Returns:
            Number of VMs successfully deleted
        """
        deleted_count = 0
        for vm in self.deployed_vms.copy():
            if self.delete_vm(vm.id):
                deleted_count += 1
                self.deployed_vms.remove(vm)
        return deleted_count
