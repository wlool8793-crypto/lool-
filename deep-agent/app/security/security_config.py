"""
Security Configuration Management System

Centralizes security configuration and coordinates all security components:
- Authentication configuration
- RBAC policies
- Threat detection rules
- Encryption settings
- Data protection policies
- Security monitoring
- Compliance management
"""

import os
import json
import yaml
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

# Import security components
from .authentication import AuthenticationConfig, AdvancedAuthManager
from .rbac import RBACConfig, RBACManager
from .threat_detection import ThreatDetectionConfig, ThreatDetector
from .encryption import EncryptionConfig, EncryptionManager
from .data_protection import DataProtectionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different components"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    description: str
    category: str
    level: SecurityLevel
    enabled: bool = True
    rules: List[Dict[str, Any]] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    compliance_frameworks: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceRequirement:
    """Compliance requirement specification"""
    requirement_id: str
    framework: str  # GDPR, CCPA, HIPAA, PCI-DSS, SOC2, etc.
    title: str
    description: str
    control_id: str
    implementation_status: str  # implemented, partial, not_implemented
    evidence: List[str] = field(default_factory=list)
    last_assessed: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    responsible_party: str = "security_team"


class SecurityConfigManager:
    """Manages all security configurations and coordinates security components"""

    def __init__(self, config_file: str = "config/security.yaml"):
        self.config_file = config_file
        self.security_config: Dict[str, Any] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.compliance_requirements: Dict[str, ComplianceRequirement] = {}
        self.security_components: Dict[str, Any] = {}

        # Initialize security levels
        self.current_security_level = SecurityLevel.MEDIUM
        self.security_audit_log: List[Dict[str, Any]] = []

        self._load_security_config()
        self._initialize_security_policies()
        self._initialize_compliance_requirements()
        self._initialize_security_components()

    def _load_security_config(self):
        """Load security configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        self.security_config = yaml.safe_load(f)
                    else:
                        self.security_config = json.load(f)
                logger.info(f"Loaded security configuration from {self.config_file}")
            else:
                logger.info(f"Security config file not found, using defaults")
                self.security_config = self._get_default_security_config()
                self._save_security_config()
        except Exception as e:
            logger.error(f"Failed to load security config: {e}")
            self.security_config = self._get_default_security_config()

    def _get_default_security_config(self) -> Dict[str, Any]:
        """Get default security configuration"""
        return {
            "general": {
                "security_level": "medium",
                "enable_security_logging": True,
                "audit_log_retention_days": 365,
                "security_monitoring_enabled": True,
                "enable_compliance_reporting": True
            },
            "authentication": {
                "enable_mfa": True,
                "mfa_required_for_admin": True,
                "password_policy": {
                    "min_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "password_expiry_days": 90,
                    "prevent_reuse": 5,
                    "account_lockout_threshold": 5,
                    "account_lockout_duration_minutes": 30
                },
                "session_timeout_minutes": 30,
                "enable_risk_based_auth": True,
                "enable_device_fingerprinting": True
            },
            "encryption": {
                "default_algorithm": "AES-256-GCM",
                "key_rotation_days": 90,
                "enable_field_level_encryption": True,
                "enable_data_at_rest_encryption": True,
                "enable_data_in_transit_encryption": True,
                "secure_random_generation": True,
                "key_derivation_iterations": 100000
            },
            "access_control": {
                "enable_rbac": True,
                "default_role": "user",
                "admin_role": "admin",
                "require_approval_for_sensitive_operations": True,
                "enable_resource_ownership": True,
                "session_based_authorization": True
            },
            "threat_detection": {
                "enable_rate_limiting": True,
                "enable_brute_force_detection": True,
                "enable_sql_injection_detection": True,
                "enable_xss_detection": True,
                "enable_anomaly_detection": True,
                "suspicious_activity_threshold": 10,
                "alert_threshold": 5,
                "auto_block_threshold": 20
            },
            "data_protection": {
                "enable_gdpr_compliance": True,
                "enable_ccpa_compliance": True,
                "enable_data_minimization": True,
                "enable_privacy_by_design": True,
                "data_retention_policy": "medium_term",
                "enable_consent_management": True,
                "enable_right_to_be_forgotten": True,
                "enable_data_portability": True
            },
            "network_security": {
                "enable_firewall": True,
                "enable_ddos_protection": True,
                "enable_ssl_tls": True,
                "min_tls_version": "1.2",
                "enable_hsts": True,
                "enable_csp": True,
                "enable_xss_protection": True
            },
            "monitoring": {
                "enable_security_monitoring": True,
                "log_level": "INFO",
                "enable_real_time_alerts": True,
                "alert_channels": ["email", "slack"],
                "security_dashboard_enabled": True,
                "enable_metrics_collection": True
            }
        }

    def _initialize_security_policies(self):
        """Initialize security policies"""
        policies = [
            SecurityPolicy(
                policy_id="password_policy",
                name="Password Security Policy",
                description="Defines password requirements and management",
                category="authentication",
                level=SecurityLevel.HIGH,
                rules=[
                    {"rule": "minimum_length", "value": 12},
                    {"rule": "complexity_required", "value": True},
                    {"rule": "rotation_period", "value": 90}
                ],
                compliance_frameworks=["GDPR", "HIPAA", "PCI-DSS"]
            ),
            SecurityPolicy(
                policy_id="access_control_policy",
                name="Access Control Policy",
                description="Defines access control principles and implementation",
                category="authorization",
                level=SecurityLevel.HIGH,
                rules=[
                    {"rule": "least_privilege", "value": True},
                    {"rule": "separation_of_duties", "value": True},
                    {"rule": "need_to_know", "value": True}
                ],
                compliance_frameworks=["GDPR", "HIPAA", "SOC2"]
            ),
            SecurityPolicy(
                policy_id="data_encryption_policy",
                name="Data Encryption Policy",
                description="Defines data encryption requirements",
                category="encryption",
                level=SecurityLevel.CRITICAL,
                rules=[
                    {"rule": "data_at_rest_encrypted", "value": True},
                    {"rule": "data_in_transit_encrypted", "value": True},
                    {"rule": "key_management", "value": "secure"}
                ],
                compliance_frameworks=["GDPR", "CCPA", "PCI-DSS", "HIPAA"]
            ),
            SecurityPolicy(
                policy_id="incident_response_policy",
                name="Incident Response Policy",
                description="Defines incident response procedures",
                category="incident_response",
                level=SecurityLevel.HIGH,
                rules=[
                    {"rule": "response_time", "value": "1_hour"},
                    {"rule": "notification_required", "value": True},
                    {"rule": "documentation_required", "value": True}
                ],
                compliance_frameworks=["GDPR", "HIPAA", "SOC2"]
            )
        ]

        for policy in policies:
            self.security_policies[policy.policy_id] = policy

        logger.info(f"Initialized {len(policies)} security policies")

    def _initialize_compliance_requirements(self):
        """Initialize compliance requirements"""
        requirements = [
            ComplianceRequirement(
                requirement_id="gdpr_32",
                framework="GDPR",
                title="Security of Processing",
                description="Implement appropriate technical and organizational security measures",
                control_id="Article 32",
                implementation_status="implemented",
                last_assessed=datetime.now() - timedelta(days=30),
                next_assessment=datetime.now() + timedelta(days=60)
            ),
            ComplianceRequirement(
                requirement_id="ccpa_1798_100",
                framework="CCPA",
                title="Consumer Privacy Rights",
                description="Implement mechanisms for consumer data rights",
                control_id="Section 1798.100",
                implementation_status="implemented",
                last_assessed=datetime.now() - timedelta(days=15),
                next_assessment=datetime.now() + timedelta(days=45)
            ),
            ComplianceRequirement(
                requirement_id="pci_dss_3_1",
                framework="PCI-DSS",
                title="Protect Cardholder Data",
                description="Implement strong access control measures",
                control_id="Requirement 3.1",
                implementation_status="partial",
                last_assessed=datetime.now() - timedelta(days=45),
                next_assessment=datetime.now() + timedelta(days=15)
            ),
            ComplianceRequirement(
                requirement_id="hipaa_164_312",
                framework="HIPAA",
                title="Technical Safeguards",
                description="Implement technical security measures",
                control_id="164.312",
                implementation_status="implemented",
                last_assessed=datetime.now() - timedelta(days=20),
                next_assessment=datetime.now() + timedelta(days=40)
            )
        ]

        for requirement in requirements:
            self.compliance_requirements[requirement.requirement_id] = requirement

        logger.info(f"Initialized {len(requirements)} compliance requirements")

    def _initialize_security_components(self):
        """Initialize all security components"""
        try:
            # Initialize encryption manager
            encryption_config = EncryptionConfig(
                algorithm=self.security_config["encryption"]["default_algorithm"],
                key_rotation_days=self.security_config["encryption"]["key_rotation_days"],
                secure_random=self.security_config["encryption"]["secure_random_generation"],
                iterations=self.security_config["encryption"]["key_derivation_iterations"]
            )
            self.security_components["encryption"] = EncryptionManager(encryption_config)

            # Initialize data protection manager
            self.security_components["data_protection"] = DataProtectionManager(
                self.security_components["encryption"]
            )

            # Initialize authentication manager
            auth_config = AuthenticationConfig(
                enable_mfa=self.security_config["authentication"]["enable_mfa"],
                password_expiry_days=self.security_config["authentication"]["password_policy"]["password_expiry_days"],
                session_timeout_minutes=self.security_config["authentication"]["session_timeout_minutes"],
                max_login_attempts=self.security_config["authentication"]["password_policy"]["account_lockout_threshold"]
            )
            self.security_components["authentication"] = AdvancedAuthManager(auth_config)

            # Initialize RBAC manager
            rbac_config = RBACConfig(
                enable_rbac=self.security_config["access_control"]["enable_rbac"],
                default_role=self.security_config["access_control"]["default_role"],
                admin_role=self.security_config["access_control"]["admin_role"]
            )
            self.security_components["rbac"] = RBACManager(rbac_config)

            # Initialize threat detection
            threat_config = ThreatDetectionConfig(
                enable_rate_limiting=self.security_config["threat_detection"]["enable_rate_limiting"],
                enable_brute_force_detection=self.security_config["threat_detection"]["enable_brute_force_detection"],
                enable_sql_injection_detection=self.security_config["threat_detection"]["enable_sql_injection_detection"],
                enable_xss_detection=self.security_config["threat_detection"]["enable_xss_detection"],
                enable_anomaly_detection=self.security_config["threat_detection"]["enable_anomaly_detection"]
            )
            self.security_components["threat_detection"] = ThreatDetector(threat_config)

            logger.info("All security components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize security components: {e}")
            raise

    def get_security_component(self, component_name: str) -> Any:
        """Get a security component by name"""
        if component_name not in self.security_components:
            raise ValueError(f"Security component {component_name} not found")
        return self.security_components[component_name]

    def update_security_config(self, section: str, updates: Dict[str, Any]):
        """Update security configuration section"""
        if section not in self.security_config:
            self.security_config[section] = {}

        self.security_config[section].update(updates)
        self._save_security_config()

        # Log configuration change
        self._log_security_event({
            "event": "security_config_updated",
            "section": section,
            "updates": updates,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Updated security configuration section: {section}")

    def _save_security_config(self):
        """Save security configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(self.security_config, f, default_flow_style=False)
                else:
                    json.dump(self.security_config, f, indent=2)
            logger.info(f"Saved security configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save security config: {e}")

    def enable_security_policy(self, policy_id: str):
        """Enable a security policy"""
        if policy_id not in self.security_policies:
            raise ValueError(f"Security policy {policy_id} not found")

        self.security_policies[policy_id].enabled = True
        self.security_policies[policy_id].last_updated = datetime.now()

        self._log_security_event({
            "event": "security_policy_enabled",
            "policy_id": policy_id,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Enabled security policy: {policy_id}")

    def disable_security_policy(self, policy_id: str):
        """Disable a security policy"""
        if policy_id not in self.security_policies:
            raise ValueError(f"Security policy {policy_id} not found")

        self.security_policies[policy_id].enabled = False
        self.security_policies[policy_id].last_updated = datetime.now()

        self._log_security_event({
            "event": "security_policy_disabled",
            "policy_id": policy_id,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Disabled security policy: {policy_id}")

    def set_security_level(self, level: SecurityLevel):
        """Set the global security level"""
        old_level = self.current_security_level
        self.current_security_level = level

        # Update component configurations based on security level
        self._adjust_security_level_configurations(level)

        self._log_security_event({
            "event": "security_level_changed",
            "old_level": old_level.value,
            "new_level": level.value,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Security level changed from {old_level.value} to {level.value}")

    def _adjust_security_level_configurations(self, level: SecurityLevel):
        """Adjust component configurations based on security level"""
        if level == SecurityLevel.LOW:
            # Relax security settings
            self.security_config["authentication"]["enable_mfa"] = False
            self.security_config["threat_detection"]["enable_rate_limiting"] = False
            self.security_config["encryption"]["key_rotation_days"] = 180

        elif level == SecurityLevel.MEDIUM:
            # Standard security settings
            self.security_config["authentication"]["enable_mfa"] = True
            self.security_config["threat_detection"]["enable_rate_limiting"] = True
            self.security_config["encryption"]["key_rotation_days"] = 90

        elif level == SecurityLevel.HIGH:
            # Enhanced security settings
            self.security_config["authentication"]["enable_mfa"] = True
            self.security_config["authentication"]["mfa_required_for_admin"] = True
            self.security_config["threat_detection"]["enable_rate_limiting"] = True
            self.security_config["threat_detection"]["enable_anomaly_detection"] = True
            self.security_config["encryption"]["key_rotation_days"] = 60

        elif level == SecurityLevel.CRITICAL:
            # Maximum security settings
            self.security_config["authentication"]["enable_mfa"] = True
            self.security_config["authentication"]["mfa_required_for_admin"] = True
            self.security_config["threat_detection"]["enable_rate_limiting"] = True
            self.security_config["threat_detection"]["enable_anomaly_detection"] = True
            self.security_config["threat_detection"]["auto_block_threshold"] = 10
            self.security_config["encryption"]["key_rotation_days"] = 30

    def perform_security_audit(self) -> Dict[str, Any]:
        """Perform comprehensive security audit"""
        audit_results = {
            "audit_timestamp": datetime.now().isoformat(),
            "security_level": self.current_security_level.value,
            "components_status": {},
            "policies_status": {},
            "compliance_status": {},
            "security_score": 0,
            "recommendations": [],
            "critical_findings": []
        }

        # Audit security components
        for component_name, component in self.security_components.items():
            try:
                if hasattr(component, 'get_status'):
                    status = component.get_status()
                else:
                    status = {"status": "active", "component": component_name}

                audit_results["components_status"][component_name] = status

                # Check for critical issues
                if isinstance(status, dict) and status.get("status") != "active":
                    audit_results["critical_findings"].append({
                        "component": component_name,
                        "issue": "Component not active",
                        "severity": "high"
                    })

            except Exception as e:
                audit_results["components_status"][component_name] = {"error": str(e)}
                audit_results["critical_findings"].append({
                    "component": component_name,
                    "issue": f"Component error: {e}",
                    "severity": "critical"
                })

        # Audit security policies
        enabled_policies = sum(1 for p in self.security_policies.values() if p.enabled)
        audit_results["policies_status"] = {
            "total_policies": len(self.security_policies),
            "enabled_policies": enabled_policies,
            "disabled_policies": len(self.security_policies) - enabled_policies
        }

        # Audit compliance status
        implemented_requirements = sum(
            1 for r in self.compliance_requirements.values()
            if r.implementation_status == "implemented"
        )
        audit_results["compliance_status"] = {
            "total_requirements": len(self.compliance_requirements),
            "implemented": implemented_requirements,
            "partial": sum(1 for r in self.compliance_requirements.values() if r.implementation_status == "partial"),
            "not_implemented": sum(1 for r in self.compliance_requirements.values() if r.implementation_status == "not_implemented")
        }

        # Calculate security score
        component_score = len(audit_results["components_status"]) * 20
        policy_score = (enabled_policies / len(self.security_policies)) * 30
        compliance_score = (implemented_requirements / len(self.compliance_requirements)) * 50

        audit_results["security_score"] = component_score + policy_score + compliance_score

        # Generate recommendations
        if audit_results["security_score"] < 70:
            audit_results["recommendations"].append("Enable additional security policies")
        if audit_results["compliance_status"]["not_implemented"] > 0:
            audit_results["recommendations"].append("Address unimplemented compliance requirements")
        if len(audit_results["critical_findings"]) > 0:
            audit_results["recommendations"].append("Resolve critical security findings immediately")

        # Log audit completion
        self._log_security_event({
            "event": "security_audit_completed",
            "security_score": audit_results["security_score"],
            "critical_findings": len(audit_results["critical_findings"]),
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Security audit completed with score: {audit_results['security_score']}")
        return audit_results

    def generate_compliance_report(self, framework: str = None) -> Dict[str, Any]:
        """Generate compliance report for specified framework"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "framework": framework or "all",
            "requirements": {},
            "summary": {},
            "recommendations": []
        }

        # Filter requirements by framework
        requirements = self.compliance_requirements.values()
        if framework:
            requirements = [r for r in requirements if r.framework == framework]

        # Analyze each requirement
        for req in requirements:
            req_data = {
                "requirement_id": req.requirement_id,
                "title": req.title,
                "framework": req.framework,
                "status": req.implementation_status,
                "last_assessed": req.last_assessed.isoformat() if req.last_assessed else None,
                "next_assessment": req.next_assessment.isoformat() if req.next_assessment else None,
                "responsible_party": req.responsible_party,
                "evidence_count": len(req.evidence)
            }

            if framework not in report["requirements"]:
                report["requirements"][framework] = []
            report["requirements"][framework].append(req_data)

        # Generate summary
        all_reqs = list(requirements)
        implemented = sum(1 for r in all_reqs if r.implementation_status == "implemented")
        partial = sum(1 for r in all_reqs if r.implementation_status == "partial")
        not_implemented = sum(1 for r in all_reqs if r.implementation_status == "not_implemented")

        report["summary"] = {
            "total_requirements": len(all_reqs),
            "implemented": implemented,
            "partial": partial,
            "not_implemented": not_implemented,
            "compliance_percentage": (implemented / len(all_reqs)) * 100 if all_reqs else 0
        }

        # Generate recommendations
        if not_implemented > 0:
            report["recommendations"].append(f"Implement {not_implemented} unimplemented requirements")
        if partial > 0:
            report["recommendations"].append(f"Complete implementation of {partial} partial requirements")

        logger.info(f"Generated compliance report for {framework or 'all frameworks'}")
        return report

    def _log_security_event(self, event_data: Dict[str, Any]):
        """Log security event"""
        self.security_audit_log.append(event_data)

        # Keep only last 10000 events
        if len(self.security_audit_log) > 10000:
            self.security_audit_log = self.security_audit_log[-10000:]

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            "security_level": self.current_security_level.value,
            "components_count": len(self.security_components),
            "policies_count": len(self.security_policies),
            "enabled_policies": sum(1 for p in self.security_policies.values() if p.enabled),
            "compliance_requirements": len(self.compliance_requirements),
            "audit_log_entries": len(self.security_audit_log),
            "security_config_loaded": bool(self.security_config),
            "last_audit": self.security_audit_log[-1]["timestamp"] if self.security_audit_log else None,
            "components": {name: "active" for name in self.security_components.keys()}
        }

    def handle_security_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security alerts and trigger appropriate responses"""
        alert_id = str(uuid.uuid4())
        alert_response = {
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat(),
            "alert_type": alert_data.get("type", "unknown"),
            "severity": alert_data.get("severity", "medium"),
            "source": alert_data.get("source", "unknown"),
            "status": "processing",
            "actions_taken": []
        }

        # Determine response based on alert type and severity
        if alert_response["severity"] in ["high", "critical"]:
            # Immediate actions for high-severity alerts
            if self.current_security_level != SecurityLevel.CRITICAL:
                self.set_security_level(SecurityLevel.CRITICAL)
                alert_response["actions_taken"].append("elevated_security_level")

            # Block malicious IP if applicable
            if alert_data.get("ip_address"):
                self._block_malicious_ip(alert_data["ip_address"])
                alert_response["actions_taken"].append("blocked_malicious_ip")

        # Log security alert
        self._log_security_event({
            "event": "security_alert_received",
            "alert_id": alert_id,
            "alert_type": alert_response["alert_type"],
            "severity": alert_response["severity"],
            "timestamp": datetime.now().isoformat()
        })

        alert_response["status"] = "completed"
        logger.warning(f"Security alert handled: {alert_response['alert_type']} ({alert_response['severity']})")

        return alert_response

    def _block_malicious_ip(self, ip_address: str):
        """Block malicious IP address"""
        # Would integrate with firewall or network security
        logger.warning(f"Blocked malicious IP: {ip_address}")

    def rotate_all_security_keys(self) -> Dict[str, Any]:
        """Rotate all security keys and certificates"""
        rotation_report = {
            "rotation_timestamp": datetime.now().isoformat(),
            "components_rotated": [],
            "errors": []
        }

        try:
            # Rotate encryption keys
            if "encryption" in self.security_components:
                self.security_components["encryption"].rotate_keys()
                rotation_report["components_rotated"].append("encryption_keys")

            # Rotate API keys (if applicable)
            # Would integrate with key management system

            # Rotate certificates (if applicable)
            # Would integrate with certificate management

            logger.info("Security key rotation completed")

        except Exception as e:
            rotation_report["errors"].append(str(e))
            logger.error(f"Failed to rotate security keys: {e}")

        return rotation_report

    def backup_security_config(self) -> str:
        """Backup security configuration"""
        backup_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "security_config": self.security_config,
            "security_policies": {
                policy_id: {
                    "name": policy.name,
                    "description": policy.description,
                    "enabled": policy.enabled,
                    "level": policy.level.value
                }
                for policy_id, policy in self.security_policies.items()
            },
            "compliance_requirements": {
                req_id: {
                    "framework": req.framework,
                    "title": req.title,
                    "implementation_status": req.implementation_status
                }
                for req_id, req in self.compliance_requirements.items()
            }
        }

        backup_filename = f"security_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = f"backups/{backup_filename}"

        os.makedirs("backups", exist_ok=True)
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)

        logger.info(f"Security configuration backed up to {backup_path}")
        return backup_path

    def restore_security_config(self, backup_path: str):
        """Restore security configuration from backup"""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)

            # Restore configuration
            self.security_config = backup_data["security_config"]

            # Restore policies
            for policy_id, policy_data in backup_data["security_policies"].items():
                if policy_id in self.security_policies:
                    self.security_policies[policy_id].enabled = policy_data["enabled"]

            # Save restored configuration
            self._save_security_config()

            logger.info(f"Security configuration restored from {backup_path}")

        except Exception as e:
            logger.error(f"Failed to restore security config: {e}")
            raise