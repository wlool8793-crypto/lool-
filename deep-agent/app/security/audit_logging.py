"""
Audit Logging and Compliance System

Provides comprehensive audit logging for security and compliance:
- Security event logging
- User activity tracking
- Data access monitoring
- Compliance reporting
- Audit trail management
- Log analysis and alerting
- Regulatory compliance (GDPR, HIPAA, PCI-DSS, SOC2)
"""

import os
import json
import uuid
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path

# Import security components
from .security_config import SecurityConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    USER_AUTHENTICATION = "user_authentication"
    USER_AUTHORIZATION = "user_authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_POLICY_VIOLATION = "security_policy_violation"
    THREAT_DETECTION = "threat_detection"
    SYSTEM_OPERATION = "system_operation"
    API_CALL = "api_call"
    ADMIN_ACTION = "admin_action"
    COMPLIANCE_EVENT = "compliance_event"
    INCIDENT_RESPONSE = "incident_response"
    PRIVACY_VIOLATION = "privacy_violation"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    NIST = "nist"


@dataclass
class AuditEvent:
    """Represents an audit event"""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    outcome: str = "success"  # success, failure, error
    error_message: Optional[str] = None
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    data_classification: Optional[str] = None
    retention_days: int = 365
    is_sensitive: bool = False
    requires_immediate_review: bool = False


@dataclass
class AuditLog:
    """Audit log configuration and management"""
    log_id: str
    name: str
    description: str
    enabled: bool = True
    retention_days: int = 365
    include_sensitive_events: bool = False
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    alert_rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


class AuditLogger:
    """Main audit logging system"""

    def __init__(self, security_config: SecurityConfigManager, log_dir: str = "logs/audit"):
        self.security_config = security_config
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.audit_logs: Dict[str, AuditLog] = {}
        self.audit_events: List[AuditEvent] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.alert_queue: List[Dict[str, Any]] = []
        self.compliance_mappings: Dict[str, List[str]] = {}

        self._initialize_audit_logs()
        self._initialize_compliance_mappings()
        self._start_background_tasks()

    def _initialize_audit_logs(self):
        """Initialize audit log configurations"""
        audit_logs = [
            AuditLog(
                log_id="security_events",
                name="Security Events Log",
                description="Logs all security-related events",
                retention_days=1825,  # 5 years
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.PCI_DSS],
                alert_rules=[
                    {"condition": "failed_logins > 5", "severity": "high", "action": "alert"},
                    {"condition": "suspicious_activity", "severity": "medium", "action": "review"}
                ]
            ),
            AuditLog(
                log_id="data_access",
                name="Data Access Log",
                description="Logs all data access and modification",
                retention_days=2555,  # 7 years
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CCPA, ComplianceFramework.HIPAA],
                include_sensitive_events=True,
                alert_rules=[
                    {"condition": "bulk_data_access", "severity": "medium", "action": "alert"},
                    {"condition": "unauthorized_access", "severity": "high", "action": "alert"}
                ]
            ),
            AuditLog(
                log_id="admin_actions",
                name="Administrative Actions Log",
                description="Logs all administrative actions",
                retention_days=2555,
                compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001],
                alert_rules=[
                    {"condition": "privilege_escalation", "severity": "high", "action": "alert"},
                    {"condition": "config_change", "severity": "medium", "action": "review"}
                ]
            ),
            AuditLog(
                log_id="compliance_events",
                name="Compliance Events Log",
                description="Logs compliance-related events",
                retention_days=3650,  # 10 years
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.PCI_DSS],
                alert_rules=[
                    {"condition": "retention_violation", "severity": "high", "action": "alert"},
                    {"condition": "consent_violation", "severity": "high", "action": "alert"}
                ]
            ),
            AuditLog(
                log_id="system_operations",
                name="System Operations Log",
                description="Logs system-level operations",
                retention_days=365,
                alert_rules=[
                    {"condition": "system_error", "severity": "medium", "action": "review"},
                    {"condition": "performance_degradation", "severity": "low", "action": "monitor"}
                ]
            )
        ]

        for log in audit_logs:
            self.audit_logs[log.log_id] = log

        logger.info(f"Initialized {len(audit_logs)} audit logs")

    def _initialize_compliance_mappings(self):
        """Initialize compliance requirement mappings"""
        self.compliance_mappings = {
            "user_authentication": [
                "gdpr_32", "hipaa_164_312", "pci_dss_8", "soc2_cc6"
            ],
            "data_access": [
                "gdpr_32", "ccpa_1798_100", "hipaa_164_312", "pci_dss_10"
            ],
            "data_modification": [
                "gdpr_32", "hipaa_164_312", "pci_dss_10", "soc2_cc6"
            ],
            "admin_action": [
                "gdpr_32", "hipaa_164_312", "soc2_cc6", "iso27001_a9"
            ],
            "incident_response": [
                "gdpr_33", "hipaa_164_308", "pci_dss_12", "soc2_cc7"
            ],
            "privacy_violation": [
                "gdpr_32", "ccpa_1798_100", "hipaa_164_312"
            ]
        }

    def _start_background_tasks(self):
        """Start background tasks for log management"""
        # Would start thread for log rotation, cleanup, and alert processing
        logger.info("Started audit log background tasks")

    def log_event(self, event_type: AuditEventType, severity: AuditSeverity, action: str,
                  user_id: Optional[str] = None, session_id: Optional[str] = None,
                  resource_type: Optional[str] = None, resource_id: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None, outcome: str = "success",
                  error_message: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None) -> str:
        """Log an audit event"""

        # Determine applicable compliance frameworks
        compliance_frameworks = self._get_applicable_frameworks(event_type.value, resource_type)

        # Determine data classification
        data_classification = self._determine_data_classification(resource_type, details)

        # Determine retention period
        retention_days = self._determine_retention_period(event_type, severity, data_classification)

        # Create audit event
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            severity=severity,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details or {},
            outcome=outcome,
            error_message=error_message,
            compliance_frameworks=compliance_frameworks,
            data_classification=data_classification,
            retention_days=retention_days,
            is_sensitive=severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL],
            requires_immediate_review=severity == AuditSeverity.CRITICAL
        )

        # Store event
        self.audit_events.append(event)

        # Write to appropriate log files
        self._write_to_log_files(event)

        # Process alerts
        self._process_alerts(event)

        # Update session tracking
        if session_id:
            self._update_session_tracking(session_id, event)

        logger.debug(f"Logged audit event: {event.event_type.value} - {action}")

        return event.event_id

    def _get_applicable_frameworks(self, event_type: str, resource_type: Optional[str]) -> List[ComplianceFramework]:
        """Determine applicable compliance frameworks"""
        frameworks = []

        # Map event types to compliance requirements
        for event_key, requirements in self.compliance_mappings.items():
            if event_key in event_type.lower():
                for req in requirements:
                    if req.startswith("gdpr"):
                        frameworks.append(ComplianceFramework.GDPR)
                    elif req.startswith("ccpa"):
                        frameworks.append(ComplianceFramework.CCPA)
                    elif req.startswith("hipaa"):
                        frameworks.append(ComplianceFramework.HIPAA)
                    elif req.startswith("pci"):
                        frameworks.append(ComplianceFramework.PCI_DSS)
                    elif req.startswith("soc2"):
                        frameworks.append(ComplianceFramework.SOC2)
                    elif req.startswith("iso"):
                        frameworks.append(ComplianceFramework.ISO27001)

        # Remove duplicates
        return list(set(frameworks))

    def _determine_data_classification(self, resource_type: Optional[str], details: Dict[str, Any]) -> Optional[str]:
        """Determine data classification for the event"""
        if not resource_type:
            return None

        sensitive_resources = [
            "user_profile", "payment_info", "medical_records", "ssn",
            "credit_card", "bank_account", "api_keys", "admin_config"
        ]

        if any(sensitive in resource_type.lower() for sensitive in sensitive_resources):
            return "sensitive"

        confidential_resources = [
            "user_data", "personal_info", "contact_info", "session_data"
        ]

        if any(confidential in resource_type.lower() for confidential in confidential_resources):
            return "confidential"

        return "internal"

    def _determine_retention_period(self, event_type: AuditEventType, severity: AuditSeverity,
                                  data_classification: Optional[str]) -> int:
        """Determine retention period for audit event"""
        # Critical events: 10 years
        if severity == AuditSeverity.CRITICAL:
            return 3650

        # Sensitive data: 7 years
        if data_classification == "sensitive":
            return 2555

        # Security events: 5 years
        if event_type in [AuditEventType.SECURITY_POLICY_VIOLATION, AuditEventType.THREAT_DETECTION]:
            return 1825

        # Compliance events: 7 years
        if event_type == AuditEventType.COMPLIANCE_EVENT:
            return 2555

        # Default: 1 year
        return 365

    def _write_to_log_files(self, event: AuditEvent):
        """Write event to appropriate log files"""
        timestamp = event.timestamp.strftime("%Y-%m-%d")
        event_data = self._serialize_event(event)

        # Write to general audit log
        general_log_file = self.log_dir / f"audit_{timestamp}.log"
        with open(general_log_file, 'a') as f:
            f.write(json.dumps(event_data) + '\n')

        # Write to specific log files based on event type
        if event.event_type in [AuditEventType.USER_AUTHENTICATION, AuditEventType.USER_AUTHORIZATION]:
            auth_log_file = self.log_dir / f"auth_{timestamp}.log"
            with open(auth_log_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')

        elif event.event_type in [AuditEventType.DATA_ACCESS, AuditEventType.DATA_MODIFICATION, AuditEventType.DATA_DELETION]:
            data_log_file = self.log_dir / f"data_{timestamp}.log"
            with open(data_log_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')

        elif event.event_type == AuditEventType.ADMIN_ACTION:
            admin_log_file = self.log_dir / f"admin_{timestamp}.log"
            with open(admin_log_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')

        elif event.event_type == AuditEventType.THREAT_DETECTION:
            threat_log_file = self.log_dir / f"threat_{timestamp}.log"
            with open(threat_log_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')

    def _serialize_event(self, event: AuditEvent) -> Dict[str, Any]:
        """Serialize audit event for storage"""
        event_dict = asdict(event)
        event_dict['timestamp'] = event.timestamp.isoformat()
        event_dict['event_type'] = event.event_type.value
        event_dict['severity'] = event.severity.value
        event_dict['compliance_frameworks'] = [f.value for f in event.compliance_frameworks]
        return event_dict

    def _process_alerts(self, event: AuditEvent):
        """Process alerts for the event"""
        for log_config in self.audit_logs.values():
            if not log_config.enabled:
                continue

            for alert_rule in log_config.alert_rules:
                if self._should_trigger_alert(event, alert_rule):
                    alert = {
                        "alert_id": str(uuid.uuid4()),
                        "event_id": event.event_id,
                        "rule": alert_rule,
                        "timestamp": datetime.now().isoformat(),
                        "severity": alert_rule.get("severity", "medium"),
                        "action": alert_rule.get("action", "alert"),
                        "event": self._serialize_event(event)
                    }
                    self.alert_queue.append(alert)
                    logger.warning(f"Alert triggered: {alert_rule['condition']}")

    def _should_trigger_alert(self, event: AuditEvent, alert_rule: Dict[str, Any]) -> bool:
        """Check if alert should be triggered"""
        condition = alert_rule.get("condition", "")

        # Failed login attempts
        if "failed_logins" in condition:
            if (event.event_type == AuditEventType.USER_AUTHENTICATION and
                event.outcome == "failure" and event.user_id):
                return self._count_recent_failures(event.user_id) > 5

        # Suspicious activity
        if "suspicious_activity" in condition:
            return event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]

        # Bulk data access
        if "bulk_data_access" in condition:
            return (event.event_type == AuditEventType.DATA_ACCESS and
                    event.details.get("record_count", 0) > 1000)

        # Unauthorized access
        if "unauthorized_access" in condition:
            return event.outcome == "failure" and event.severity == AuditSeverity.HIGH

        # Privilege escalation
        if "privilege_escalation" in condition:
            return (event.event_type == AuditEventType.ADMIN_ACTION and
                    "privilege" in event.action.lower())

        # Configuration change
        if "config_change" in condition:
            return event.event_type == AuditEventType.CONFIGURATION_CHANGE

        # System error
        if "system_error" in condition:
            return event.outcome == "error"

        return False

    def _count_recent_failures(self, user_id: str) -> int:
        """Count recent authentication failures for user"""
        cutoff_time = datetime.now() - timedelta(minutes=15)
        failures = [
            event for event in self.audit_events
            if (event.user_id == user_id and
                event.event_type == AuditEventType.USER_AUTHENTICATION and
                event.outcome == "failure" and
                event.timestamp > cutoff_time)
        ]
        return len(failures)

    def _update_session_tracking(self, session_id: str, event: AuditEvent):
        """Update session tracking information"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "user_id": event.user_id,
                "start_time": event.timestamp,
                "last_activity": event.timestamp,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "event_count": 0,
                "actions": []
            }

        session = self.active_sessions[session_id]
        session["last_activity"] = event.timestamp
        session["event_count"] += 1
        session["actions"].append({
            "timestamp": event.timestamp.isoformat(),
            "action": event.action,
            "resource_type": event.resource_type,
            "outcome": event.outcome
        })

    def query_audit_logs(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query audit logs with filters"""
        filtered_events = []

        for event in self.audit_events:
            if self._event_matches_filters(event, filters):
                filtered_events.append(self._serialize_event(event))

        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)

        # Apply limit
        limit = filters.get("limit", 100)
        return filtered_events[:limit]

    def _event_matches_filters(self, event: AuditEvent, filters: Dict[str, Any]) -> bool:
        """Check if event matches query filters"""
        # Time range filter
        if "start_time" in filters:
            start_time = datetime.fromisoformat(filters["start_time"])
            if event.timestamp < start_time:
                return False

        if "end_time" in filters:
            end_time = datetime.fromisoformat(filters["end_time"])
            if event.timestamp > end_time:
                return False

        # User filter
        if "user_id" in filters and event.user_id != filters["user_id"]:
            return False

        # Event type filter
        if "event_type" in filters:
            if isinstance(filters["event_type"], str):
                if event.event_type.value != filters["event_type"]:
                    return False
            else:  # List of types
                if event.event_type.value not in filters["event_type"]:
                    return False

        # Severity filter
        if "severity" in filters and event.severity.value != filters["severity"]:
            return False

        # Resource type filter
        if "resource_type" in filters and event.resource_type != filters["resource_type"]:
            return False

        # Outcome filter
        if "outcome" in filters and event.outcome != filters["outcome"]:
            return False

        # IP address filter
        if "ip_address" in filters and event.ip_address != filters["ip_address"]:
            return False

        return True

    def generate_compliance_report(self, framework: ComplianceFramework,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate compliance report for specified framework"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()

        # Filter events by compliance framework and time range
        relevant_events = [
            event for event in self.audit_events
            if (framework in event.compliance_frameworks and
                start_date <= event.timestamp <= end_date)
        ]

        # Analyze events by type
        event_counts = {}
        for event in relevant_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Identify compliance issues
        compliance_issues = []
        for event in relevant_events:
            if event.outcome == "failure" or event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                compliance_issues.append({
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "user_id": event.user_id,
                    "issue": event.error_message or "Policy violation"
                })

        # Calculate compliance score
        total_events = len(relevant_events)
        failed_events = len([e for e in relevant_events if e.outcome == "failure"])
        compliance_score = ((total_events - failed_events) / total_events * 100) if total_events > 0 else 100

        report = {
            "framework": framework.value,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_events": total_events,
            "event_counts": event_counts,
            "compliance_issues": compliance_issues,
            "compliance_score": round(compliance_score, 2),
            "generated_at": datetime.now().isoformat(),
            "recommendations": self._generate_compliance_recommendations(compliance_issues, framework)
        }

        logger.info(f"Generated compliance report for {framework.value}")
        return report

    def _generate_compliance_recommendations(self, issues: List[Dict[str, Any]], framework: ComplianceFramework) -> List[str]:
        """Generate compliance recommendations based on issues"""
        recommendations = []

        if not issues:
            recommendations.append("No compliance issues detected. Maintain current security posture.")
            return recommendations

        # Analyze issue patterns
        issue_types = [issue["event_type"] for issue in issues]
        severity_counts = {}
        for issue in issues:
            severity = issue["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Generate recommendations based on framework and issues
        if framework == ComplianceFramework.GDPR:
            if "data_access" in issue_types:
                recommendations.append("Review data access controls and implement stricter authorization")
            if "privacy_violation" in issue_types:
                recommendations.append("Enhance privacy controls and review data processing activities")

        elif framework == ComplianceFramework.HIPAA:
            if "data_access" in issue_types:
                recommendations.append("Implement stricter access controls for protected health information")
            if any("medical" in issue.get("issue", "") for issue in issues):
                recommendations.append("Review medical data handling procedures")

        elif framework == ComplianceFramework.PCI_DSS:
            if "data_access" in issue_types and any("card" in issue.get("issue", "") for issue in issues):
                recommendations.append("Review credit card data handling and implement tokenization")
            recommendations.append("Conduct quarterly PCI DSS compliance review")

        # General recommendations based on severity
        if severity_counts.get("critical", 0) > 0:
            recommendations.append("Address critical security issues immediately")
        if severity_counts.get("high", 0) > 5:
            recommendations.append("Implement enhanced monitoring and alerting")

        return recommendations

    def rotate_logs(self):
        """Rotate audit logs based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=365)  # Default 1 year

        # Remove expired events from memory
        self.audit_events = [
            event for event in self.audit_events
            if event.timestamp > cutoff_date
        ]

        # Archive old log files
        for log_file in self.log_dir.glob("*.log"):
            file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_date < cutoff_date:
                archive_file = self.log_dir / "archive" / log_file.name
                archive_file.parent.mkdir(exist_ok=True)
                log_file.rename(archive_file)

        logger.info("Audit log rotation completed")

    def export_audit_data(self, format_type: str = "json", filters: Optional[Dict[str, Any]] = None) -> str:
        """Export audit data in specified format"""
        events = self.query_audit_logs(filters or {})

        if format_type.lower() == "json":
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_events": len(events),
                "events": events
            }
            return json.dumps(export_data, indent=2)

        elif format_type.lower() == "csv":
            # Generate CSV format
            import csv
            import io

            output = io.StringIO()
            if events:
                fieldnames = events[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(events)

            return output.getvalue()

        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def get_audit_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics for specified time period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_events = [
            event for event in self.audit_events
            if event.timestamp > cutoff_date
        ]

        # Basic statistics
        total_events = len(recent_events)
        unique_users = len(set(event.user_id for event in recent_events if event.user_id))

        # Event type distribution
        event_types = {}
        for event in recent_events:
            event_type = event.event_type.value
            event_types[event_type] = event_types.get(event_type, 0) + 1

        # Severity distribution
        severity_dist = {}
        for event in recent_events:
            severity = event.severity.value
            severity_dist[severity] = severity_dist.get(severity, 0) + 1

        # Outcome distribution
        outcome_dist = {}
        for event in recent_events:
            outcome = event.outcome
            outcome_dist[outcome] = outcome_dist.get(outcome, 0) + 1

        # Top users by activity
        user_activity = {}
        for event in recent_events:
            if event.user_id:
                user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1

        top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]

        # Alert statistics
        recent_alerts = [alert for alert in self.alert_queue if
                        datetime.fromisoformat(alert["timestamp"]) > cutoff_date]

        return {
            "period_days": days,
            "total_events": total_events,
            "unique_users": unique_users,
            "event_types": event_types,
            "severity_distribution": severity_dist,
            "outcome_distribution": outcome_dist,
            "top_active_users": top_users,
            "total_alerts": len(recent_alerts),
            "active_sessions": len(self.active_sessions),
            "generated_at": datetime.now().isoformat()
        }

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old session tracking data"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        old_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session["last_activity"] < cutoff_time
        ]

        for session_id in old_sessions:
            del self.active_sessions[session_id]

        logger.info(f"Cleaned up {len(old_sessions)} old sessions")

    def get_pending_alerts(self) -> List[Dict[str, Any]]:
        """Get pending security alerts"""
        return self.alert_queue.copy()

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str, notes: str = ""):
        """Acknowledge a security alert"""
        for i, alert in enumerate(self.alert_queue):
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_by"] = acknowledged_by
                alert["acknowledged_at"] = datetime.now().isoformat()
                alert["notes"] = notes
                logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                break