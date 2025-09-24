"""
Security Module

Comprehensive security system providing:
- Advanced authentication with MFA and risk assessment
- Role-based access control (RBAC)
- Threat detection and security monitoring
- Data encryption and protection
- Audit logging and compliance reporting
- Security configuration management
"""

from .authentication import (
    AuthenticationConfig,
    AdvancedAuthManager,
    MFAManager,
    RiskAssessmentManager,
    DeviceFingerprintingManager
)

from .rbac import (
    RBACConfig,
    RBACManager,
    Role,
    Permission,
    Policy
)

from .threat_detection import (
    ThreatDetectionConfig,
    ThreatDetector,
    DetectionRule,
    AlertManager
)

from .encryption import (
    EncryptionConfig,
    EncryptionManager,
    EncryptionKey
)

from .data_protection import (
    DataProtectionManager,
    DataCategory,
    ConsentType,
    RetentionPolicy,
    ConsentRecord,
    DataSubject
)

from .audit_logging import (
    AuditLogger,
    AuditEventType,
    AuditSeverity,
    ComplianceFramework,
    AuditEvent,
    AuditLog
)

from .security_config import (
    SecurityConfigManager,
    SecurityLevel,
    SecurityPolicy,
    ComplianceRequirement
)

from .api_security import (
    APISecurityManager,
    APIKeyManager,
    RateLimiter,
    RateLimitStrategy,
    APIKey,
    APIKeyStatus,
    SecurityRule
)

from .api_gateway import (
    APIGateway,
    APIGatewayConfig,
    APIEndpoint,
    CORSConfig,
    CSPConfig,
    HTTPMethod,
    SecurityLevel as APISecurityLevel
)

__all__ = [
    # Authentication
    'AuthenticationConfig',
    'AdvancedAuthManager',
    'MFAManager',
    'RiskAssessmentManager',
    'DeviceFingerprintingManager',

    # RBAC
    'RBACConfig',
    'RBACManager',
    'Role',
    'Permission',
    'Policy',

    # Threat Detection
    'ThreatDetectionConfig',
    'ThreatDetector',
    'DetectionRule',
    'AlertManager',

    # Encryption
    'EncryptionConfig',
    'EncryptionManager',
    'EncryptionKey',

    # Data Protection
    'DataProtectionManager',
    'DataCategory',
    'ConsentType',
    'RetentionPolicy',
    'ConsentRecord',
    'DataSubject',

    # Audit Logging
    'AuditLogger',
    'AuditEventType',
    'AuditSeverity',
    'ComplianceFramework',
    'AuditEvent',
    'AuditLog',

    # Security Configuration
    'SecurityConfigManager',
    'SecurityLevel',
    'SecurityPolicy',
    'ComplianceRequirement',

    # API Security
    'APISecurityManager',
    'APIKeyManager',
    'RateLimiter',
    'RateLimitStrategy',
    'APIKey',
    'APIKeyStatus',
    'SecurityRule',

    # API Gateway
    'APIGateway',
    'APIGatewayConfig',
    'APIEndpoint',
    'CORSConfig',
    'CSPConfig',
    'HTTPMethod',
    'APISecurityLevel'
]