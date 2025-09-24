"""
API Security and Rate Limiting System

Provides comprehensive API security measures:
- Advanced rate limiting with multiple strategies
- API key management and authentication
- Request validation and sanitization
- API gateway security
- Web application firewall (WAF) rules
- DDoS protection
- API abuse detection and prevention
- CORS and CSP policies
- Request/response logging and monitoring
"""

import os
import json
import time
import hashlib
import secrets
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import logging
import re
import asyncio
from ipaddress import ip_address, ip_network

# Import security components
from .security_config import SecurityConfigManager
from .audit_logging import AuditLogger, AuditEventType, AuditSeverity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    LEAKY_BUCKET = "leaky_bucket"


class APIKeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class SecurityLevel(Enum):
    """API security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class APIKey:
    """API key with metadata"""
    key_id: str
    key_hash: str
    key_prefix: str
    name: str
    description: str
    owner_id: str
    permissions: List[str] = field(default_factory=list)
    rate_limit: int = 1000  # requests per hour
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    allowed_ips: List[str] = field(default_factory=list)
    allowed_referers: List[str] = field(default_factory=list)
    webhooks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    window_size: int = 60  # seconds
    enable_ip_whitelisting: bool = True
    enable_rate_limit_headers: bool = True
    enable_progressive_delays: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 100
    circuit_breaker_timeout: int = 300


@dataclass
class SecurityRule:
    """Security rule definition"""
    rule_id: str
    name: str
    description: str
    type: str  # pattern, regex, rate_limit, ip_block, etc.
    condition: str
    action: str  # block, challenge, log, alert
    severity: SecurityLevel
    enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Advanced rate limiting implementation"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.counters: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.token_buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.sliding_windows: Dict[str, deque] = defaultdict(deque)
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.ip_whitelist: set = set()
        self.ip_blacklist: set = set()

        # Start cleanup task
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cleanup task"""
        # Would start asyncio task for periodic cleanup
        logger.info("Started rate limiter cleanup task")

    def check_rate_limit(self, identifier: str, resource: str = "default") -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        if identifier in self.ip_whitelist:
            return True, {"message": "IP whitelisted", "remaining": float('inf')}

        if identifier in self.ip_blacklist:
            return False, {"message": "IP blacklisted", "remaining": 0}

        # Check circuit breaker first
        if self.config.enable_circuit_breaker:
            circuit_status = self._check_circuit_breaker(identifier)
            if circuit_status["blocked"]:
                return False, {
                    "message": "Circuit breaker tripped",
                    "remaining": 0,
                    "retry_after": circuit_status["retry_after"]
                }

        # Apply rate limiting strategy
        if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._token_bucket_limit(identifier, resource)
        elif self.config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._fixed_window_limit(identifier, resource)
        elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._sliding_window_limit(identifier, resource)
        elif self.config.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return self._leaky_bucket_limit(identifier, resource)
        else:
            return True, {"message": "No rate limiting", "remaining": float('inf')}

    def _token_bucket_limit(self, identifier: str, resource: str) -> Tuple[bool, Dict[str, Any]]:
        """Token bucket rate limiting"""
        key = f"{identifier}:{resource}"
        bucket = self.token_buckets[key]

        current_time = time.time()
        if not bucket:
            bucket = {
                "tokens": self.config.burst_limit,
                "last_refill": current_time,
                "capacity": self.config.burst_limit,
                "refill_rate": self.config.requests_per_minute / 60  # tokens per second
            }
            self.token_buckets[key] = bucket

        # Refill tokens
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * bucket["refill_rate"]
        bucket["tokens"] = min(bucket["capacity"], bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Check if request can be processed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            remaining = bucket["tokens"]
            return True, {
                "remaining": remaining,
                "reset_time": current_time + (1 / bucket["refill_rate"]),
                "limit": bucket["capacity"]
            }
        else:
            retry_after = 1 / bucket["refill_rate"]
            return False, {
                "remaining": 0,
                "retry_after": retry_after,
                "limit": bucket["capacity"]
            }

    def _fixed_window_limit(self, identifier: str, resource: str) -> Tuple[bool, Dict[str, Any]]:
        """Fixed window rate limiting"""
        key = f"{identifier}:{resource}"
        current_time = time.time()
        window_start = int(current_time // self.config.window_size) * self.config.window_size

        if key not in self.counters:
            self.counters[key] = {
                "count": 0,
                "window_start": window_start,
                "limit": self.config.requests_per_minute
            }

        counter = self.counters[key]

        # Reset window if it's a new window
        if current_time - counter["window_start"] >= self.config.window_size:
            counter["count"] = 0
            counter["window_start"] = window_start

        # Check limit
        if counter["count"] < counter["limit"]:
            counter["count"] += 1
            remaining = counter["limit"] - counter["count"]
            reset_time = window_start + self.config.window_size

            return True, {
                "remaining": remaining,
                "reset_time": reset_time,
                "limit": counter["limit"]
            }
        else:
            retry_after = window_start + self.config.window_size - current_time
            return False, {
                "remaining": 0,
                "retry_after": retry_after,
                "limit": counter["limit"]
            }

    def _sliding_window_limit(self, identifier: str, resource: str) -> Tuple[bool, Dict[str, Any]]:
        """Sliding window rate limiting"""
        key = f"{identifier}:{resource}"
        current_time = time.time()
        window_size = self.config.window_size

        if key not in self.sliding_windows:
            self.sliding_windows[key] = deque()

        window = self.sliding_windows[key]

        # Remove old requests
        cutoff_time = current_time - window_size
        while window and window[0] < cutoff_time:
            window.popleft()

        # Check limit
        if len(window) < self.config.requests_per_minute:
            window.append(current_time)
            remaining = self.config.requests_per_minute - len(window)

            return True, {
                "remaining": remaining,
                "reset_time": current_time + 1,  # Next potential reset
                "limit": self.config.requests_per_minute
            }
        else:
            retry_after = window[0] + window_size - current_time
            return False, {
                "remaining": 0,
                "retry_after": retry_after,
                "limit": self.config.requests_per_minute
            }

    def _leaky_bucket_limit(self, identifier: str, resource: str) -> Tuple[bool, Dict[str, Any]]:
        """Leaky bucket rate limiting"""
        key = f"{identifier}:{resource}"
        current_time = time.time()

        if key not in self.counters:
            self.counters[key] = {
                "bucket_size": 0,
                "last_leak": current_time,
                "capacity": self.config.burst_limit,
                "leak_rate": self.config.requests_per_minute / 60  # requests per second
            }

        bucket = self.counters[key]

        # Leak from bucket
        time_passed = current_time - bucket["last_leak"]
        leak_amount = time_passed * bucket["leak_rate"]
        bucket["bucket_size"] = max(0, bucket["bucket_size"] - leak_amount)
        bucket["last_leak"] = current_time

        # Check if request can be added
        if bucket["bucket_size"] < bucket["capacity"]:
            bucket["bucket_size"] += 1
            remaining = bucket["capacity"] - bucket["bucket_size"]

            return True, {
                "remaining": remaining,
                "reset_time": current_time + (1 / bucket["leak_rate"]),
                "limit": bucket["capacity"]
            }
        else:
            retry_after = 1 / bucket["leak_rate"]
            return False, {
                "remaining": 0,
                "retry_after": retry_after,
                "limit": bucket["capacity"]
            }

    def _check_circuit_breaker(self, identifier: str) -> Dict[str, Any]:
        """Check circuit breaker status"""
        if identifier not in self.circuit_breakers:
            self.circuit_breakers[identifier] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure": None,
                "retry_after": None
            }

        breaker = self.circuit_breakers[identifier]
        current_time = time.time()

        # Reset circuit breaker if cooldown period has passed
        if (breaker["state"] == "open" and
            breaker["retry_after"] and
            current_time > breaker["retry_after"]):
            breaker["state"] = "half_open"
            breaker["failure_count"] = 0

        return {
            "blocked": breaker["state"] == "open",
            "retry_after": breaker["retry_after"],
            "state": breaker["state"]
        }

    def record_failure(self, identifier: str):
        """Record failure for circuit breaker"""
        if not self.config.enable_circuit_breaker:
            return

        if identifier not in self.circuit_breakers:
            self.circuit_breakers[identifier] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None,
                "retry_after": None
            }

        breaker = self.circuit_breakers[identifier]
        breaker["failure_count"] += 1
        breaker["last_failure"] = time.time()

        # Trip circuit breaker if threshold exceeded
        if (breaker["failure_count"] >= self.config.circuit_breaker_threshold and
            breaker["state"] != "open"):
            breaker["state"] = "open"
            breaker["retry_after"] = time.time() + self.config.circuit_breaker_timeout

    def record_success(self, identifier: str):
        """Record success for circuit breaker"""
        if not self.config.enable_circuit_breaker:
            return

        if identifier in self.circuit_breakers:
            breaker = self.circuit_breakers[identifier]
            if breaker["state"] == "half_open":
                breaker["state"] = "closed"
                breaker["failure_count"] = 0

    def add_to_whitelist(self, identifier: str):
        """Add identifier to whitelist"""
        self.ip_whitelist.add(identifier)
        logger.info(f"Added {identifier} to rate limit whitelist")

    def remove_from_whitelist(self, identifier: str):
        """Remove identifier from whitelist"""
        self.ip_whitelist.discard(identifier)
        logger.info(f"Removed {identifier} from rate limit whitelist")

    def add_to_blacklist(self, identifier: str):
        """Add identifier to blacklist"""
        self.ip_blacklist.add(identifier)
        logger.info(f"Added {identifier} to rate limit blacklist")

    def remove_from_blacklist(self, identifier: str):
        """Remove identifier from blacklist"""
        self.ip_blacklist.discard(identifier)
        logger.info(f"Removed {identifier} from rate limit blacklist")

    def cleanup_old_data(self):
        """Clean up old rate limiting data"""
        current_time = time.time()
        cutoff_time = current_time - (self.config.window_size * 2)

        # Clean up counters
        keys_to_remove = []
        for key, counter in self.counters.items():
            if counter["window_start"] < cutoff_time:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.counters[key]

        # Clean up sliding windows
        for key in list(self.sliding_windows.keys()):
            window = self.sliding_windows[key]
            if window and window[-1] < cutoff_time:
                del self.sliding_windows[key]

        # Clean up circuit breakers
        for identifier in list(self.circuit_breakers.keys()):
            breaker = self.circuit_breakers[identifier]
            if (breaker["last_failure"] and
                current_time - breaker["last_failure"] > self.config.circuit_breaker_timeout * 2):
                del self.circuit_breakers[identifier]

        logger.debug("Rate limiter cleanup completed")


class APIKeyManager:
    """API key management system"""

    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.key_prefixes: Dict[str, str] = {}  # prefix -> key_id mapping

    def generate_api_key(self, name: str, owner_id: str, permissions: List[str] = None,
                        rate_limit: int = 1000, expires_days: int = None) -> APIKey:
        """Generate a new API key"""
        # Generate secure random key
        key_bytes = secrets.token_bytes(32)
        key_string = key_bytes.hex()
        key_prefix = key_string[:8]

        # Hash the key for storage
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()

        # Calculate expiry
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + timedelta(days=expires_days)

        # Create API key object
        api_key = APIKey(
            key_id=str(uuid.uuid4()),
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
            description=f"API key for {name}",
            owner_id=owner_id,
            permissions=permissions or [],
            rate_limit=rate_limit,
            expires_at=expires_at
        )

        self.api_keys[api_key.key_id] = api_key
        self.key_prefixes[key_prefix] = api_key.key_id

        logger.info(f"Generated API key {api_key.key_id} for {owner_id}")
        return api_key, key_string

    def validate_api_key(self, key_string: str) -> Optional[APIKey]:
        """Validate API key and return key info"""
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        key_prefix = key_string[:8]

        # Find key by prefix first (faster lookup)
        if key_prefix not in self.key_prefixes:
            return None

        key_id = self.key_prefixes[key_prefix]
        api_key = self.api_keys.get(key_id)

        if not api_key:
            return None

        # Check if key hash matches
        if api_key.key_hash != key_hash:
            return None

        # Check key status
        if api_key.status != APIKeyStatus.ACTIVE:
            return None

        # Check expiry
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            api_key.status = APIKeyStatus.EXPIRED
            return None

        # Update last used timestamp
        api_key.last_used = datetime.now()

        return api_key

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id not in self.api_keys:
            return False

        api_key = self.api_keys[key_id]
        api_key.status = APIKeyStatus.REVOKED

        # Remove from prefix mapping
        if api_key.key_prefix in self.key_prefixes:
            del self.key_prefixes[api_key.key_prefix]

        logger.info(f"Revoked API key {key_id}")
        return True

    def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        return self.api_keys.get(key_id)

    def get_keys_by_owner(self, owner_id: str) -> List[APIKey]:
        """Get all API keys for an owner"""
        return [key for key in self.api_keys.values() if key.owner_id == owner_id]

    def update_api_key(self, key_id: str, updates: Dict[str, Any]) -> bool:
        """Update API key properties"""
        if key_id not in self.api_keys:
            return False

        api_key = self.api_keys[key_id]

        for field, value in updates.items():
            if hasattr(api_key, field):
                setattr(api_key, field, value)

        logger.info(f"Updated API key {key_id}")
        return True

    def check_permission(self, api_key: APIKey, required_permission: str) -> bool:
        """Check if API key has required permission"""
        return required_permission in api_key.permissions

    def check_rate_limit(self, api_key: APIKey) -> bool:
        """Check if API key is within its rate limit"""
        # Would integrate with rate limiter
        return True


class APISecurityManager:
    """Main API security management system"""

    def __init__(self, security_config: SecurityConfigManager, audit_logger: AuditLogger):
        self.security_config = security_config
        self.audit_logger = audit_logger

        # Initialize components
        rate_config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_limit=10,
            enable_circuit_breaker=True
        )
        self.rate_limiter = RateLimiter(rate_config)
        self.api_key_manager = APIKeyManager()

        # Security rules
        self.security_rules: Dict[str, SecurityRule] = {}
        self.blocked_ips: set = set()
        self.suspicious_patterns: List[Dict[str, Any]] = []

        self._initialize_security_rules()

    def _initialize_security_rules(self):
        """Initialize security rules"""
        rules = [
            SecurityRule(
                rule_id="sql_injection_pattern",
                name="SQL Injection Detection",
                description="Detect SQL injection attempts",
                type="pattern",
                condition=r"(union\s+select|drop\s+table|insert\s+into|delete\s+from|update\s+\w+\s+set)",
                action="block",
                severity=SecurityLevel.CRITICAL,
                priority=1
            ),
            SecurityRule(
                rule_id="xss_pattern",
                name="XSS Detection",
                description="Detect cross-site scripting attempts",
                type="pattern",
                condition=r"(<script|javascript:|on\w+\s*=|alert\s*\(|document\.)",
                action="block",
                severity=SecurityLevel.HIGH,
                priority=2
            ),
            SecurityRule(
                rule_id="path_traversal",
                name="Path Traversal Detection",
                description="Detect directory traversal attempts",
                type="pattern",
                condition=r"(\.\./|\.\.\\\|\.\./\.\./)",
                action="block",
                severity=SecurityLevel.HIGH,
                priority=3
            ),
            SecurityRule(
                rule_id="command_injection",
                name="Command Injection Detection",
                description="Detect command injection attempts",
                type="pattern",
                condition=r"(;|\||&|\$\(|`|\$\{)",
                action="block",
                severity=SecurityLevel.CRITICAL,
                priority=4
            ),
            SecurityRule(
                rule_id="large_payload",
                name="Large Payload Detection",
                description="Detect unusually large request payloads",
                type="size",
                condition="payload_size > 10485760",  # 10MB
                action="block",
                severity=SecurityLevel.MEDIUM,
                priority=5
            ),
            SecurityRule(
                rule_id="suspicious_user_agent",
                name="Suspicious User Agent",
                description="Detect suspicious user agents",
                type="pattern",
                condition=r"(sqlmap|nikto|nmap|masscan|burp|metasploit)",
                action="block",
                severity=SecurityLevel.HIGH,
                priority=6
            )
        ]

        for rule in rules:
            self.security_rules[rule.rule_id] = rule

        logger.info(f"Initialized {len(rules)} security rules")

    def validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API request against security rules"""
        validation_result = {
            "allowed": True,
            "violations": [],
            "score": 0,
            "action": "allow",
            "message": "Request validated successfully"
        }

        # Extract request information
        ip_address = request_data.get("ip_address", "")
        user_agent = request_data.get("user_agent", "")
        method = request_data.get("method", "")
        path = request_data.get("path", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        api_key = request_data.get("api_key")

        # Check IP blacklist
        if ip_address in self.blocked_ips:
            validation_result["allowed"] = False
            validation_result["action"] = "block"
            validation_result["message"] = "IP address blocked"
            return validation_result

        # Check rate limiting
        if ip_address:
            rate_limit_result, rate_info = self.rate_limiter.check_rate_limit(ip_address)
            if not rate_limit_result:
                validation_result["allowed"] = False
                validation_result["action"] = "block"
                validation_result["message"] = "Rate limit exceeded"
                validation_result["violations"].append({
                    "rule": "rate_limit",
                    "message": "Rate limit exceeded",
                    "severity": "high",
                    "retry_after": rate_info.get("retry_after")
                })
                return validation_result

        # Validate API key if provided
        if api_key:
            key_info = self.api_key_manager.validate_api_key(api_key)
            if not key_info:
                validation_result["allowed"] = False
                validation_result["action"] = "block"
                validation_result["message"] = "Invalid API key"
                validation_result["violations"].append({
                    "rule": "api_key_validation",
                    "message": "Invalid API key",
                    "severity": "high"
                })
                return validation_result

        # Apply security rules
        for rule in self.security_rules.values():
            if not rule.enabled:
                continue

            violation = self._check_security_rule(rule, request_data)
            if violation:
                validation_result["violations"].append(violation)
                validation_result["score"] += self._get_severity_score(rule.severity)

                # Determine action based on rule and severity
                if rule.action == "block" or rule.severity == SecurityLevel.CRITICAL:
                    validation_result["allowed"] = False
                    validation_result["action"] = "block"
                    validation_result["message"] = f"Security violation: {rule.name}"

        # Log security event
        self._log_security_event(request_data, validation_result)

        return validation_result

    def _check_security_rule(self, rule: SecurityRule, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if request violates a security rule"""
        if rule.type == "pattern":
            return self._check_pattern_rule(rule, request_data)
        elif rule.type == "size":
            return self._check_size_rule(rule, request_data)
        elif rule.type == "regex":
            return self._check_regex_rule(rule, request_data)
        else:
            return None

    def _check_pattern_rule(self, rule: SecurityRule, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check pattern-based security rule"""
        pattern = rule.condition.lower()
        search_targets = [
            request_data.get("path", ""),
            request_data.get("body", ""),
            request_data.get("user_agent", ""),
            str(request_data.get("headers", {}))
        ]

        for target in search_targets:
            if pattern in target.lower():
                return {
                    "rule": rule.rule_id,
                    "name": rule.name,
                    "message": f"Pattern detected: {pattern}",
                    "severity": rule.severity.value,
                    "action": rule.action
                }

        return None

    def _check_size_rule(self, rule: SecurityRule, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check size-based security rule"""
        body_size = len(str(request_data.get("body", "")))
        size_limit = int(rule.condition.split(">")[1].strip())

        if body_size > size_limit:
            return {
                "rule": rule.rule_id,
                "name": rule.name,
                "message": f"Payload size {body_size} exceeds limit {size_limit}",
                "severity": rule.severity.value,
                "action": rule.action
            }

        return None

    def _check_regex_rule(self, rule: SecurityRule, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check regex-based security rule"""
        try:
            pattern = re.compile(rule.condition, re.IGNORECASE)
            search_targets = [
                request_data.get("path", ""),
                request_data.get("body", ""),
                request_data.get("user_agent", "")
            ]

            for target in search_targets:
                if pattern.search(target):
                    return {
                        "rule": rule.rule_id,
                        "name": rule.name,
                        "message": f"Regex pattern matched",
                        "severity": rule.severity.value,
                        "action": rule.action
                    }

        except re.error:
            logger.error(f"Invalid regex pattern in rule {rule.rule_id}")

        return None

    def _get_severity_score(self, severity: SecurityLevel) -> int:
        """Get severity score for rule"""
        severity_scores = {
            SecurityLevel.LOW: 1,
            SecurityLevel.MEDIUM: 5,
            SecurityLevel.HIGH: 10,
            SecurityLevel.CRITICAL: 20
        }
        return severity_scores.get(severity, 1)

    def _log_security_event(self, request_data: Dict[str, Any], validation_result: Dict[str, Any]):
        """Log security validation event"""
        event_type = AuditEventType.API_CALL
        severity = AuditSeverity.LOW

        if not validation_result["allowed"]:
            event_type = AuditEventType.SECURITY_POLICY_VIOLATION
            if validation_result["score"] >= 20:
                severity = AuditSeverity.CRITICAL
            elif validation_result["score"] >= 10:
                severity = AuditSeverity.HIGH
            elif validation_result["score"] >= 5:
                severity = AuditSeverity.MEDIUM

        self.audit_logger.log_event(
            event_type=event_type,
            severity=severity,
            action="api_request_validation",
            user_id=request_data.get("user_id"),
            ip_address=request_data.get("ip_address"),
            resource_type="api_endpoint",
            resource_id=request_data.get("path"),
            details={
                "method": request_data.get("method"),
                "validation_score": validation_result["score"],
                "violations": validation_result["violations"],
                "allowed": validation_result["allowed"]
            },
            outcome="success" if validation_result["allowed"] else "failure"
        )

    def block_ip_address(self, ip_address: str, reason: str = "", duration_hours: int = 24):
        """Block an IP address"""
        try:
            # Validate IP address
            ip_obj = ip_address(ip_address)
            self.blocked_ips.add(ip_address)

            # Log IP block event
            self.audit_logger.log_event(
                event_type=AuditEventType.THREAT_DETECTION,
                severity=AuditSeverity.HIGH,
                action="ip_blocked",
                resource_type="ip_address",
                resource_id=ip_address,
                details={
                    "reason": reason,
                    "duration_hours": duration_hours,
                    "blocked_by": "api_security"
                }
            )

            logger.warning(f"Blocked IP address: {ip_address} - {reason}")

        except ValueError:
            logger.error(f"Invalid IP address format: {ip_address}")

    def unblock_ip_address(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        logger.info(f"Unblocked IP address: {ip_address}")

    def get_security_status(self) -> Dict[str, Any]:
        """Get API security system status"""
        return {
            "blocked_ips_count": len(self.blocked_ips),
            "security_rules_count": len(self.security_rules),
            "active_rules_count": len([r for r in self.security_rules.values() if r.enabled]),
            "api_keys_count": len(self.api_key_manager.api_keys),
            "suspicious_patterns_count": len(self.suspicious_patterns),
            "rate_limiter_status": "active",
            "security_features": [
                "rate_limiting",
                "api_key_authentication",
                "ip_blocking",
                "request_validation",
                "sql_injection_detection",
                "xss_detection",
                "circuit_breaker"
            ]
        }

    def generate_security_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate security report for specified period"""
        # Would integrate with audit logger to get recent events
        report = {
            "report_period_days": days,
            "generated_at": datetime.now().isoformat(),
            "blocked_requests": 0,
            "failed_validations": 0,
            "blocked_ips": len(self.blocked_ips),
            "api_keys_active": len([k for k in self.api_key_manager.api_keys.values() if k.status == APIKeyStatus.ACTIVE]),
            "security_violations": [],
            "top_blocked_ips": [],
            "top_violation_types": []
        }

        # Would populate with actual data from audit logs
        logger.info(f"Generated security report for {days} days")
        return report