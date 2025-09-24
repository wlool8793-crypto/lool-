"""
Advanced Authentication System for LangGraph Deep Web Agent

This module provides comprehensive authentication mechanisms including
multi-factor authentication, social logins, biometric authentication,
and advanced security features.
"""

import asyncio
import json
import logging
import secrets
import hashlib
import base64
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import asyncpg
import redis.asyncio as redis
from passlib.context import CryptContext
from passlib.hash import argon2, bcrypt, pbkdf2_sha256
import pyotp
import qrcode
from io import BytesIO

from app.core.config import settings
from app.database.redis import RedisManager
from app.database.models import User
from app.integrations.external_apis import ExternalAPIManager

logger = logging.getLogger(__name__)

class AuthMethod(Enum):
    PASSWORD = "password"
    OTP = "otp"
    BIOMETRIC = "biometric"
    SOCIAL = "social"
    API_KEY = "api_key"
    WEBAUTHN = "webauthn"
    SAML = "saml"
    OAUTH2 = "oauth2"

class MFAType(Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    AUTHENTICATOR = "authenticator"
    BIOMETRIC = "biometric"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuthAttempt:
    """Authentication attempt record"""
    id: str
    user_id: str
    method: AuthMethod
    success: bool
    ip_address: str
    user_agent: str
    location: str = ""
    device_fingerprint: str = ""
    risk_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityContext:
    """User security context"""
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    location: str
    device_fingerprint: str
    risk_level: RiskLevel
    auth_methods: List[AuthMethod]
    mfa_required: bool = False
    mfa_verified: bool = False
    session_timeout: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MFADevice:
    """MFA device configuration"""
    id: str
    user_id: str
    mfa_type: MFAType
    name: str
    secret: str
    enabled: bool = True
    backup_codes: List[str] = field(default_factory=list)
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    id: str
    name: str
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    password_expire_days: int = 90
    mfa_required: bool = True
    session_timeout_hours: int = 24
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    allowed_ip_ranges: List[str] = field(default_factory=list)
    risk_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedAuthManager:
    """Advanced authentication and security manager"""

    def __init__(self):
        self.redis_manager = RedisManager()
        self.api_manager = ExternalAPIManager()

        # Password hashing context
        self.pwd_context = CryptContext(
            schemes=["argon2", "bcrypt", "pbkdf2_sha256"],
            deprecated="auto",
            argon2__time_cost=3,
            argon2__memory_cost=65536,
            argon2__parallelism=4,
            argon2__hash_len=32,
            bcrypt__rounds=12
        )

        # Security policies
        self.policies = self._load_security_policies()

        # Rate limiting
        self.attempt_counters = {}
        self.locked_accounts = {}

        # Risk assessment
        self.risk_factors = {}
        self._initialize_risk_factors()

        # Session management
        self.active_sessions = {}

        # MFA management
        self.mfa_devices = {}

    def _load_security_policies(self) -> Dict[str, SecurityPolicy]:
        """Load security policies"""
        return {
            "default": SecurityPolicy(
                id="default",
                name="Default Security Policy",
                password_min_length=12,
                password_require_uppercase=True,
                password_require_lowercase=True,
                password_require_numbers=True,
                password_require_special=True,
                password_expire_days=90,
                mfa_required=True,
                session_timeout_hours=24,
                max_login_attempts=5,
                lockout_duration_minutes=30,
                risk_threshold=0.7
            ),
            "high_security": SecurityPolicy(
                id="high_security",
                name="High Security Policy",
                password_min_length=16,
                password_require_uppercase=True,
                password_require_lowercase=True,
                password_require_numbers=True,
                password_require_special=True,
                password_expire_days=30,
                mfa_required=True,
                session_timeout_hours=8,
                max_login_attempts=3,
                lockout_duration_minutes=60,
                risk_threshold=0.5
            ),
            "relaxed": SecurityPolicy(
                id="relaxed",
                name="Relaxed Security Policy",
                password_min_length=8,
                password_require_uppercase=False,
                password_require_lowercase=True,
                password_require_numbers=False,
                password_require_special=False,
                password_expire_days=180,
                mfa_required=False,
                session_timeout_hours=72,
                max_login_attempts=10,
                lockout_duration_minutes=15,
                risk_threshold=0.8
            )
        }

    def _initialize_risk_factors(self):
        """Initialize risk assessment factors"""
        self.risk_factors = {
            "new_device": 0.3,
            "new_location": 0.4,
            "impossible_travel": 0.8,
            "suspicious_ip": 0.6,
            "brute_force": 0.9,
            "malicious_user_agent": 0.5,
            "time_anomaly": 0.3,
            "failed_attempts": 0.4,
            "high_privilege": 0.2
        }

    async def hash_password(self, password: str) -> str:
        """Hash password using secure algorithm"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    async def validate_password_strength(self, password: str, policy: SecurityPolicy) -> Dict[str, Any]:
        """Validate password against security policy"""
        validation_result = {
            'valid': True,
            'score': 0,
            'issues': [],
            'suggestions': []
        }

        try:
            # Check minimum length
            if len(password) < policy.password_min_length:
                validation_result['valid'] = False
                validation_result['issues'].append(f"Password must be at least {policy.password_min_length} characters long")
                validation_result['suggestions'].append("Use a longer password")

            # Check character requirements
            if policy.password_require_uppercase and not re.search(r'[A-Z]', password):
                validation_result['valid'] = False
                validation_result['issues'].append("Password must contain uppercase letters")
                validation_result['suggestions'].append("Add uppercase letters")

            if policy.password_require_lowercase and not re.search(r'[a-z]', password):
                validation_result['valid'] = False
                validation_result['issues'].append("Password must contain lowercase letters")
                validation_result['suggestions'].append("Add lowercase letters")

            if policy.password_require_numbers and not re.search(r'\d', password):
                validation_result['valid'] = False
                validation_result['issues'].append("Password must contain numbers")
                validation_result['suggestions'].append("Add numbers")

            if policy.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                validation_result['valid'] = False
                validation_result['issues'].append("Password must contain special characters")
                validation_result['suggestions'].append("Add special characters")

            # Check for common passwords
            common_passwords = [
                "password", "123456", "qwerty", "admin", "letmein",
                "welcome", "monkey", "password1", "123456789"
            ]
            if password.lower() in common_passwords:
                validation_result['valid'] = False
                validation_result['issues'].append("Password is too common")
                validation_result['suggestions'].append("Choose a more unique password")

            # Calculate password strength score
            score = 0
            if len(password) >= 12:
                score += 2
            elif len(password) >= 8:
                score += 1

            if re.search(r'[A-Z]', password):
                score += 1
            if re.search(r'[a-z]', password):
                score += 1
            if re.search(r'\d', password):
                score += 1
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                score += 1

            if not re.search(r'(.)\1{2,}', password):  # No repeated characters
                score += 1

            validation_result['score'] = score

            return validation_result

        except Exception as e:
            logger.error(f"Error validating password strength: {e}")
            validation_result['valid'] = False
            validation_result['issues'].append("Validation error occurred")
            return validation_result

    async def assess_login_risk(self, user_id: str, ip_address: str, user_agent: str,
                               device_fingerprint: str) -> Tuple[float, RiskLevel, List[str]]:
        """Assess login risk and return risk score, level, and factors"""
        risk_score = 0.0
        risk_factors = []

        try:
            # Get user's recent login history
            recent_logins = await self._get_recent_logins(user_id, days=30)

            # Check for new device
            if recent_logins:
                known_devices = set(login.get('device_fingerprint', '') for login in recent_logins)
                if device_fingerprint not in known_devices:
                    risk_score += self.risk_factors["new_device"]
                    risk_factors.append("New device detected")

            # Check for new location
            if recent_logins:
                known_locations = set(login.get('location', '') for login in recent_logins)
                current_location = await self._get_location_from_ip(ip_address)
                if current_location not in known_locations:
                    risk_score += self.risk_factors["new_location"]
                    risk_factors.append("New location detected")

            # Check for impossible travel
            if recent_logins:
                last_login = recent_logins[0]
                last_location = last_login.get('location', '')
                last_time = last_login.get('timestamp')
                current_location = await self._get_location_from_ip(ip_address)

                if last_location and current_location and last_time:
                    distance = await self._calculate_distance(last_location, current_location)
                    time_diff = (datetime.now() - last_time).total_seconds()
                    speed = distance / time_diff if time_diff > 0 else 0

                    if speed > 900:  # Faster than commercial airplane
                        risk_score += self.risk_factors["impossible_travel"]
                        risk_factors.append("Impossible travel detected")

            # Check for suspicious IP
            if await self._is_suspicious_ip(ip_address):
                risk_score += self.risk_factors["suspicious_ip"]
                risk_factors.append("Suspicious IP address")

            # Check for brute force attempts
            failed_attempts = await self._get_failed_attempts(user_id, ip_address, hours=1)
            if failed_attempts > 5:
                risk_score += self.risk_factors["brute_force"]
                risk_factors.append("Multiple failed login attempts")

            # Check user agent
            if await self._is_malicious_user_agent(user_agent):
                risk_score += self.risk_factors["malicious_user_agent"]
                risk_factors.append("Suspicious user agent")

            # Check time anomalies
            current_hour = datetime.now().hour
            user_timezone = await self._get_user_timezone(user_id)
            if user_timezone and not (9 <= current_hour <= 17):  # Outside business hours
                risk_score += self.risk_factors["time_anomaly"]
                risk_factors.append("Login outside normal hours")

            # Determine risk level
            if risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.3:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            return risk_score, risk_level, risk_factors

        except Exception as e:
            logger.error(f"Error assessing login risk: {e}")
            return 0.5, RiskLevel.MEDIUM, ["Risk assessment error"]

    async def _get_recent_logins(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get recent login history for user"""
        try:
            # This would fetch from database
            return []
        except Exception as e:
            logger.error(f"Error getting recent logins: {e}")
            return []

    async def _get_location_from_ip(self, ip_address: str) -> str:
        """Get location from IP address"""
        try:
            # This would use a geolocation service
            return "Unknown"
        except Exception as e:
            logger.error(f"Error getting location from IP: {e}")
            return "Unknown"

    async def _calculate_distance(self, location1: str, location2: str) -> float:
        """Calculate distance between two locations"""
        # This would use geolocation distance calculation
        return 0.0

    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            # This would check against threat intelligence feeds
            return False
        except Exception as e:
            logger.error(f"Error checking suspicious IP: {e}")
            return False

    async def _get_failed_attempts(self, user_id: str, ip_address: str, hours: int) -> int:
        """Get failed login attempts"""
        try:
            # This would fetch from database
            return 0
        except Exception as e:
            logger.error(f"Error getting failed attempts: {e}")
            return 0

    async def _is_malicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is malicious"""
        try:
            malicious_patterns = [
                'bot', 'crawler', 'spider', 'scanner', 'tester',
                'curl', 'wget', 'python-requests'
            ]
            return any(pattern.lower() in user_agent.lower() for pattern in malicious_patterns)
        except Exception as e:
            logger.error(f"Error checking malicious user agent: {e}")
            return False

    async def _get_user_timezone(self, user_id: str) -> Optional[str]:
        """Get user timezone"""
        try:
            # This would fetch from database
            return None
        except Exception as e:
            logger.error(f"Error getting user timezone: {e}")
            return None

    async def generate_totp_secret(self) -> str:
        """Generate TOTP secret"""
        try:
            return pyotp.random_base32()
        except Exception as e:
            logger.error(f"Error generating TOTP secret: {e}")
            raise

    async def generate_totp_qr_code(self, secret: str, user_email: str, app_name: str = "DeepAgent") -> str:
        """Generate TOTP QR code as base64 image"""
        try:
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(user_email, issuer_name=app_name)

            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            # Convert to base64
            img_buffer = BytesIO()
            qr.make_image(fill_color="black", back_color="white").save(img_buffer, format="PNG")
            img_buffer.seek(0)
            qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            return f"data:image/png;base64,{qr_base64}"

        except Exception as e:
            logger.error(f"Error generating TOTP QR code: {e}")
            raise

    async def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # Allow 1 step window
        except Exception as e:
            logger.error(f"Error verifying TOTP: {e}")
            return False

    async def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA"""
        try:
            codes = []
            for _ in range(count):
                code = ''.join(secrets.choice('0123456789') for _ in range(8))
                codes.append(code)
            return codes
        except Exception as e:
            logger.error(f"Error generating backup codes: {e}")
            raise

    async def create_mfa_device(self, user_id: str, mfa_type: MFAType, name: str) -> MFADevice:
        """Create MFA device for user"""
        try:
            device_id = f"mfa_{int(datetime.now().timestamp())}"
            secret = await self.generate_totp_secret()
            backup_codes = await self.generate_backup_codes()

            device = MFADevice(
                id=device_id,
                user_id=user_id,
                mfa_type=mfa_type,
                name=name,
                secret=secret,
                backup_codes=backup_codes
            )

            # Store device
            self.mfa_devices[device_id] = device

            return device

        except Exception as e:
            logger.error(f"Error creating MFA device: {e}")
            raise

    async def verify_mfa(self, user_id: str, device_id: str, token: str) -> bool:
        """Verify MFA token"""
        try:
            device = self.mfa_devices.get(device_id)
            if not device or not device.enabled:
                return False

            if device.mfa_type == MFAType.TOTP:
                return await self.verify_totp(device.secret, token)
            elif device.mfa_type == MFAType.BACKUP:
                return token in device.backup_codes

            return False

        except Exception as e:
            logger.error(f"Error verifying MFA: {e}")
            return False

    async def create_session(self, user_id: str, security_context: SecurityContext) -> str:
        """Create secure session for user"""
        try:
            session_id = f"session_{secrets.token_urlsafe(32)}"
            session_timeout = security_context.session_timeout

            # Store session
            session_data = {
                'user_id': user_id,
                'security_context': {
                    'ip_address': security_context.ip_address,
                    'user_agent': security_context.user_agent,
                    'location': security_context.location,
                    'device_fingerprint': security_context.device_fingerprint,
                    'risk_level': security_context.risk_level.value,
                    'mfa_verified': security_context.mfa_verified,
                    'permissions': security_context.permissions
                },
                'created_at': datetime.now().isoformat(),
                'expires_at': session_timeout.isoformat()
            }

            # Store in Redis
            await self.redis_manager.set(
                f"session:{session_id}",
                json.dumps(session_data),
                expire=int((session_timeout - datetime.now()).total_seconds())
            )

            # Add to active sessions
            self.active_sessions[session_id] = security_context

            return session_id

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    async def validate_session(self, session_id: str) -> Optional[SecurityContext]:
        """Validate session and return security context"""
        try:
            # Get session from Redis
            session_data = await self.redis_manager.get(f"session:{session_id}")
            if not session_data:
                return None

            session = json.loads(session_data)

            # Check expiration
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.now() > expires_at:
                await self.delete_session(session_id)
                return None

            # Create security context
            context_data = session['security_context']
            security_context = SecurityContext(
                user_id=session['user_id'],
                session_id=session_id,
                ip_address=context_data['ip_address'],
                user_agent=context_data['user_agent'],
                location=context_data['location'],
                device_fingerprint=context_data['device_fingerprint'],
                risk_level=RiskLevel(context_data['risk_level']),
                mfa_verified=context_data.get('mfa_verified', False),
                permissions=context_data.get('permissions', [])
            )

            return security_context

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            # Remove from Redis
            await self.redis_manager.delete(f"session:{session_id}")

            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            return True

        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    async def record_auth_attempt(self, attempt: AuthAttempt):
        """Record authentication attempt"""
        try:
            # Store in Redis for recent attempts
            attempt_key = f"auth_attempt:{attempt.user_id}:{int(attempt.timestamp.timestamp())}"
            await self.redis_manager.set(
                attempt_key,
                json.dumps({
                    'id': attempt.id,
                    'user_id': attempt.user_id,
                    'method': attempt.method.value,
                    'success': attempt.success,
                    'ip_address': attempt.ip_address,
                    'user_agent': attempt.user_agent,
                    'location': attempt.location,
                    'device_fingerprint': attempt.device_fingerprint,
                    'risk_score': attempt.risk_score,
                    'timestamp': attempt.timestamp.isoformat()
                }),
                expire=86400 * 30  # 30 days
            )

            # Update attempt counters
            if not attempt.success:
                counter_key = f"failed_attempts:{attempt.user_id}:{attempt.ip_address}"
                await self.redis_manager.incr(counter_key)
                await self.redis_manager.expire(counter_key, 3600)  # 1 hour

        except Exception as e:
            logger.error(f"Error recording auth attempt: {e}")

    async def check_account_lockout(self, user_id: str, ip_address: str) -> Tuple[bool, Optional[datetime]]:
        """Check if account is locked out"""
        try:
            lockout_key = f"account_lockout:{user_id}"
            lockout_data = await self.redis_manager.get(lockout_key)

            if lockout_data:
                lockout_info = json.loads(lockout_data)
                lockout_until = datetime.fromisoformat(lockout_info['until'])

                if datetime.now() < lockout_until:
                    return True, lockout_until
                else:
                    # Lockout expired
                    await self.redis_manager.delete(lockout_key)
                    return False, None

            return False, None

        except Exception as e:
            logger.error(f"Error checking account lockout: {e}")
            return False, None

    async def lock_account(self, user_id: str, duration_minutes: int = 30):
        """Lock user account"""
        try:
            lockout_key = f"account_lockout:{user_id}"
            lockout_until = datetime.now() + timedelta(minutes=duration_minutes)

            lockout_data = {
                'user_id': user_id,
                'until': lockout_until.isoformat(),
                'reason': 'too_many_failed_attempts'
            }

            await self.redis_manager.set(
                lockout_key,
                json.dumps(lockout_data),
                expire=duration_minutes * 60
            )

            logger.warning(f"Account locked for user {user_id} until {lockout_until}")

        except Exception as e:
            logger.error(f"Error locking account: {e}")

    async def unlock_account(self, user_id: str):
        """Unlock user account"""
        try:
            lockout_key = f"account_lockout:{user_id}"
            await self.redis_manager.delete(lockout_key)

            # Clear failed attempt counters
            await self.redis_manager.delete(f"failed_attempts:{user_id}")

            logger.info(f"Account unlocked for user {user_id}")

        except Exception as e:
            logger.error(f"Error unlocking account: {e}")

    async def generate_device_fingerprint(self, user_agent: str, ip_address: str,
                                       additional_data: Dict[str, str] = None) -> str:
        """Generate device fingerprint"""
        try:
            fingerprint_data = {
                'user_agent': user_agent,
                'ip_address': ip_address,
                'screen_resolution': additional_data.get('screen_resolution', '') if additional_data else '',
                'platform': additional_data.get('platform', '') if additional_data else '',
                'language': additional_data.get('language', '') if additional_data else '',
                'timezone': additional_data.get('timezone', '') if additional_data else ''
            }

            fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()

            return fingerprint_hash

        except Exception as e:
            logger.error(f"Error generating device fingerprint: {e}")
            return secrets.token_urlsafe(32)

    async def authenticate_user(self, username: str, password: str, ip_address: str,
                             user_agent: str, additional_data: Dict[str, str] = None) -> Dict[str, Any]:
        """Authenticate user with comprehensive security checks"""
        auth_result = {
            'success': False,
            'session_id': None,
            'mfa_required': False,
            'risk_level': None,
            'security_context': None,
            'error': None
        }

        try:
            # Generate device fingerprint
            device_fingerprint = await self.generate_device_fingerprint(user_agent, ip_address, additional_data)

            # Get user from database
            user = await self._get_user_by_username(username)
            if not user:
                auth_result['error'] = "Invalid username or password"
                return auth_result

            # Check account lockout
            is_locked, lockout_until = await self.check_account_lockout(user.id, ip_address)
            if is_locked:
                auth_result['error'] = f"Account locked until {lockout_until}"
                return auth_result

            # Verify password
            if not await self.verify_password(password, user.hashed_password):
                # Record failed attempt
                attempt = AuthAttempt(
                    id=f"attempt_{int(datetime.now().timestamp())}",
                    user_id=user.id,
                    method=AuthMethod.PASSWORD,
                    success=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_fingerprint=device_fingerprint
                )
                await self.record_auth_attempt(attempt)

                # Check if account should be locked
                failed_attempts = await self._get_failed_attempts(user.id, ip_address, hours=1)
                if failed_attempts >= 5:
                    await self.lock_account(user.id)

                auth_result['error'] = "Invalid username or password"
                return auth_result

            # Assess login risk
            risk_score, risk_level, risk_factors = await self.assess_login_risk(
                user.id, ip_address, user_agent, device_fingerprint
            )

            # Create security context
            security_context = SecurityContext(
                user_id=user.id,
                session_id="",  # Will be set after MFA if required
                ip_address=ip_address,
                user_agent=user_agent,
                location=await self._get_location_from_ip(ip_address),
                device_fingerprint=device_fingerprint,
                risk_level=risk_level,
                auth_methods=[AuthMethod.PASSWORD],
                mfa_required=risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] or user.mfa_enabled,
                permissions=user.permissions,
                session_timeout=datetime.now() + timedelta(hours=24)
            )

            # Check if MFA is required
            if security_context.mfa_required and not security_context.mfa_verified:
                auth_result['mfa_required'] = True
                auth_result['security_context'] = security_context
                auth_result['risk_level'] = risk_level
                return auth_result

            # Create session
            session_id = await self.create_session(user.id, security_context)
            security_context.session_id = session_id

            # Record successful attempt
            attempt = AuthAttempt(
                id=f"attempt_{int(datetime.now().timestamp())}",
                user_id=user.id,
                method=AuthMethod.PASSWORD,
                success=True,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                risk_score=risk_score
            )
            await self.record_auth_attempt(attempt)

            auth_result['success'] = True
            auth_result['session_id'] = session_id
            auth_result['security_context'] = security_context
            auth_result['risk_level'] = risk_level

            return auth_result

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            auth_result['error'] = str(e)
            return auth_result

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        # This would fetch from database
        return None

    async def verify_mfa_and_complete_auth(self, user_id: str, session_id: str,
                                        device_id: str, token: str) -> Dict[str, Any]:
        """Verify MFA and complete authentication"""
        auth_result = {
            'success': False,
            'session_id': None,
            'error': None
        }

        try:
            # Verify MFA token
            if not await self.verify_mfa(user_id, device_id, token):
                auth_result['error'] = "Invalid MFA token"
                return auth_result

            # Get temporary security context
            security_context = await self.validate_session(session_id)
            if not security_context:
                auth_result['error'] = "Session expired"
                return auth_result

            # Update security context
            security_context.mfa_verified = True
            security_context.auth_methods.append(AuthMethod.OTP)

            # Create new session
            new_session_id = await self.create_session(user_id, security_context)
            security_context.session_id = new_session_id

            # Delete temporary session
            await self.delete_session(session_id)

            auth_result['success'] = True
            auth_result['session_id'] = new_session_id

            return auth_result

        except Exception as e:
            logger.error(f"Error completing MFA authentication: {e}")
            auth_result['error'] = str(e)
            return auth_result