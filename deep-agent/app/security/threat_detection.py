"""
Security Monitoring and Threat Detection System for LangGraph Deep Web Agent

This module provides comprehensive security monitoring, threat detection,
anomaly detection, and incident response capabilities.
"""

import asyncio
import json
import logging
import re
import ipaddress
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncpg
import redis.asyncio as redis
from collections import defaultdict, deque
import statistics

from app.core.config import settings
from app.database.redis import RedisManager
from app.security.authentication import RiskLevel, SecurityContext
from app.integrations.api_monitoring import APIMonitor

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    BRUTE_FORCE = "brute_force"
    DDOS_ATTACK = "ddos_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    MALICIOUS_USER_AGENT = "malicious_user_agent"
    SUSPICIOUS_IP = "suspicious_ip"
    IMPOSSIBLE_TRAVEL = "impossible_travel"
    ACCOUNT_TAKEOVER = "account_takeover"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_DETECTION = "malware_detection"
    PHISHING_ATTEMPT = "phishing_attempt"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class SecurityEvent:
    """Security event record"""
    id: str
    event_type: str
    user_id: str
    ip_address: str
    user_agent: str
    resource: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThreatAlert:
    """Threat detection alert"""
    id: str
    threat_type: ThreatType
    severity: AlertSeverity
    title: str
    description: str
    affected_resources: List[str]
    detection_time: datetime = field(default_factory=datetime.now)
    source_events: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: IncidentStatus = IncidentStatus.OPEN

@dataclass
class SecurityIncident:
    """Security incident record"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: IncidentStatus
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    assigned_to: str = ""
    affected_users: List[str] = field(default_factory=list)
    affected_resources: List[str] = field(default_factory=list)
    detection_method: str = ""
    mitigation_steps: List[str] = field(default_factory=list)
    related_alerts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BaselineMetric:
    """Security baseline metric"""
    metric_name: str
    baseline_value: float
    standard_deviation: float
    last_updated: datetime = field(default_factory=datetime.now)
    sample_size: int = 0

class ThreatDetector:
    """Threat detection and security monitoring system"""

    def __init__(self):
        self.redis_manager = RedisManager()
        self.api_monitor = APIMonitor()

        # Detection rules
        self.detection_rules = self._initialize_detection_rules()

        # Baseline metrics
        self.baselines = self._initialize_baselines()

        # Active threats
        self.active_threats = {}

        # Incident response
        self.incidents = {}

        # Rate limiting and anomaly detection
        self.event_counters = defaultdict(int)
        self.ip_reputation = {}
        self.user_behavior = defaultdict(lambda: deque(maxlen=100))

        # Malicious patterns
        self.malicious_patterns = self._initialize_malicious_patterns()

        # Monitoring workers
        self._monitoring_workers = {}
        self._detection_worker_running = False

        # Threat intelligence feeds
        self.threat_feeds = {}
        self._initialize_threat_feeds()

    def _initialize_detection_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize threat detection rules"""
        return {
            "brute_force": {
                "name": "Brute Force Attack",
                "description": "Multiple failed login attempts from same IP",
                "threshold": 5,
                "time_window": 300,  # 5 minutes
                "severity": AlertSeverity.HIGH,
                "conditions": {
                    "event_type": ["login_failed"],
                    "same_ip": True,
                    "count": 5
                }
            },
            "ddos_attack": {
                "name": "DDoS Attack",
                "description": "High volume of requests from single IP",
                "threshold": 1000,
                "time_window": 60,  # 1 minute
                "severity": AlertSeverity.CRITICAL,
                "conditions": {
                    "event_type": ["api_request"],
                    "same_ip": True,
                    "count": 1000
                }
            },
            "sql_injection": {
                "name": "SQL Injection Attempt",
                "description": "SQL injection patterns detected in request",
                "threshold": 1,
                "time_window": 1,
                "severity": AlertSeverity.HIGH,
                "conditions": {
                    "pattern_match": ["sql_injection_patterns"]
                }
            },
            "xss_attack": {
                "name": "XSS Attack Attempt",
                "description": "Cross-site scripting patterns detected",
                "threshold": 1,
                "time_window": 1,
                "severity": AlertSeverity.HIGH,
                "conditions": {
                    "pattern_match": ["xss_patterns"]
                }
            },
            "impossible_travel": {
                "name": "Impossible Travel",
                "description": "User login from geographically impossible locations",
                "threshold": 1,
                "time_window": 3600,  # 1 hour
                "severity": AlertSeverity.CRITICAL,
                "conditions": {
                    "geographic_analysis": True
                }
            },
            "account_takeover": {
                "name": "Account Takeover",
                "description": "Suspicious account activity indicating takeover",
                "threshold": 3,
                "time_window": 1800,  # 30 minutes
                "severity": AlertSeverity.CRITICAL,
                "conditions": {
                    "behavior_anomaly": True,
                    "risk_factors": ["new_device", "new_location", "impossible_travel"]
                }
            },
            "data_exfiltration": {
                "name": "Data Exfiltration",
                "description": "Large volume of data access/transfer indicating exfiltration",
                "threshold": 10000,  # 10MB
                "time_window": 3600,  # 1 hour
                "severity": AlertSeverity.CRITICAL,
                "conditions": {
                    "data_volume": True,
                    "unusual_pattern": True
                }
            },
            "rate_limit_violation": {
                "name": "Rate Limit Violation",
                "description": "API rate limit exceeded",
                "threshold": 100,
                "time_window": 60,  # 1 minute
                "severity": AlertSeverity.MEDIUM,
                "conditions": {
                    "rate_limit": True
                }
            }
        }

    def _initialize_baselines(self) -> Dict[str, BaselineMetric]:
        """Initialize security baseline metrics"""
        return {
            "login_attempts_per_hour": BaselineMetric(
                metric_name="login_attempts_per_hour",
                baseline_value=10.0,
                standard_deviation=5.0,
                sample_size=1000
            ),
            "api_requests_per_minute": BaselineMetric(
                metric_name="api_requests_per_minute",
                baseline_value=100.0,
                standard_deviation=50.0,
                sample_size=10000
            ),
            "data_transfer_per_hour": BaselineMetric(
                metric_name="data_transfer_per_hour",
                baseline_value=100.0,  # MB
                standard_deviation=50.0,
                sample_size=1000
            ),
            "failed_login_rate": BaselineMetric(
                metric_name="failed_login_rate",
                baseline_value=0.05,  # 5%
                standard_deviation=0.02,
                sample_size=5000
            ),
            "session_duration": BaselineMetric(
                metric_name="session_duration",
                baseline_value=1800.0,  # 30 minutes
                standard_deviation=600.0,
                sample_size=2000
            )
        }

    def _initialize_malicious_patterns(self) -> Dict[str, List[str]]:
        """Initialize malicious pattern detection"""
        return {
            "sql_injection_patterns": [
                r"(?i)\bunion\b.*\bselect\b",
                r"(?i)\bselect\b.*\bfrom\b.*\bwhere\b",
                r"(?i)\bdrop\b.*\btable\b",
                r"(?i)\binsert\b.*\binto\b",
                r"(?i)\bupdate\b.*\bset\b",
                r"(?i)\bdelete\b.*\bfrom\b",
                r"(?i)\bexec\b",
                r"(?i)\bxp_cmdshell\b",
                r"(?i)\b;\s*drop\b",
                r"(?i)\b'\s*or\s*'1'\s*=\s*'1",
                r"(?i)'\s*or\s*1\s*=\s*1\s*--",
                r"(?i)\bwaitfor\s+delay\b",
                r"(?i)\bsleep\b\s*\("
            ],
            "xss_patterns": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>",
                r"vbscript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"<img[^>]*on\w+\s*=",
                r"<svg[^>]*on\w+\s*=",
                r"expression\s*\(",
                r"eval\s*\("
            ],
            "path_traversal_patterns": [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"/etc/shadow",
                r"C:\\Windows\\System32",
                r"..//..",
                r"%2e%2e%2f",
                r"%2e%2e\\"
            ],
            "command_injection_patterns": [
                r";\s*\w+",
                r"\|\s*\w+",
                r"&\s*\w+",
                r"`[^`]*`",
                r"\$\([^)]*\)",
                r"<\s*\w+[^>]*>",
                r"\bnc\s+",
                r"\bnetcat\s+",
                r"\btelnet\s+",
                r"\bwget\s+",
                r"\bcurl\s+"
            ],
            "malicious_user_agents": [
                r"sqlmap",
                r"nikto",
                r"nmap",
                r"masscan",
                r"zgrab",
                r"crawler",
                r"bot",
                r"spider",
                r"scanner",
                r"tester",
                r"curl",
                r"wget",
                r"python-requests",
                r"python-urllib"
            ]
        }

    def _initialize_threat_feeds(self):
        """Initialize threat intelligence feeds"""
        self.threat_feeds = {
            "malicious_ips": {
                "last_updated": datetime.now(),
                "ips": set(),
                "update_interval": 3600  # 1 hour
            },
            "compromised_credentials": {
                "last_updated": datetime.now(),
                "credentials": set(),
                "update_interval": 1800  # 30 minutes
            },
            "malicious_domains": {
                "last_updated": datetime.now(),
                "domains": set(),
                "update_interval": 3600  # 1 hour
            },
            "known_malware_hashes": {
                "last_updated": datetime.now(),
                "hashes": set(),
                "update_interval": 7200  # 2 hours
            }
        }

    async def process_security_event(self, event: SecurityEvent) -> Optional[ThreatAlert]:
        """Process security event and detect threats"""
        try:
            # Store event
            await self._store_security_event(event)

            # Update counters and metrics
            await self._update_metrics(event)

            # Run detection rules
            alerts = await self._run_detection_rules(event)

            # Run anomaly detection
            anomaly_alerts = await self._detect_anomalies(event)
            alerts.extend(anomaly_alerts)

            # Process alerts
            for alert in alerts:
                await self._process_threat_alert(alert)

            # Return the highest severity alert
            if alerts:
                return max(alerts, key=lambda a: a.severity.value)

            return None

        except Exception as e:
            logger.error(f"Error processing security event: {e}")
            return None

    async def _store_security_event(self, event: SecurityEvent):
        """Store security event in database"""
        try:
            event_key = f"security_event:{event.id}"
            event_data = {
                'id': event.id,
                'event_type': event.event_type,
                'user_id': event.user_id,
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'resource': event.resource,
                'action': event.action,
                'timestamp': event.timestamp.isoformat(),
                'severity': event.severity.value,
                'risk_score': event.risk_score,
                'metadata': event.metadata,
                'context': event.context
            }

            await self.redis_manager.set(
                event_key,
                json.dumps(event_data),
                expire=86400 * 90  # 90 days
            )

        except Exception as e:
            logger.error(f"Error storing security event: {e}")

    async def _update_metrics(self, event: SecurityEvent):
        """Update security metrics and counters"""
        try:
            # Update event counters
            counter_key = f"event_counter:{event.event_type}:{event.ip_address}"
            await self.redis_manager.incr(counter_key)
            await self.redis_manager.expire(counter_key, 3600)  # 1 hour

            # Update user behavior history
            user_key = f"user_behavior:{event.user_id}"
            behavior_data = {
                'timestamp': event.timestamp.isoformat(),
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'action': event.action,
                'resource': event.resource,
                'risk_score': event.risk_score
            }

            await self.redis_manager.lpush(user_key, json.dumps(behavior_data))
            await self.redis_manager.ltrim(user_key, 0, 99)  # Keep last 100 events

        except Exception as e:
            logger.error(f"Error updating metrics: {e}")

    async def _run_detection_rules(self, event: SecurityEvent) -> List[ThreatAlert]:
        """Run detection rules against event"""
        alerts = []

        try:
            for rule_name, rule in self.detection_rules.items():
                if await self._evaluate_detection_rule(rule_name, rule, event):
                    alert = await self._create_threat_alert(
                        ThreatType(rule_name),
                        rule["severity"],
                        rule["name"],
                        rule["description"],
                        [event.id]
                    )
                    alerts.append(alert)

        except Exception as e:
            logger.error(f"Error running detection rules: {e}")

        return alerts

    async def _evaluate_detection_rule(self, rule_name: str, rule: Dict[str, Any], event: SecurityEvent) -> bool:
        """Evaluate single detection rule"""
        try:
            conditions = rule["conditions"]

            # Check pattern matching
            if "pattern_match" in conditions:
                for pattern_type in conditions["pattern_match"]:
                    if pattern_type in self.malicious_patterns:
                        patterns = self.malicious_patterns[pattern_type]
                        text_to_check = event.metadata.get('request_data', '') + event.context.get('request_body', '')

                        for pattern in patterns:
                            if re.search(pattern, text_to_check, re.IGNORECASE):
                                return True

            # Check count-based conditions
            if "count" in conditions:
                count_key = f"rule_counter:{rule_name}:{event.ip_address}"
                current_count = int(await self.redis_manager.get(count_key) or 0)

                if current_count >= conditions["count"]:
                    return True

                await self.redis_manager.incr(count_key)
                await self.redis_manager.expire(count_key, rule["time_window"])

            # Check geographic analysis
            if conditions.get("geographic_analysis"):
                return await self._detect_impossible_travel(event)

            # Check behavior anomaly
            if conditions.get("behavior_anomaly"):
                return await self._detect_behavior_anomaly(event)

            # Check rate limit
            if conditions.get("rate_limit"):
                return await self._detect_rate_limit_violation(event)

            # Check data volume
            if conditions.get("data_volume"):
                return await self._detect_data_exfiltration(event)

            return False

        except Exception as e:
            logger.error(f"Error evaluating detection rule {rule_name}: {e}")
            return False

    async def _detect_impossible_travel(self, event: SecurityEvent) -> bool:
        """Detect impossible travel scenarios"""
        try:
            # Get user's recent login locations
            user_key = f"user_locations:{event.user_id}"
            recent_locations = await self.redis_manager.lrange(user_key, 0, 4)  # Last 5 locations

            if not recent_locations:
                # Store current location
                location_data = {
                    'ip_address': event.ip_address,
                    'timestamp': event.timestamp.isoformat(),
                    'location': event.context.get('location', 'Unknown')
                }
                await self.redis_manager.lpush(user_key, json.dumps(location_data))
                await self.redis_manager.ltrim(user_key, 0, 4)
                return False

            # Calculate distance and speed
            for location_data in recent_locations:
                prev_location = json.loads(location_data)
                prev_time = datetime.fromisoformat(prev_location['timestamp'])
                prev_ip = prev_location['ip_address']

                # Calculate distance between IPs (simplified)
                distance = await self._calculate_ip_distance(prev_ip, event.ip_address)
                time_diff = (event.timestamp - prev_time).total_seconds()

                if time_diff > 0:
                    speed = distance / time_diff  # km/s

                    # Check if speed is impossible (> 900 km/h)
                    if speed > 0.25:  # 900 km/h = 0.25 km/s
                        return True

            # Store current location
            location_data = {
                'ip_address': event.ip_address,
                'timestamp': event.timestamp.isoformat(),
                'location': event.context.get('location', 'Unknown')
            }
            await self.redis_manager.lpush(user_key, json.dumps(location_data))
            await self.redis_manager.ltrim(user_key, 0, 4)

            return False

        except Exception as e:
            logger.error(f"Error detecting impossible travel: {e}")
            return False

    async def _detect_behavior_anomaly(self, event: SecurityEvent) -> bool:
        """Detect behavioral anomalies"""
        try:
            # Get user's behavior history
            user_key = f"user_behavior:{event.user_id}"
            behavior_history = await self.redis_manager.lrange(user_key, 0, 99)

            if len(behavior_history) < 10:
                return False  # Not enough data

            # Analyze patterns
            recent_actions = []
            for behavior_data in behavior_history:
                behavior = json.loads(behavior_data)
                recent_actions.append(behavior['action'])

            # Check for unusual actions
            action_frequency = {}
            for action in recent_actions:
                action_frequency[action] = action_frequency.get(action, 0) + 1

            # If current action is rare for this user
            if event.action not in action_frequency or action_frequency[event.action] < 2:
                return True

            return False

        except Exception as e:
            logger.error(f"Error detecting behavior anomaly: {e}")
            return False

    async def _detect_rate_limit_violation(self, event: SecurityEvent) -> bool:
        """Detect rate limit violations"""
        try:
            # Check API request rate
            rate_key = f"api_rate:{event.ip_address}:{event.user_id}"
            current_rate = int(await self.redis_manager.get(rate_key) or 0)

            if current_rate > 100:  # 100 requests per minute
                return True

            await self.redis_manager.incr(rate_key)
            await self.redis_manager.expire(rate_key, 60)  # 1 minute

            return False

        except Exception as e:
            logger.error(f"Error detecting rate limit violation: {e}")
            return False

    async def _detect_data_exfiltration(self, event: SecurityEvent) -> bool:
        """Detect data exfiltration patterns"""
        try:
            # Check data transfer volume
            data_volume = event.metadata.get('data_size', 0)  # bytes

            if data_volume > 10 * 1024 * 1024:  # 10MB
                return True

            # Check for unusual data access patterns
            if event.action in ["data_export", "data_download", "file_download"]:
                # Check if this is unusual for the user
                user_key = f"data_access:{event.user_id}"
                access_history = await self.redis_manager.lrange(user_key, 0, 9)

                if len(access_history) < 5:
                    return True  # New pattern

                # Check frequency
                recent_access = len([a for a in access_history if json.loads(a)['action'] == event.action])
                if recent_access < 2:
                    return True  # Unusual pattern

            return False

        except Exception as e:
            logger.error(f"Error detecting data exfiltration: {e}")
            return False

    async def _detect_anomalies(self, event: SecurityEvent) -> List[ThreatAlert]:
        """Detect statistical anomalies"""
        alerts = []

        try:
            # Check against baselines
            for metric_name, baseline in self.baselines.items():
                current_value = await self._get_current_metric_value(metric_name, event)

                if current_value is not None:
                    # Calculate z-score
                    z_score = (current_value - baseline.baseline_value) / baseline.standard_deviation

                    # Check if anomaly (z-score > 3)
                    if abs(z_score) > 3:
                        alert = await self._create_threat_alert(
                            ThreatType.ANOMALOUS_BEHAVIOR,
                            AlertSeverity.MEDIUM,
                            f"Anomaly detected in {metric_name}",
                            f"Unusual {metric_name}: {current_value} (baseline: {baseline.baseline_value})",
                            [event.id]
                        )
                        alerts.append(alert)

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")

        return alerts

    async def _get_current_metric_value(self, metric_name: str, event: SecurityEvent) -> Optional[float]:
        """Get current value for metric"""
        try:
            if metric_name == "login_attempts_per_hour":
                # Count login attempts in last hour
                count_key = f"login_attempts:{event.ip_address}"
                return float(await self.redis_manager.get(count_key) or 0)

            elif metric_name == "api_requests_per_minute":
                # Count API requests in last minute
                count_key = f"api_requests:{event.ip_address}"
                return float(await self.redis_manager.get(count_key) or 0)

            elif metric_name == "data_transfer_per_hour":
                # Sum data transfer in last hour
                return float(event.metadata.get('data_size', 0))

            elif metric_name == "failed_login_rate":
                # Calculate failed login rate
                total_key = f"total_logins:{event.ip_address}"
                failed_key = f"failed_logins:{event.ip_address}"

                total = float(await self.redis_manager.get(total_key) or 1)
                failed = float(await self.redis_manager.get(failed_key) or 0)

                return failed / total

            elif metric_name == "session_duration":
                # Get average session duration
                return float(event.metadata.get('session_duration', 0))

            return None

        except Exception as e:
            logger.error(f"Error getting metric value: {e}")
            return None

    async def _create_threat_alert(self, threat_type: ThreatType, severity: AlertSeverity,
                                 title: str, description: str, source_events: List[str]) -> ThreatAlert:
        """Create threat alert"""
        alert_id = f"alert_{int(datetime.now().timestamp())}_{hash(title) % 10000}"

        alert = ThreatAlert(
            id=alert_id,
            threat_type=threat_type,
            severity=severity,
            title=title,
            description=description,
            source_events=source_events,
            confidence=0.8  # Default confidence
        )

        return alert

    async def _process_threat_alert(self, alert: ThreatAlert):
        """Process threat alert and create incident if necessary"""
        try:
            # Store alert
            await self._store_threat_alert(alert)

            # Check if this should escalate to incident
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                incident = await self._create_security_incident(alert)
                if incident:
                    logger.warning(f"Security incident created: {incident.id} - {incident.title}")

            # Send notifications
            await self._send_threat_notification(alert)

            # Update threat intelligence
            await self._update_threat_intelligence(alert)

        except Exception as e:
            logger.error(f"Error processing threat alert: {e}")

    async def _store_threat_alert(self, alert: ThreatAlert):
        """Store threat alert"""
        try:
            alert_key = f"threat_alert:{alert.id}"
            alert_data = {
                'id': alert.id,
                'threat_type': alert.threat_type.value,
                'severity': alert.severity.value,
                'title': alert.title,
                'description': alert.description,
                'detection_time': alert.detection_time.isoformat(),
                'source_events': alert.source_events,
                'confidence': alert.confidence,
                'status': alert.status.value,
                'metadata': alert.metadata
            }

            await self.redis_manager.set(
                alert_key,
                json.dumps(alert_data),
                expire=86400 * 30  # 30 days
            )

        except Exception as e:
            logger.error(f"Error storing threat alert: {e}")

    async def _create_security_incident(self, alert: ThreatAlert) -> Optional[SecurityIncident]:
        """Create security incident from alert"""
        try:
            incident_id = f"incident_{int(datetime.now().timestamp())}"

            incident = SecurityIncident(
                id=incident_id,
                title=f"Incident: {alert.title}",
                description=alert.description,
                severity=alert.severity,
                status=IncidentStatus.OPEN,
                detection_method="automated_threat_detection",
                related_alerts=[alert.id]
            )

            # Store incident
            await self._store_security_incident(incident)

            return incident

        except Exception as e:
            logger.error(f"Error creating security incident: {e}")
            return None

    async def _store_security_incident(self, incident: SecurityIncident):
        """Store security incident"""
        try:
            incident_key = f"security_incident:{incident.id}"
            incident_data = {
                'id': incident.id,
                'title': incident.title,
                'description': incident.description,
                'severity': incident.severity.value,
                'status': incident.status.value,
                'created_at': incident.created_at.isoformat(),
                'updated_at': incident.updated_at.isoformat(),
                'assigned_to': incident.assigned_to,
                'affected_users': incident.affected_users,
                'affected_resources': incident.affected_resources,
                'detection_method': incident.detection_method,
                'mitigation_steps': incident.mitigation_steps,
                'related_alerts': incident.related_alerts,
                'metadata': incident.metadata
            }

            await self.redis_manager.set(
                incident_key,
                json.dumps(incident_data),
                expire=86400 * 365  # 1 year
            )

        except Exception as e:
            logger.error(f"Error storing security incident: {e}")

    async def _send_threat_notification(self, alert: ThreatAlert):
        """Send threat notification"""
        try:
            notification_data = {
                'alert_id': alert.id,
                'severity': alert.severity.value,
                'title': alert.title,
                'description': alert.description,
                'timestamp': alert.detection_time.isoformat()
            }

            # Store notification for delivery
            notification_key = f"threat_notification:{alert.id}"
            await self.redis_manager.set(
                notification_key,
                json.dumps(notification_data),
                expire=86400  # 24 hours
            )

            # Log notification
            if alert.severity == AlertSeverity.CRITICAL:
                logger.critical(f"CRITICAL THREAT ALERT: {alert.title}")
            elif alert.severity == AlertSeverity.HIGH:
                logger.error(f"HIGH THREAT ALERT: {alert.title}")
            else:
                logger.warning(f"THREAT ALERT: {alert.title}")

        except Exception as e:
            logger.error(f"Error sending threat notification: {e}")

    async def _update_threat_intelligence(self, alert: ThreatAlert):
        """Update threat intelligence based on alert"""
        try:
            # Update IP reputation
            if alert.threat_type in [ThreatType.BRUTE_FORCE, ThreatType.DDOS_ATTACK]:
                if 'ip_address' in alert.metadata:
                    ip = alert.metadata['ip_address']
                    reputation_key = f"ip_reputation:{ip}"
                    reputation_data = {
                        'threat_score': 0.8,
                        'last_seen': alert.detection_time.isoformat(),
                        'threat_types': [alert.threat_type.value]
                    }
                    await self.redis_manager.set(reputation_key, json.dumps(reputation_data), expire=86400 * 7)

        except Exception as e:
            logger.error(f"Error updating threat intelligence: {e}")

    async def _calculate_ip_distance(self, ip1: str, ip2: str) -> float:
        """Calculate approximate distance between two IP addresses"""
        try:
            # This is a simplified calculation
            # In practice, you'd use a geolocation service
            return 0.0

        except Exception as e:
            logger.error(f"Error calculating IP distance: {e}")
            return 0.0

    async def start_monitoring(self):
        """Start threat monitoring"""
        logger.info("Starting threat detection monitoring")

        # Start detection worker
        if not self._detection_worker_running:
            asyncio.create_task(self._detection_worker())
            self._detection_worker_running = True

        # Start threat intelligence updates
        asyncio.create_task(self._update_threat_feeds())

        logger.info("Threat detection monitoring started")

    async def _detection_worker(self):
        """Worker for continuous threat detection"""
        logger.info("Threat detection worker started")

        while True:
            try:
                # Process queued security events
                await self._process_queued_events()

                # Run periodic threat scans
                await self._run_periodic_scans()

                # Clean up old data
                await self._cleanup_old_data()

                # Wait for next cycle
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in threat detection worker: {e}")
                await asyncio.sleep(60)

    async def _process_queued_events(self):
        """Process queued security events"""
        # This would process events from a queue
        pass

    async def _run_periodic_scans(self):
        """Run periodic threat scans"""
        try:
            # Scan for suspicious IPs
            await self._scan_suspicious_ips()

            # Scan for unusual behavior patterns
            await self._scan_behavior_patterns()

            # Update baselines
            await self._update_baselines()

        except Exception as e:
            logger.error(f"Error running periodic scans: {e}")

    async def _scan_suspicious_ips(self):
        """Scan for suspicious IP addresses"""
        try:
            # Get recent IPs with high activity
            suspicious_ips = await self.redis_manager.keys("ip_reputation:*")

            for ip_key in suspicious_ips:
                ip = ip_key.split(":")[-1]
                reputation_data = await self.redis_manager.get(ip_key)

                if reputation_data:
                    data = json.loads(reputation_data)
                    if data['threat_score'] > 0.7:
                        # Check if still active
                        activity_key = f"ip_activity:{ip}"
                        recent_activity = await self.redis_manager.get(activity_key)

                        if not recent_activity:
                            # IP no longer active, reduce reputation
                            data['threat_score'] *= 0.9
                            await self.redis_manager.set(ip_key, json.dumps(data), expire=86400 * 7)

        except Exception as e:
            logger.error(f"Error scanning suspicious IPs: {e}")

    async def _scan_behavior_patterns(self):
        """Scan for unusual behavior patterns"""
        # This would implement advanced behavior analysis
        pass

    async def _update_baselines(self):
        """Update security baselines"""
        try:
            # Update baselines periodically based on recent activity
            for metric_name, baseline in self.baselines.items():
                # This would recalculate baselines from recent data
                pass

        except Exception as e:
            logger.error(f"Error updating baselines: {e}")

    async def _cleanup_old_data(self):
        """Clean up old security data"""
        try:
            # Clean up old events (older than 90 days)
            cutoff_time = datetime.now() - timedelta(days=90)
            # This would clean up old data from database

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    async def _update_threat_feeds(self):
        """Update threat intelligence feeds"""
        while True:
            try:
                # Update malicious IPs
                await self._update_malicious_ips()

                # Update compromised credentials
                await self._update_compromised_credentials()

                # Wait for next update
                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                logger.error(f"Error updating threat feeds: {e}")
                await asyncio.sleep(3600)

    async def _update_malicious_ips(self):
        """Update malicious IP list"""
        try:
            # This would fetch from threat intelligence feeds
            # For now, it's a placeholder
            pass

        except Exception as e:
            logger.error(f"Error updating malicious IPs: {e}")

    async def _update_compromised_credentials(self):
        """Update compromised credentials list"""
        try:
            # This would fetch from breach databases
            # For now, it's a placeholder
            pass

        except Exception as e:
            logger.error(f"Error updating compromised credentials: {e}")

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        try:
            dashboard = {
                'total_alerts': 0,
                'active_incidents': 0,
                'threat_distribution': {},
                'recent_alerts': [],
                'system_health': 'healthy',
                'last_update': datetime.now().isoformat()
            }

            # Get recent alerts
            recent_alerts = await self.redis_manager.keys("threat_alert:*")
            dashboard['total_alerts'] = len(recent_alerts)

            # Get active incidents
            active_incidents = await self.redis_manager.keys("security_incident:*")
            dashboard['active_incidents'] = len(active_incidents)

            # Get threat distribution
            threat_types = defaultdict(int)
            for alert_key in recent_alerts:
                alert_data = await self.redis_manager.get(alert_key)
                if alert_data:
                    alert = json.loads(alert_data)
                    threat_types[alert['threat_type']] += 1

            dashboard['threat_distribution'] = dict(threat_types)

            # Get recent critical alerts
            critical_alerts = []
            for alert_key in recent_alerts[:10]:  # Last 10 alerts
                alert_data = await self.redis_manager.get(alert_key)
                if alert_data:
                    alert = json.loads(alert_data)
                    if alert['severity'] in ['high', 'critical']:
                        critical_alerts.append(alert)

            dashboard['recent_alerts'] = critical_alerts[:5]

            return dashboard

        except Exception as e:
            logger.error(f"Error getting security dashboard: {e}")
            return {'error': str(e)}

    async def get_security_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            report = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_events': 0,
                    'total_alerts': 0,
                    'total_incidents': 0,
                    'critical_incidents': 0
                },
                'threat_types': {},
                'top_affected_ips': {},
                'top_affected_users': {},
                'recommendations': []
            }

            # This would generate comprehensive report from database
            # For now, it's a placeholder

            return report

        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {'error': str(e)}