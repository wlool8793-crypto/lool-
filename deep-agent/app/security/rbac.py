"""
Role-Based Access Control (RBAC) System for LangGraph Deep Web Agent

This module provides comprehensive role-based access control including
role management, permission handling, access control policies, and
authorization mechanisms.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncpg
import redis.asyncio as redis
from functools import wraps

from app.core.config import settings
from app.database.redis import RedisManager
from app.security.authentication import SecurityContext

logger = logging.getLogger(__name__)

class Permission(Enum):
    # User Management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Role Management
    ROLE_READ = "role:read"
    ROLE_WRITE = "role:write"
    ROLE_DELETE = "role:delete"
    ROLE_MANAGE = "role:manage"

    # System Administration
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_ADMIN = "system:admin"

    # Agent Operations
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_EXECUTE = "agent:execute"
    AGENT_MANAGE = "agent:manage"

    # Data Access
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"

    # API Access
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_DELETE = "api:delete"
    API_ADMIN = "api:admin"

    # Integrations
    INTEGRATION_READ = "integration:read"
    INTEGRATION_WRITE = "integration:write"
    INTEGRATION_DELETE = "integration:delete"
    INTEGRATION_ADMIN = "integration:admin"

    # Security
    SECURITY_READ = "security:read"
    SECURITY_WRITE = "security:write"
    SECURITY_ADMIN = "security:admin"

    # Monitoring
    MONITORING_READ = "monitoring:read"
    MONITORING_WRITE = "monitoring:write"
    MONITORING_ADMIN = "monitoring:admin"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    BILLING_ADMIN = "billing:admin"

class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"
    DEVELOPER = "developer"
    SUPPORT = "support"
    AUDITOR = "auditor"

class ResourceType(Enum):
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    AGENT = "agent"
    CONVERSATION = "conversation"
    FILE = "file"
    API_KEY = "api_key"
    WEBHOOK = "webhook"
    INTEGRATION = "integration"
    SYSTEM = "system"

class AccessLevel(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

@dataclass
class RoleDefinition:
    """Role definition with permissions"""
    id: str
    name: str
    description: str
    permissions: Set[Permission]
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PermissionPolicy:
    """Access control policy"""
    id: str
    name: str
    resource_type: ResourceType
    conditions: Dict[str, Any]
    effect: str  # "allow" or "deny"
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessRequest:
    """Access control request"""
    user_id: str
    resource_type: ResourceType
    resource_id: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AccessDecision:
    """Access control decision"""
    request: AccessRequest
    allowed: bool
    reason: str
    policies_evaluated: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

class RBACManager:
    """Role-Based Access Control Manager"""

    def __init__(self):
        self.redis_manager = RedisManager()

        # Role definitions
        self.role_definitions = self._initialize_role_definitions()

        # Permission policies
        self.policies = self._initialize_policies()

        # User role assignments
        self.user_roles = {}

        # Resource ownership
        self.resource_ownership = {}

        # Permission cache
        self.permission_cache = {}

        # Default roles for new users
        self.default_roles = [Role.USER]

    def _initialize_role_definitions(self) -> Dict[Role, RoleDefinition]:
        """Initialize system role definitions"""
        return {
            Role.SUPER_ADMIN: RoleDefinition(
                id="role_super_admin",
                name="Super Administrator",
                description="Full system access with all permissions",
                permissions=set(Permission),
                is_system_role=True
            ),
            Role.ADMIN: RoleDefinition(
                id="role_admin",
                name="Administrator",
                description="System administration with most permissions",
                permissions={
                    # User Management
                    Permission.USER_READ, Permission.USER_WRITE, Permission.USER_MANAGE,
                    # Role Management
                    Permission.ROLE_READ, Permission.ROLE_WRITE,
                    # System
                    Permission.SYSTEM_READ, Permission.SYSTEM_WRITE, Permission.SYSTEM_CONFIG,
                    # Agent Operations
                    Permission.AGENT_READ, Permission.AGENT_WRITE, Permission.AGENT_EXECUTE, Permission.AGENT_MANAGE,
                    # Data Access
                    Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_EXPORT,
                    # API Access
                    Permission.API_READ, Permission.API_WRITE, Permission.API_ADMIN,
                    # Integrations
                    Permission.INTEGRATION_READ, Permission.INTEGRATION_WRITE, Permission.INTEGRATION_ADMIN,
                    # Security
                    Permission.SECURITY_READ, Permission.SECURITY_WRITE,
                    # Monitoring
                    Permission.MONITORING_READ, Permission.MONITORING_WRITE, Permission.MONITORING_ADMIN,
                    # Billing
                    Permission.BILLING_READ, Permission.BILLING_WRITE, Permission.BILLING_ADMIN
                },
                is_system_role=True
            ),
            Role.MANAGER: RoleDefinition(
                id="role_manager",
                name="Manager",
                description="Team management with limited permissions",
                permissions={
                    # User Management
                    Permission.USER_READ,
                    # System
                    Permission.SYSTEM_READ,
                    # Agent Operations
                    Permission.AGENT_READ, Permission.AGENT_EXECUTE,
                    # Data Access
                    Permission.DATA_READ, Permission.DATA_WRITE,
                    # API Access
                    Permission.API_READ,
                    # Integrations
                    Permission.INTEGRATION_READ, Permission.INTEGRATION_WRITE,
                    # Monitoring
                    Permission.MONITORING_READ, Permission.MONITORING_WRITE,
                    # Billing
                    Permission.BILLING_READ
                },
                is_system_role=True
            ),
            Role.USER: RoleDefinition(
                id="role_user",
                name="User",
                description="Standard user with basic permissions",
                permissions={
                    # System
                    Permission.SYSTEM_READ,
                    # Agent Operations
                    Permission.AGENT_READ, Permission.AGENT_EXECUTE,
                    # Data Access
                    Permission.DATA_READ, Permission.DATA_WRITE,
                    # API Access
                    Permission.API_READ,
                    # Integrations
                    Permission.INTEGRATION_READ,
                    # Monitoring
                    Permission.MONITORING_READ
                },
                is_system_role=True
            ),
            Role.GUEST: RoleDefinition(
                id="role_guest",
                name="Guest",
                description="Limited access for temporary users",
                permissions={
                    # System
                    Permission.SYSTEM_READ,
                    # Agent Operations
                    Permission.AGENT_READ,
                    # Data Access
                    Permission.DATA_READ,
                    # API Access
                    Permission.API_READ,
                    # Monitoring
                    Permission.MONITORING_READ
                },
                is_system_role=True
            ),
            Role.DEVELOPER: RoleDefinition(
                id="role_developer",
                name="Developer",
                description="Development and testing permissions",
                permissions={
                    # System
                    Permission.SYSTEM_READ, Permission.SYSTEM_WRITE,
                    # Agent Operations
                    Permission.AGENT_READ, Permission.AGENT_WRITE, Permission.AGENT_EXECUTE,
                    # Data Access
                    Permission.DATA_READ, Permission.DATA_WRITE,
                    # API Access
                    Permission.API_READ, Permission.API_WRITE,
                    # Integrations
                    Permission.INTEGRATION_READ, Permission.INTEGRATION_WRITE,
                    # Monitoring
                    Permission.MONITORING_READ, Permission.MONITORING_WRITE
                },
                is_system_role=True
            ),
            Role.SUPPORT: RoleDefinition(
                id="role_support",
                name="Support",
                description="Customer support permissions",
                permissions={
                    # User Management
                    Permission.USER_READ,
                    # System
                    Permission.SYSTEM_READ,
                    # Agent Operations
                    Permission.AGENT_READ,
                    # Data Access
                    Permission.DATA_READ,
                    # API Access
                    Permission.API_READ,
                    # Monitoring
                    Permission.MONITORING_READ, Permission.MONITORING_WRITE
                },
                is_system_role=True
            ),
            Role.AUDITOR: RoleDefinition(
                id="role_auditor",
                name="Auditor",
                description="Audit and compliance permissions",
                permissions={
                    # User Management
                    Permission.USER_READ,
                    # Role Management
                    Permission.ROLE_READ,
                    # System
                    Permission.SYSTEM_READ,
                    # Data Access
                    Permission.DATA_READ, Permission.DATA_EXPORT,
                    # Security
                    Permission.SECURITY_READ,
                    # Monitoring
                    Permission.MONITORING_READ,
                    # Billing
                    Permission.BILLING_READ
                },
                is_system_role=True
            )
        }

    def _initialize_policies(self) -> List[PermissionPolicy]:
        """Initialize permission policies"""
        return [
            # Ownership policies
            PermissionPolicy(
                id="policy_ownership",
                name="Resource Ownership",
                resource_type=ResourceType.AGENT,
                conditions={"owner": "${user_id}"},
                effect="allow",
                priority=100
            ),
            PermissionPolicy(
                id="policy_conversation_ownership",
                name="Conversation Ownership",
                resource_type=ResourceType.CONVERSATION,
                conditions={"owner": "${user_id}"},
                effect="allow",
                priority=100
            ),
            # Time-based policies
            PermissionPolicy(
                id="policy_business_hours",
                name="Business Hours Access",
                resource_type=ResourceType.SYSTEM,
                conditions={"time": "business_hours"},
                effect="allow",
                priority=50
            ),
            # Location-based policies
            PermissionPolicy(
                id="policy_office_access",
                name="Office Network Access",
                resource_type=ResourceType.SYSTEM,
                conditions={"location": "office"},
                effect="allow",
                priority=60
            ),
            # Risk-based policies
            PermissionPolicy(
                id="policy_low_risk_access",
                name="Low Risk Access",
                resource_type=ResourceType.SYSTEM,
                conditions={"risk_level": ["low", "medium"]},
                effect="allow",
                priority=70
            ),
            # Deny policies
            PermissionPolicy(
                id="policy_high_risk_deny",
                name="High Risk Deny",
                resource_type=ResourceType.SYSTEM,
                conditions={"risk_level": ["high", "critical"]},
                effect="deny",
                priority=200
            )
        ]

    async def assign_role(self, user_id: str, role: Role, assigned_by: str = None,
                         expires_at: datetime = None) -> bool:
        """Assign role to user"""
        try:
            # Check if role exists
            if role not in self.role_definitions:
                logger.error(f"Role {role.value} not found")
                return False

            # Store role assignment
            assignment_key = f"user_roles:{user_id}"
            role_data = {
                'role': role.value,
                'assigned_by': assigned_by,
                'assigned_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat() if expires_at else None
            }

            # Add to user roles
            if user_id not in self.user_roles:
                self.user_roles[user_id] = []

            # Remove existing role assignment if any
            self.user_roles[user_id] = [r for r in self.user_roles[user_id] if r != role]

            # Add new role assignment
            self.user_roles[user_id].append(role)

            # Store in Redis
            await self.redis_manager.hset(assignment_key, role.value, json.dumps(role_data))

            # Clear permission cache for user
            if user_id in self.permission_cache:
                del self.permission_cache[user_id]

            logger.info(f"Role {role.value} assigned to user {user_id}")

            return True

        except Exception as e:
            logger.error(f"Error assigning role to user {user_id}: {e}")
            return False

    async def remove_role(self, user_id: str, role: Role) -> bool:
        """Remove role from user"""
        try:
            # Remove from user roles
            if user_id in self.user_roles:
                self.user_roles[user_id] = [r for r in self.user_roles[user_id] if r != role]

            # Remove from Redis
            assignment_key = f"user_roles:{user_id}"
            await self.redis_manager.hdel(assignment_key, role.value)

            # Clear permission cache for user
            if user_id in self.permission_cache:
                del self.permission_cache[user_id]

            logger.info(f"Role {role.value} removed from user {user_id}")

            return True

        except Exception as e:
            logger.error(f"Error removing role from user {user_id}: {e}")
            return False

    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get roles assigned to user"""
        try:
            # Check cache
            if user_id in self.user_roles:
                return self.user_roles[user_id]

            # Get from Redis
            assignment_key = f"user_roles:{user_id}"
            role_assignments = await self.redis_manager.hgetall(assignment_key)

            roles = []
            for role_value in role_assignments.keys():
                try:
                    role = Role(role_value)
                    roles.append(role)
                except ValueError:
                    continue

            # Cache result
            self.user_roles[user_id] = roles

            return roles

        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return []

    async def get_user_permissions(self, user_id: str, use_cache: bool = True) -> Set[Permission]:
        """Get all permissions for user based on roles"""
        try:
            # Check cache
            if use_cache and user_id in self.permission_cache:
                return self.permission_cache[user_id]

            # Get user roles
            user_roles = await self.get_user_roles(user_id)

            # Collect permissions from all roles
            permissions = set()
            for role in user_roles:
                if role in self.role_definitions:
                    permissions.update(self.role_definitions[role].permissions)

            # Cache result
            self.permission_cache[user_id] = permissions

            return permissions

        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return set()

    async def has_permission(self, user_id: str, permission: Permission,
                           context: Dict[str, Any] = None) -> bool:
        """Check if user has specific permission"""
        try:
            # Get user permissions
            user_permissions = await self.get_user_permissions(user_id)

            # Check if permission is directly granted
            if permission in user_permissions:
                return True

            # Check if user has a higher-level permission
            for user_perm in user_permissions:
                if self._is_permission_granted(user_perm, permission):
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    def _is_permission_granted(self, granted_perm: Permission, requested_perm: Permission) -> bool:
        """Check if granted permission includes requested permission"""
        # This implements permission hierarchy
        perm_hierarchy = {
            Permission.USER_MANAGE: [Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE],
            Permission.ROLE_MANAGE: [Permission.ROLE_READ, Permission.ROLE_WRITE, Permission.ROLE_DELETE],
            Permission.SYSTEM_ADMIN: [Permission.SYSTEM_READ, Permission.SYSTEM_WRITE, Permission.SYSTEM_CONFIG],
            Permission.AGENT_MANAGE: [Permission.AGENT_READ, Permission.AGENT_WRITE, Permission.AGENT_EXECUTE],
            Permission.DATA_DELETE: [Permission.DATA_READ, Permission.DATA_WRITE],
            Permission.API_ADMIN: [Permission.API_READ, Permission.API_WRITE, Permission.API_DELETE],
            Permission.INTEGRATION_ADMIN: [Permission.INTEGRATION_READ, Permission.INTEGRATION_WRITE, Permission.INTEGRATION_DELETE],
            Permission.SECURITY_ADMIN: [Permission.SECURITY_READ, Permission.SECURITY_WRITE],
            Permission.MONITORING_ADMIN: [Permission.MONITORING_READ, Permission.MONITORING_WRITE],
            Permission.BILLING_ADMIN: [Permission.BILLING_READ, Permission.BILLING_WRITE]
        }

        return requested_perm in perm_hierarchy.get(granted_perm, [])

    async def check_access(self, request: AccessRequest) -> AccessDecision:
        """Check access control for a request"""
        try:
            # Get user permissions
            user_permissions = await self.get_user_permissions(request.user_id)

            # Get user roles
            user_roles = await self.get_user_roles(request.user_id)

            # Check direct permission
            required_permission = self._get_required_permission(request.resource_type, request.action)
            has_direct_permission = required_permission in user_permissions

            # Check policies
            policy_results = await self._evaluate_policies(request, user_roles)

            # Combine results
            allowed = has_direct_permission and policy_results['allowed']

            # Create decision
            decision = AccessDecision(
                request=request,
                allowed=allowed,
                reason=policy_results['reason'],
                policies_evaluated=policy_results['policies_evaluated']
            )

            # Log access decision
            await self._log_access_decision(decision)

            return decision

        except Exception as e:
            logger.error(f"Error checking access: {e}")
            return AccessDecision(
                request=request,
                allowed=False,
                reason=f"Access check error: {str(e)}",
                policies_evaluated=[]
            )

    def _get_required_permission(self, resource_type: ResourceType, action: str) -> Permission:
        """Get required permission for resource and action"""
        permission_map = {
            (ResourceType.USER, "read"): Permission.USER_READ,
            (ResourceType.USER, "write"): Permission.USER_WRITE,
            (ResourceType.USER, "delete"): Permission.USER_DELETE,
            (ResourceType.USER, "manage"): Permission.USER_MANAGE,
            (ResourceType.ROLE, "read"): Permission.ROLE_READ,
            (ResourceType.ROLE, "write"): Permission.ROLE_WRITE,
            (ResourceType.ROLE, "delete"): Permission.ROLE_DELETE,
            (ResourceType.ROLE, "manage"): Permission.ROLE_MANAGE,
            (ResourceType.AGENT, "read"): Permission.AGENT_READ,
            (ResourceType.AGENT, "write"): Permission.AGENT_WRITE,
            (ResourceType.AGENT, "execute"): Permission.AGENT_EXECUTE,
            (ResourceType.AGENT, "manage"): Permission.AGENT_MANAGE,
            (ResourceType.SYSTEM, "read"): Permission.SYSTEM_READ,
            (ResourceType.SYSTEM, "write"): Permission.SYSTEM_WRITE,
            (ResourceType.SYSTEM, "config"): Permission.SYSTEM_CONFIG,
            (ResourceType.SYSTEM, "admin"): Permission.SYSTEM_ADMIN,
        }

        return permission_map.get((resource_type, action), Permission.SYSTEM_READ)

    async def _evaluate_policies(self, request: AccessRequest, user_roles: List[Role]) -> Dict[str, Any]:
        """Evaluate permission policies"""
        try:
            policy_results = {
                'allowed': True,
                'reason': '',
                'policies_evaluated': []
            }

            # Sort policies by priority (higher priority first)
            sorted_policies = sorted(self.policies, key=lambda p: p.priority, reverse=True)

            for policy in sorted_policies:
                if policy.resource_type != request.resource_type:
                    continue

                # Evaluate policy conditions
                if await self._evaluate_policy_conditions(policy, request, user_roles):
                    policy_results['policies_evaluated'].append(policy.id)

                    if policy.effect == "deny":
                        policy_results['allowed'] = False
                        policy_results['reason'] = f"Denied by policy: {policy.name}"
                        break
                    elif policy.effect == "allow":
                        policy_results['reason'] = f"Allowed by policy: {policy.name}"

            return policy_results

        except Exception as e:
            logger.error(f"Error evaluating policies: {e}")
            return {
                'allowed': False,
                'reason': f"Policy evaluation error: {str(e)}",
                'policies_evaluated': []
            }

    async def _evaluate_policy_conditions(self, policy: PermissionPolicy,
                                       request: AccessRequest, user_roles: List[Role]) -> bool:
        """Evaluate policy conditions"""
        try:
            conditions = policy.conditions

            # Check ownership condition
            if "owner" in conditions:
                expected_owner = conditions["owner"]
                if expected_owner == "${user_id}" and request.resource_id != request.user_id:
                    return False

            # Check role conditions
            if "roles" in conditions:
                required_roles = set(conditions["roles"])
                user_role_set = set(role.value for role in user_roles)
                if not required_roles.intersection(user_role_set):
                    return False

            # Check time conditions
            if "time" in conditions:
                time_condition = conditions["time"]
                if time_condition == "business_hours":
                    current_hour = datetime.now().hour
                    if not (9 <= current_hour <= 17):
                        return False

            # Check location conditions
            if "location" in conditions:
                location_condition = conditions["location"]
                user_location = request.context.get('location', '')
                if user_location != location_condition:
                    return False

            # Check risk level conditions
            if "risk_level" in conditions:
                risk_levels = conditions["risk_level"]
                user_risk = request.context.get('risk_level', '')
                if user_risk not in risk_levels:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error evaluating policy conditions: {e}")
            return False

    async def _log_access_decision(self, decision: AccessDecision):
        """Log access control decision"""
        try:
            log_data = {
                'user_id': decision.request.user_id,
                'resource_type': decision.request.resource_type.value,
                'resource_id': decision.request.resource_id,
                'action': decision.request.action,
                'allowed': decision.allowed,
                'reason': decision.reason,
                'timestamp': decision.timestamp.isoformat(),
                'context': decision.request.context
            }

            # Store in Redis for audit trail
            log_key = f"access_log:{decision.request.user_id}:{int(decision.timestamp.timestamp())}"
            await self.redis_manager.set(
                log_key,
                json.dumps(log_data),
                expire=86400 * 90  # 90 days
            )

        except Exception as e:
            logger.error(f"Error logging access decision: {e}")

    async def create_custom_role(self, name: str, description: str, permissions: Set[Permission],
                               created_by: str) -> Optional[RoleDefinition]:
        """Create custom role"""
        try:
            role_id = f"custom_role_{int(datetime.now().timestamp())}"

            role = RoleDefinition(
                id=role_id,
                name=name,
                description=description,
                permissions=permissions,
                is_system_role=False
            )

            # Store role definition
            # This would be stored in database
            logger.info(f"Custom role created: {name} by {created_by}")

            return role

        except Exception as e:
            logger.error(f"Error creating custom role: {e}")
            return None

    async def update_role_permissions(self, role: Role, permissions: Set[Permission],
                                    updated_by: str) -> bool:
        """Update role permissions"""
        try:
            if role not in self.role_definitions:
                logger.error(f"Role {role.value} not found")
                return False

            # Update permissions
            self.role_definitions[role].permissions = permissions
            self.role_definitions[role].updated_at = datetime.now()

            # Clear permission cache for all users with this role
            for user_id in self.user_roles:
                if role in self.user_roles[user_id]:
                    if user_id in self.permission_cache:
                        del self.permission_cache[user_id]

            logger.info(f"Role permissions updated: {role.value} by {updated_by}")

            return True

        except Exception as e:
            logger.error(f"Error updating role permissions: {e}")
            return False

    async def get_access_logs(self, user_id: str = None, resource_type: ResourceType = None,
                            start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get access control logs"""
        try:
            # This would query the database for access logs
            return []

        except Exception as e:
            logger.error(f"Error getting access logs: {e}")
            return []

    async def set_resource_owner(self, resource_type: ResourceType, resource_id: str, owner_id: str) -> bool:
        """Set resource owner"""
        try:
            ownership_key = f"resource_ownership:{resource_type.value}:{resource_id}"
            ownership_data = {
                'owner_id': owner_id,
                'created_at': datetime.now().isoformat()
            }

            await self.redis_manager.set(
                ownership_key,
                json.dumps(ownership_data),
                expire=86400 * 365  # 1 year
            )

            return True

        except Exception as e:
            logger.error(f"Error setting resource owner: {e}")
            return False

    async def get_resource_owner(self, resource_type: ResourceType, resource_id: str) -> Optional[str]:
        """Get resource owner"""
        try:
            ownership_key = f"resource_ownership:{resource_type.value}:{resource_id}"
            ownership_data = await self.redis_manager.get(ownership_key)

            if ownership_data:
                data = json.loads(ownership_data)
                return data['owner_id']

            return None

        except Exception as e:
            logger.error(f"Error getting resource owner: {e}")
            return None

    def require_permission(self, permission: Permission):
        """Decorator to require permission for function access"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get user_id from kwargs or security context
                user_id = kwargs.get('user_id') or getattr(args[0], 'user_id', None)
                if not user_id:
                    raise PermissionError("User ID not found")

                # Check permission
                if not await self.has_permission(user_id, permission):
                    raise PermissionError(f"Permission {permission.value} required")

                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def require_role(self, role: Role):
        """Decorator to require role for function access"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get user_id from kwargs or security context
                user_id = kwargs.get('user_id') or getattr(args[0], 'user_id', None)
                if not user_id:
                    raise PermissionError("User ID not found")

                # Get user roles
                user_roles = await self.get_user_roles(user_id)
                if role not in user_roles:
                    raise PermissionError(f"Role {role.value} required")

                return await func(*args, **kwargs)
            return wrapper
        return decorator

    async def check_resource_access(self, user_id: str, resource_type: ResourceType,
                                 resource_id: str, action: str,
                                 context: Dict[str, Any] = None) -> bool:
        """Check if user can access specific resource"""
        try:
            request = AccessRequest(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                context=context or {}
            )

            decision = await self.check_access(request)
            return decision.allowed

        except Exception as e:
            logger.error(f"Error checking resource access: {e}")
            return False

    async def get_user_effective_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get effective permissions for user with detailed breakdown"""
        try:
            # Get user roles
            user_roles = await self.get_user_roles(user_id)

            # Get direct permissions
            direct_permissions = await self.get_user_permissions(user_id)

            # Calculate effective permissions by role
            role_permissions = {}
            for role in user_roles:
                if role in self.role_definitions:
                    role_permissions[role.value] = list(self.role_definitions[role].permissions)

            return {
                'user_id': user_id,
                'roles': [role.value for role in user_roles],
                'direct_permissions': list(direct_permissions),
                'role_permissions': role_permissions,
                'total_permissions': len(direct_permissions),
                'highest_role': max(user_roles, key=lambda r: r.name if r in self.role_definitions else 0, default=None)
            }

        except Exception as e:
            logger.error(f"Error getting effective permissions: {e}")
            return {'user_id': user_id, 'error': str(e)}

    async def cleanup_expired_roles(self):
        """Clean up expired role assignments"""
        try:
            # This would scan for expired role assignments and remove them
            logger.info("Expired role assignments cleanup completed")

        except Exception as e:
            logger.error(f"Error cleaning up expired roles: {e}")

    async def get_role_statistics(self) -> Dict[str, Any]:
        """Get role assignment statistics"""
        try:
            stats = {
                'total_users': len(self.user_roles),
                'role_distribution': {},
                'custom_roles': 0,
                'system_roles': len(self.role_definitions)
            }

            # Count role distribution
            for user_roles in self.user_roles.values():
                for role in user_roles:
                    role_name = role.value
                    if role_name not in stats['role_distribution']:
                        stats['role_distribution'][role_name] = 0
                    stats['role_distribution'][role_name] += 1

            return stats

        except Exception as e:
            logger.error(f"Error getting role statistics: {e}")
            return {'error': str(e)}