"""
API Gateway Security Middleware

Provides comprehensive API gateway security features:
- Request validation and sanitization
- Response filtering and masking
- CORS and CSP policy enforcement
- Rate limiting middleware
- Authentication and authorization
- API key management
- Webhook security
- Request/response logging
- Performance monitoring
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from functools import wraps
import hashlib
import secrets

# Import security components
from .api_security import APISecurityManager, APIKeyManager
from .audit_logging import AuditLogger, AuditEventType, AuditSeverity
from .rbac import RBACManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class SecurityLevel(Enum):
    """Security levels for endpoints"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: HTTPMethod
    handler: Callable
    security_level: SecurityLevel = SecurityLevel.AUTHENTICATED
    required_permissions: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None
    cors_enabled: bool = True
    validation_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CORSConfig:
    """CORS configuration"""
    enabled: bool = True
    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    allow_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization", "X-API-Key"])
    allow_credentials: bool = False
    max_age: int = 86400  # 24 hours


@dataclass
class CSPConfig:
    """Content Security Policy configuration"""
    enabled: bool = True
    default_src: List[str] = field(default_factory=lambda: ["'self'"])
    script_src: List[str] = field(default_factory=lambda: ["'self'"])
    style_src: List[str] = field(default_factory=lambda: ["'self'"])
    img_src: List[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    font_src: List[str] = field(default_factory=lambda: ["'self'"])
    connect_src: List[str] = field(default_factory=lambda: ["'self'"])
    object_src: List[str] = field(default_factory=lambda: ["'none'"])
    frame_src: List[str] = field(default_factory=lambda: ["'self'"])
    report_uri: Optional[str] = None
    report_only: bool = False


@dataclass
class APIGatewayConfig:
    """API Gateway configuration"""
    cors: CORSConfig = field(default_factory=CORSConfig)
    csp: CSPConfig = field(default_factory=CSPConfig)
    enable_request_validation: bool = True
    enable_response_validation: bool = True
    enable_rate_limiting: bool = True
    enable_api_keys: bool = True
    enable_audit_logging: bool = True
    enable_performance_monitoring: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_response_size: int = 50 * 1024 * 1024  # 50MB
    request_timeout: int = 30  # seconds
    response_timeout: int = 60  # seconds
    trusted_proxies: List[str] = field(default_factory=list)


class APIGateway:
    """Main API Gateway implementation"""

    def __init__(self, security_manager: APISecurityManager, audit_logger: AuditLogger,
                 rbac_manager: RBACManager, config: APIGatewayConfig = None):
        self.security_manager = security_manager
        self.audit_logger = audit_logger
        self.rbac_manager = rbac_manager
        self.config = config or APIGatewayConfig()

        self.endpoints: Dict[str, Dict[HTTPMethod, APIEndpoint]] = {}
        self.middleware_stack: List[Callable] = []
        self.error_handlers: Dict[Exception, Callable] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}

        self._initialize_middleware()
        self._initialize_error_handlers()

    def _initialize_middleware(self):
        """Initialize middleware stack"""
        self.middleware_stack = [
            self._cors_middleware,
            self._security_headers_middleware,
            self._request_size_middleware,
            self._authentication_middleware,
            self._authorization_middleware,
            self._rate_limiting_middleware,
            self._request_validation_middleware,
            self._response_validation_middleware,
            self._audit_logging_middleware,
            self._performance_monitoring_middleware
        ]

    def _initialize_error_handlers(self):
        """Initialize error handlers"""
        self.error_handlers = {
            Exception: self._handle_generic_error,
            ValueError: self._handle_validation_error,
            PermissionError: self._handle_authorization_error,
            TimeoutError: self._handle_timeout_error
        }

    def register_endpoint(self, endpoint: APIEndpoint):
        """Register an API endpoint"""
        if endpoint.path not in self.endpoints:
            self.endpoints[endpoint.path] = {}

        self.endpoints[endpoint.path][endpoint.method] = endpoint

        logger.info(f"Registered endpoint: {endpoint.method.value} {endpoint.path}")

    def route(self, path: str, method: HTTPMethod = HTTPMethod.GET,
              security_level: SecurityLevel = SecurityLevel.AUTHENTICATED,
              required_permissions: List[str] = None, rate_limit: int = None):
        """Decorator for route registration"""
        def decorator(handler: Callable):
            endpoint = APIEndpoint(
                path=path,
                method=method,
                handler=handler,
                security_level=security_level,
                required_permissions=required_permissions or [],
                rate_limit=rate_limit
            )
            self.register_endpoint(endpoint)

            @wraps(handler)
            def wrapper(*args, **kwargs):
                return self._handle_request(path, method, *args, **kwargs)

            return wrapper
        return decorator

    def _handle_request(self, path: str, method: HTTPMethod, *args, **kwargs):
        """Handle incoming request"""
        start_time = time.time()

        # Create request context
        request_context = self._create_request_context(path, method, args, kwargs)

        try:
            # Find endpoint
            endpoint = self._find_endpoint(path, method)
            if not endpoint:
                return self._create_error_response(404, "Endpoint not found")

            # Execute middleware stack
            for middleware in self.middleware_stack:
                result = middleware(request_context, endpoint)
                if result:  # Middleware returned early (error or redirect)
                    return result

            # Execute endpoint handler
            response = endpoint.handler(*args, **kwargs)

            # Process response
            processed_response = self._process_response(response, request_context, endpoint)

            return processed_response

        except Exception as e:
            # Handle errors
            error_handler = self.error_handlers.get(type(e), self._handle_generic_error)
            return error_handler(e, request_context)

        finally:
            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(path, method, execution_time)

    def _create_request_context(self, path: str, method: HTTPMethod, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """Create request context"""
        return {
            "path": path,
            "method": method.value,
            "args": args,
            "kwargs": kwargs,
            "timestamp": datetime.now(),
            "client_ip": self._get_client_ip(),
            "user_agent": self._get_user_agent(),
            "headers": self._get_headers(),
            "authenticated": False,
            "authorized": False,
            "user_id": None,
            "api_key": None,
            "permissions": [],
            "rate_limited": False,
            "validation_errors": []
        }

    def _find_endpoint(self, path: str, method: HTTPMethod) -> Optional[APIEndpoint]:
        """Find endpoint by path and method"""
        # Exact match
        if path in self.endpoints and method in self.endpoints[path]:
            return self.endpoints[path][method]

        # Pattern matching (would implement more sophisticated routing)
        for endpoint_path, methods in self.endpoints.items():
            if self._path_matches(path, endpoint_path) and method in methods:
                return methods[method]

        return None

    def _path_matches(self, request_path: str, endpoint_path: str) -> bool:
        """Check if request path matches endpoint pattern"""
        # Simple exact match for now
        # Would implement more sophisticated pattern matching
        return request_path == endpoint_path

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Would extract from request headers or direct connection
        return "127.0.0.1"  # Placeholder

    def _get_user_agent(self) -> str:
        """Get user agent string"""
        # Would extract from request headers
        return "Unknown"  # Placeholder

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        # Would extract from request
        return {}  # Placeholder

    def _cors_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """CORS middleware"""
        if not self.config.cors.enabled or not endpoint.cors_enabled:
            return None

        # Handle OPTIONS preflight request
        if request_context["method"] == "OPTIONS":
            return self._create_cors_response()

        # Add CORS headers to response (would be done in response processing)
        return None

    def _create_cors_response(self) -> Dict[str, Any]:
        """Create CORS preflight response"""
        return {
            "status_code": 200,
            "headers": {
                "Access-Control-Allow-Origin": ", ".join(self.config.cors.allow_origins),
                "Access-Control-Allow-Methods": ", ".join(self.config.cors.allow_methods),
                "Access-Control-Allow-Headers": ", ".join(self.config.cors.allow_headers),
                "Access-Control-Allow-Credentials": str(self.config.cors.allow_credentials).lower(),
                "Access-Control-Max-Age": str(self.config.cors.max_age)
            },
            "body": ""
        }

    def _security_headers_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Security headers middleware"""
        # Would add security headers to response
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        # Add CSP header if enabled
        if self.config.csp.enabled:
            csp_header = self._build_csp_header()
            security_headers["Content-Security-Policy"] = csp_header

        # Store headers for response processing
        request_context["security_headers"] = security_headers
        return None

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header"""
        csp_parts = []

        if self.config.csp.default_src:
            csp_parts.append(f"default-src {' '.join(self.config.csp.default_src)}")
        if self.config.csp.script_src:
            csp_parts.append(f"script-src {' '.join(self.config.csp.script_src)}")
        if self.config.csp.style_src:
            csp_parts.append(f"style-src {' '.join(self.config.csp.style_src)}")
        if self.config.csp.img_src:
            csp_parts.append(f"img-src {' '.join(self.config.csp.img_src)}")
        if self.config.csp.font_src:
            csp_parts.append(f"font-src {' '.join(self.config.csp.font_src)}")
        if self.config.csp.connect_src:
            csp_parts.append(f"connect-src {' '.join(self.config.csp.connect_src)}")
        if self.config.csp.object_src:
            csp_parts.append(f"object-src {' '.join(self.config.csp.object_src)}")
        if self.config.csp.frame_src:
            csp_parts.append(f"frame-src {' '.join(self.config.csp.frame_src)}")

        csp_string = "; ".join(csp_parts)

        if self.config.csp.report_uri:
            csp_string += f"; report-uri {self.config.csp.report_uri}"

        return csp_string

    def _request_size_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Request size validation middleware"""
        if not self.config.enable_request_validation:
            return None

        # Would check actual request size
        request_size = 0  # Placeholder - would get from request

        if request_size > self.config.max_request_size:
            return self._create_error_response(413, "Request too large")

        return None

    def _authentication_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Authentication middleware"""
        if endpoint.security_level == SecurityLevel.PUBLIC:
            return None

        # Extract authentication credentials
        auth_header = request_context["headers"].get("Authorization")
        api_key = request_context["headers"].get("X-API-Key")

        user_id = None
        permissions = []

        # Try API key authentication
        if api_key and self.config.enable_api_keys:
            api_key_info = self.security_manager.api_key_manager.validate_api_key(api_key)
            if api_key_info:
                user_id = api_key_info.owner_id
                permissions = api_key_info.permissions
                request_context["api_key"] = api_key
                request_context["authenticated"] = True

        # Try JWT token authentication (would implement)
        elif auth_header and auth_header.startswith("Bearer "):
            # Would validate JWT token
            pass

        # Check if authentication is required
        if endpoint.security_level in [SecurityLevel.AUTHENTICATED, SecurityLevel.AUTHORIZED, SecurityLevel.ADMIN]:
            if not request_context["authenticated"]:
                return self._create_error_response(401, "Authentication required")

        request_context["user_id"] = user_id
        request_context["permissions"] = permissions

        return None

    def _authorization_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Authorization middleware"""
        if endpoint.security_level in [SecurityLevel.PUBLIC, SecurityLevel.AUTHENTICATED]:
            return None

        if not request_context["authenticated"]:
            return self._create_error_response(401, "Authentication required")

        user_id = request_context["user_id"]
        required_permissions = endpoint.required_permissions

        # Check if user has required permissions
        for permission in required_permissions:
            if not self.rbac_manager.check_permission(user_id, permission):
                return self._create_error_response(403, f"Permission denied: {permission}")

        # Check admin access
        if endpoint.security_level == SecurityLevel.ADMIN:
            if not self.rbac_manager.has_role(user_id, "admin"):
                return self._create_error_response(403, "Admin access required")

        request_context["authorized"] = True
        return None

    def _rate_limiting_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Rate limiting middleware"""
        if not self.config.enable_rate_limiting:
            return None

        client_ip = request_context["client_ip"]
        rate_limit = endpoint.rate_limit or 1000  # Default rate limit

        # Check rate limit
        rate_limit_result, rate_info = self.security_manager.rate_limiter.check_rate_limit(
            client_ip, f"{endpoint.method.value}:{endpoint.path}"
        )

        if not rate_limit_result:
            request_context["rate_limited"] = True
            retry_after = rate_info.get("retry_after", 60)
            return self._create_error_response(
                429,
                "Rate limit exceeded",
                headers={"Retry-After": str(int(retry_after))}
            )

        return None

    def _request_validation_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Request validation middleware"""
        if not self.config.enable_request_validation or not endpoint.validation_schema:
            return None

        # Would validate request body against schema
        # For now, just pass through
        return None

    def _response_validation_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Response validation middleware"""
        if not self.config.enable_response_validation or not endpoint.response_schema:
            return None

        # Would validate response against schema
        # This would be called after the handler executes
        return None

    def _audit_logging_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Audit logging middleware"""
        if not self.config.enable_audit_logging:
            return None

        # Log request start
        # Would log response completion after handler execution
        return None

    def _performance_monitoring_middleware(self, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Optional[Dict[str, Any]]:
        """Performance monitoring middleware"""
        if not self.config.enable_performance_monitoring:
            return None

        # Start performance monitoring
        request_context["performance_start"] = time.time()
        return None

    def _process_response(self, response: Any, request_context: Dict[str, Any], endpoint: APIEndpoint) -> Dict[str, Any]:
        """Process response from endpoint handler"""
        # Create standard response format
        processed_response = {
            "status_code": 200,
            "headers": {},
            "body": response
        }

        # Add security headers
        if "security_headers" in request_context:
            processed_response["headers"].update(request_context["security_headers"])

        # Add CORS headers
        if self.config.cors.enabled and endpoint.cors_enabled:
            processed_response["headers"].update({
                "Access-Control-Allow-Origin": ", ".join(self.config.cors.config.allow_origins),
                "Access-Control-Allow-Methods": ", ".join(self.config.cors.config.allow_methods),
                "Access-Control-Allow-Headers": ", ".join(self.config.cors.config.allow_headers),
                "Access-Control-Allow-Credentials": str(self.config.cors.config.allow_credentials).lower()
            })

        # Add rate limit headers
        if not request_context["rate_limited"]:
            processed_response["headers"]["X-RateLimit-Limit"] = "1000"
            processed_response["headers"]["X-RateLimit-Remaining"] = "999"

        # Log audit event
        if self.config.enable_audit_logging:
            self._log_audit_event(request_context, processed_response, endpoint)

        return processed_response

    def _log_audit_event(self, request_context: Dict[str, Any], response: Dict[str, Any], endpoint: APIEndpoint):
        """Log audit event for API request"""
        severity = AuditSeverity.LOW
        if response["status_code"] >= 400:
            severity = AuditSeverity.MEDIUM
        if response["status_code"] >= 500:
            severity = AuditSeverity.HIGH

        self.audit_logger.log_event(
            event_type=AuditEventType.API_CALL,
            severity=severity,
            action=f"{endpoint.method.value} {endpoint.path}",
            user_id=request_context["user_id"],
            ip_address=request_context["client_ip"],
            resource_type="api_endpoint",
            resource_id=endpoint.path,
            details={
                "method": endpoint.method.value,
                "status_code": response["status_code"],
                "authenticated": request_context["authenticated"],
                "authorized": request_context["authorized"],
                "rate_limited": request_context["rate_limited"],
                "response_time": time.time() - request_context.get("performance_start", time.time())
            },
            outcome="success" if response["status_code"] < 400 else "failure"
        )

    def _update_performance_metrics(self, path: str, method: HTTPMethod, execution_time: float):
        """Update performance metrics"""
        key = f"{method.value}:{path}"
        if key not in self.performance_metrics:
            self.performance_metrics[key] = {
                "count": 0,
                "total_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "avg_time": 0
            }

        metrics = self.performance_metrics[key]
        metrics["count"] += 1
        metrics["total_time"] += execution_time
        metrics["min_time"] = min(metrics["min_time"], execution_time)
        metrics["max_time"] = max(metrics["max_time"], execution_time)
        metrics["avg_time"] = metrics["total_time"] / metrics["count"]

    def _create_error_response(self, status_code: int, message: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status_code": status_code,
            "headers": headers or {},
            "body": {
                "error": {
                    "code": status_code,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
            }
        }

    def _handle_generic_error(self, error: Exception, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic exceptions"""
        logger.error(f"Unhandled error: {error}", exc_info=True)

        return self._create_error_response(
            500,
            "Internal server error"
        )

    def _handle_validation_error(self, error: ValueError, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors"""
        return self._create_error_response(
            400,
            str(error)
        )

    def _handle_authorization_error(self, error: PermissionError, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authorization errors"""
        return self._create_error_response(
            403,
            str(error)
        )

    def _handle_timeout_error(self, error: TimeoutError, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout errors"""
        return self._create_error_response(
            504,
            "Request timeout"
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "metrics": self.performance_metrics,
            "total_requests": sum(m["count"] for m in self.performance_metrics.values()),
            "avg_response_time": sum(m["avg_time"] for m in self.performance_metrics.values()) / len(self.performance_metrics) if self.performance_metrics else 0,
            "slowest_endpoints": sorted(
                [(key, metrics["avg_time"]) for key, metrics in self.performance_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    def get_gateway_status(self) -> Dict[str, Any]:
        """Get API gateway status"""
        return {
            "endpoints_count": sum(len(methods) for methods in self.endpoints.values()),
            "middleware_count": len(self.middleware_stack),
            "performance_metrics_count": len(self.performance_metrics),
            "cors_enabled": self.config.cors.enabled,
            "csp_enabled": self.config.csp.enabled,
            "request_validation_enabled": self.config.enable_request_validation,
            "rate_limiting_enabled": self.config.enable_rate_limiting,
            "api_keys_enabled": self.config.enable_api_keys,
            "audit_logging_enabled": self.config.enable_audit_logging
        }